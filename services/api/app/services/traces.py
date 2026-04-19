"""Trace / Audit Layer V1.

The Trace Layer keeps a lightweight record of every ABrain-side
interaction so LabOS can reconstruct the end-to-end flow:

    ABrain Query
      -> Adapter Response (recommended actions)
      -> Approval (optional HITL gate)
      -> Execution (static ACTION_MAP dispatch)
      -> Result

This module deliberately does NOT implement:
- any decision logic (stays in ABrain + the static adapter catalog)
- any analytics / aggregation engine
- any event-sourcing store

It only owns:
- `TraceContext` rows (trace_id + small context snapshot + status)
- helpers that other layers call to ensure / update a trace
- read helpers that join approvals + execution logs for UI display

The linkage to approvals / executions is done via `trace_id` columns
that already exist on `ApprovalRequest` and `ABrainExecutionLog`.
"""

from __future__ import annotations

from typing import Any, Iterable

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import ABrainExecutionLog, ApprovalRequest, TraceContext, _utcnow
from ..schemas import (
    ABrainAdapterContextRead,
    ABrainAdapterResponse,
    ABrainExecutionLogRead,
    ApprovalRequestRead,
    TraceContextDetailRead,
    TraceContextRead,
    TraceContextSource,
    TraceContextStatus,
    TraceTimelineEvent,
    TraceTimelineEventKind,
)
from . import approvals as approvals_service
from .abrain_execution import get_log_read


_ALLOWED_SOURCE_STRINGS = {item.value for item in TraceContextSource}


def ensure_trace(
    session: Session,
    *,
    trace_id: str | None,
    source: str | None = None,
    root_query: str | None = None,
    summary: str | None = None,
    context_snapshot: dict[str, Any] | None = None,
) -> TraceContext | None:
    """Create a new `TraceContext` if this trace_id is unseen, else touch it.

    Callers pass whatever trace_id is on their payload (may be None — in
    which case the adapter's call path is still fully functional, we just
    don't record a trace). The record is intentionally small: we do NOT
    re-serialize the full lab context here.
    """

    if not trace_id:
        return None
    coerced_source = _coerce_source(source)

    existing = session.get(TraceContext, trace_id)
    if existing is None:
        record = TraceContext(
            trace_id=trace_id,
            source=coerced_source,
            status=TraceContextStatus.open.value,
            root_query=_shorten(root_query, 2000),
            summary=_shorten(summary, 2000),
            context_snapshot=context_snapshot or {},
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    changed = False
    if root_query and not existing.root_query:
        existing.root_query = _shorten(root_query, 2000)
        changed = True
    if summary and not existing.summary:
        existing.summary = _shorten(summary, 2000)
        changed = True
    if context_snapshot and not existing.context_snapshot:
        existing.context_snapshot = context_snapshot
        changed = True
    if existing.source == TraceContextSource.local.value and coerced_source != TraceContextSource.local.value:
        existing.source = coerced_source
        changed = True
    if changed:
        existing.updated_at = _utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
    return existing


def mark_status(
    session: Session,
    trace_id: str | None,
    target_status: TraceContextStatus,
) -> TraceContext | None:
    if not trace_id:
        return None
    record = session.get(TraceContext, trace_id)
    if record is None:
        return None
    # Never downgrade from a terminal state back to open — once a trace is
    # recorded as completed/failed it stays that way. `failed` wins over
    # `completed` if anything later blows up.
    current = TraceContextStatus(record.status) if record.status in {s.value for s in TraceContextStatus} else TraceContextStatus.open
    if current == TraceContextStatus.failed:
        return record
    if current == TraceContextStatus.completed and target_status != TraceContextStatus.failed:
        return record
    record.status = target_status.value
    record.updated_at = _utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def build_snapshot_from_adapter(
    context: ABrainAdapterContextRead,
    response: ABrainAdapterResponse,
) -> dict[str, Any]:
    """Small, deterministic snapshot — NOT a full context dump."""

    summary = context.summary
    ops = context.operations
    reactors = [
        {
            'id': reactor.id,
            'name': reactor.name,
            'status': reactor.status,
            'health_status': reactor.health_status,
        }
        for reactor in context.reactors[:5]
    ]
    return {
        'generated_at': context.generated_at.isoformat() if context.generated_at else None,
        'mode': response.mode,
        'open_tasks': summary.open_tasks,
        'overdue_tasks': summary.overdue_tasks,
        'critical_alerts': summary.critical_alerts,
        'open_alerts': summary.open_alerts,
        'open_safety_incidents': ops.open_safety_incident_count,
        'blocked_commands': ops.blocked_command_count,
        'failed_commands': ops.failed_command_count,
        'reactors': reactors,
        'policy_decision': response.policy_decision,
        'approval_required': response.approval_required,
    }


def list_traces(
    session: Session,
    *,
    status_filter: TraceContextStatus | None = None,
    source_filter: TraceContextSource | None = None,
    limit: int = 100,
) -> list[TraceContextRead]:
    statement = select(TraceContext)
    if status_filter is not None:
        statement = statement.where(TraceContext.status == status_filter.value)
    if source_filter is not None:
        statement = statement.where(TraceContext.source == source_filter.value)
    statement = statement.order_by(TraceContext.created_at.desc(), TraceContext.trace_id.desc()).limit(max(1, min(limit, 500)))
    traces = list(session.exec(statement).all())
    if not traces:
        return []
    trace_ids = [trace.trace_id for trace in traces]
    exec_counts, appr_counts, appr_pending = _aggregate_counts(session, trace_ids)
    return [_as_read(trace, exec_counts, appr_counts, appr_pending) for trace in traces]


def get_trace_detail(session: Session, trace_id: str) -> TraceContextDetailRead:
    record = session.get(TraceContext, trace_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Trace not found')

    executions_raw = list(
        session.exec(
            select(ABrainExecutionLog)
            .where(ABrainExecutionLog.trace_id == trace_id)
            .order_by(ABrainExecutionLog.created_at.asc(), ABrainExecutionLog.id.asc())
        ).all()
    )
    approvals_raw = list(
        session.exec(
            select(ApprovalRequest)
            .where(ApprovalRequest.trace_id == trace_id)
            .order_by(ApprovalRequest.created_at.asc(), ApprovalRequest.id.asc())
        ).all()
    )
    executions = [get_log_read(log) for log in executions_raw]
    approvals = [approvals_service._serialize(session, appr) for appr in approvals_raw]
    timeline = _build_timeline(record, executions, approvals)

    exec_counts = {trace_id: len(executions)}
    appr_counts = {trace_id: len(approvals)}
    appr_pending = {trace_id: sum(1 for appr in approvals if appr.status.value == 'pending')}
    base = _as_read(record, exec_counts, appr_counts, appr_pending)

    return TraceContextDetailRead(
        **base.model_dump(),
        timeline=timeline,
        executions=executions,
        approvals=approvals,
    )


def _build_timeline(
    record: TraceContext,
    executions: Iterable[ABrainExecutionLogRead],
    approvals: Iterable[ApprovalRequestRead],
) -> list[TraceTimelineEvent]:
    events: list[TraceTimelineEvent] = []
    if record.root_query or record.summary:
        events.append(
            TraceTimelineEvent(
                kind=TraceTimelineEventKind.query,
                created_at=record.created_at,
                label=record.root_query or 'ABrain query',
                status=record.status,
                details={'summary': record.summary} if record.summary else {},
            )
        )
    for appr in approvals:
        events.append(
            TraceTimelineEvent(
                kind=TraceTimelineEventKind.approval,
                created_at=appr.created_at,
                label=f'Approval · {appr.action_name}',
                status=appr.status.value,
                details={
                    'id': appr.id,
                    'risk_level': appr.risk_level.value if appr.risk_level else None,
                    'decided_at': appr.decided_at.isoformat() if appr.decided_at else None,
                    'blocked_reason': appr.blocked_reason,
                    'last_error': appr.last_error,
                },
            )
        )
    for log in executions:
        events.append(
            TraceTimelineEvent(
                kind=TraceTimelineEventKind.execution,
                created_at=log.created_at,
                label=f'Execute · {log.action}',
                status=log.status.value,
                details={
                    'id': log.id,
                    'blocked_reason': log.blocked_reason,
                    'executed_by': log.executed_by,
                },
            )
        )
    events.sort(key=lambda ev: (ev.created_at, ev.kind.value))
    return events


def _aggregate_counts(
    session: Session,
    trace_ids: list[str],
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    exec_rows = list(
        session.exec(
            select(ABrainExecutionLog).where(ABrainExecutionLog.trace_id.in_(trace_ids))
        ).all()
    )
    appr_rows = list(
        session.exec(
            select(ApprovalRequest).where(ApprovalRequest.trace_id.in_(trace_ids))
        ).all()
    )
    exec_counts: dict[str, int] = {tid: 0 for tid in trace_ids}
    appr_counts: dict[str, int] = {tid: 0 for tid in trace_ids}
    appr_pending: dict[str, int] = {tid: 0 for tid in trace_ids}
    for log in exec_rows:
        if log.trace_id:
            exec_counts[log.trace_id] = exec_counts.get(log.trace_id, 0) + 1
    for appr in appr_rows:
        if appr.trace_id:
            appr_counts[appr.trace_id] = appr_counts.get(appr.trace_id, 0) + 1
            if appr.status == 'pending':
                appr_pending[appr.trace_id] = appr_pending.get(appr.trace_id, 0) + 1
    return exec_counts, appr_counts, appr_pending


def _as_read(
    record: TraceContext,
    exec_counts: dict[str, int],
    appr_counts: dict[str, int],
    appr_pending: dict[str, int],
) -> TraceContextRead:
    return TraceContextRead(
        trace_id=record.trace_id,
        source=_as_source_enum(record.source),
        status=_as_status_enum(record.status),
        root_query=record.root_query,
        summary=record.summary,
        context_snapshot=record.context_snapshot or {},
        created_at=record.created_at,
        updated_at=record.updated_at,
        execution_count=exec_counts.get(record.trace_id, 0),
        approval_count=appr_counts.get(record.trace_id, 0),
        pending_approval_count=appr_pending.get(record.trace_id, 0),
    )


def _coerce_source(raw: str | None) -> str:
    if not raw:
        return TraceContextSource.local.value
    lowered = raw.lower()
    if lowered in _ALLOWED_SOURCE_STRINGS:
        return lowered
    if lowered.startswith('approval:') or lowered.startswith('operator'):
        return TraceContextSource.operator.value
    if 'abrain' in lowered:
        return TraceContextSource.abrain.value
    return TraceContextSource.local.value


def _as_source_enum(raw: str) -> TraceContextSource:
    try:
        return TraceContextSource(raw)
    except ValueError:
        return TraceContextSource.local


def _as_status_enum(raw: str) -> TraceContextStatus:
    try:
        return TraceContextStatus(raw)
    except ValueError:
        return TraceContextStatus.open


def _shorten(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) <= max_len:
        return value
    return value[: max_len - 1] + '…'


__all__ = [
    'build_snapshot_from_adapter',
    'ensure_trace',
    'get_trace_detail',
    'list_traces',
    'mark_status',
]
