"""Rule engine — LOCAL AUTOMATION / FALLBACK LAYER.

Boundary Hardening V1: this module is *not* the decision layer. In the
target architecture (Smolit-AI-Assistant → ABrain → LabOS Adapter → LabOS),
ABrain decides whether a rule-worthy condition warrants a task or alert.

Rules remain in LabOS as a **local automation fallback** for environments
running without ABrain. Every execution is marked `execution_origin =
'labos_local'` in its `action_result` so downstream consumers can tell
a local-fallback side effect apart from an ABrain-driven one.

Do NOT extend this module with planning, prioritization, multi-step
orchestration, or cross-domain reasoning. Those belong to ABrain.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Alert, Reactor, Rule, RuleExecution, Sensor, Task, _utcnow
from ..schemas import (
    AlertCreate,
    AlertStatus,
    RuleActionType,
    RuleCreate,
    RuleEnabledUpdate,
    RuleEvaluationResponse,
    RuleExecutionRead,
    RuleExecutionStatus,
    RuleRead,
    RuleTriggerType,
    RuleUpdate,
    TaskCreate,
    TaskStatus,
)
from . import alerts as alert_service
from . import sensors as sensor_service
from . import tasks as task_service

_ALERT_DUPLICATE_WINDOW_HOURS = 12

EXECUTION_ORIGIN_LOCAL = 'labos_local'


@dataclass
class _EvaluationOutcome:
    matched: bool
    evaluation_summary: dict[str, Any]
    template_context: dict[str, Any]


def list_rules(session: Session) -> list[RuleRead]:
    statement = select(Rule).order_by(Rule.updated_at.desc(), Rule.id.desc())
    return [RuleRead.model_validate(rule) for rule in session.exec(statement).all()]


def get_rule_or_404(session: Session, rule_id: int) -> Rule:
    rule = session.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    return rule


def get_rule_read(session: Session, rule_id: int) -> RuleRead:
    return RuleRead.model_validate(get_rule_or_404(session, rule_id))


def create_rule(session: Session, payload: RuleCreate) -> RuleRead:
    rule = Rule(
        name=payload.name,
        description=payload.description,
        is_enabled=payload.is_enabled,
        trigger_type=payload.trigger_type.value,
        condition_type=payload.condition_type.value,
        condition_config=payload.condition_config,
        action_type=payload.action_type.value,
        action_config=payload.action_config,
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return RuleRead.model_validate(rule)


def update_rule(session: Session, rule: Rule, payload: RuleUpdate) -> RuleRead:
    rule.name = payload.name
    rule.description = payload.description
    rule.is_enabled = payload.is_enabled
    rule.trigger_type = payload.trigger_type.value
    rule.condition_type = payload.condition_type.value
    rule.condition_config = payload.condition_config
    rule.action_type = payload.action_type.value
    rule.action_config = payload.action_config
    rule.updated_at = _utcnow()
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return RuleRead.model_validate(rule)


def update_rule_enabled(session: Session, rule: Rule, payload: RuleEnabledUpdate) -> RuleRead:
    rule.is_enabled = payload.is_enabled
    rule.updated_at = _utcnow()
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return RuleRead.model_validate(rule)


def evaluate_rule(session: Session, rule: Rule, *, dry_run: bool) -> RuleEvaluationResponse:
    outcome = _evaluate_match(session, rule)
    rule.last_evaluated_at = _utcnow()
    rule.updated_at = _utcnow()
    session.add(rule)
    session.commit()
    session.refresh(rule)

    if not outcome.matched:
        execution = _create_execution(
            session,
            rule=rule,
            status_value=RuleExecutionStatus.not_matched.value,
            dry_run=dry_run,
            evaluation_summary=outcome.evaluation_summary,
            action_result={'executed': False},
        )
        return RuleEvaluationResponse(rule=RuleRead.model_validate(rule), execution=execution)

    if dry_run:
        action_result = {'executed': False, 'dry_run': True, 'action_type': rule.action_type}
        execution = _create_execution(
            session,
            rule=rule,
            status_value=RuleExecutionStatus.matched.value,
            dry_run=True,
            evaluation_summary=outcome.evaluation_summary,
            action_result=action_result,
        )
        return RuleEvaluationResponse(rule=RuleRead.model_validate(rule), execution=execution)

    try:
        action_result = _execute_action(session, rule, outcome.template_context)
        execution = _create_execution(
            session,
            rule=rule,
            status_value=RuleExecutionStatus.executed.value,
            dry_run=False,
            evaluation_summary=outcome.evaluation_summary,
            action_result=action_result,
        )
        return RuleEvaluationResponse(rule=RuleRead.model_validate(rule), execution=execution)
    except HTTPException as exc:
        execution = _create_execution(
            session,
            rule=rule,
            status_value=RuleExecutionStatus.failed.value,
            dry_run=False,
            evaluation_summary=outcome.evaluation_summary,
            action_result={'executed': False, 'error': exc.detail},
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={'message': exc.detail, 'execution': execution.model_dump(mode='json')},
        )
    except Exception as exc:
        execution = _create_execution(
            session,
            rule=rule,
            status_value=RuleExecutionStatus.failed.value,
            dry_run=False,
            evaluation_summary=outcome.evaluation_summary,
            action_result={'executed': False, 'error': str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={'message': str(exc), 'execution': execution.model_dump(mode='json')},
        )


def evaluate_all_rules(session: Session, *, dry_run: bool) -> list[RuleExecutionRead]:
    rules = session.exec(select(Rule).where(Rule.is_enabled.is_(True)).order_by(Rule.id.asc())).all()
    executions: list[RuleExecutionRead] = []
    for rule in rules:
        executions.append(evaluate_rule(session, rule, dry_run=dry_run).execution)
    return executions


def list_rule_executions(session: Session, rule_id: int | None = None, limit: int = 20) -> list[RuleExecutionRead]:
    statement = select(RuleExecution).order_by(RuleExecution.created_at.desc(), RuleExecution.id.desc()).limit(limit)
    if rule_id is not None:
        statement = statement.where(RuleExecution.rule_id == rule_id)
    executions = list(session.exec(statement).all())
    return _serialize_executions(session, executions)


def count_active_rules(session: Session) -> int:
    return len(session.exec(select(Rule.id).where(Rule.is_enabled.is_(True))).all())


def list_recent_executions(session: Session, limit: int = 4) -> list[RuleExecutionRead]:
    return list_rule_executions(session, limit=limit)


def _evaluate_match(session: Session, rule: Rule) -> _EvaluationOutcome:
    trigger_type = RuleTriggerType(rule.trigger_type)
    if trigger_type == RuleTriggerType.sensor_threshold:
        return _evaluate_sensor_threshold(session, rule)
    if trigger_type == RuleTriggerType.stale_sensor:
        return _evaluate_stale_sensor(session, rule)
    if trigger_type == RuleTriggerType.overdue_tasks:
        return _evaluate_overdue_tasks(session, rule)
    if trigger_type == RuleTriggerType.reactor_status:
        return _evaluate_reactor_status(session, rule)
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Unsupported rule trigger')


def _evaluate_sensor_threshold(session: Session, rule: Rule) -> _EvaluationOutcome:
    sensor_id = int(rule.condition_config['sensor_id'])
    threshold = float(rule.condition_config['threshold'])
    sensor = sensor_service.get_sensor_read(session, sensor_id)

    if sensor.last_value is None:
        return _EvaluationOutcome(
            matched=False,
            evaluation_summary={'reason': 'no_sensor_value', 'sensor_id': sensor_id},
            template_context={'sensor_id': sensor.id, 'sensor_name': sensor.name, 'reactor_name': sensor.reactor_name or ''},
        )

    if rule.condition_type == 'threshold_gt':
        matched = sensor.last_value > threshold
        comparator = '>'
    else:
        matched = sensor.last_value < threshold
        comparator = '<'

    return _EvaluationOutcome(
        matched=matched,
        evaluation_summary={
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'last_value': sensor.last_value,
            'threshold': threshold,
            'comparator': comparator,
            'matched': matched,
        },
        template_context={
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'reactor_id': sensor.reactor_id or '',
            'reactor_name': sensor.reactor_name or '',
            'value': sensor.last_value,
            'threshold': threshold,
            'unit': sensor.unit,
            'status': sensor.status,
        },
    )


def _evaluate_stale_sensor(session: Session, rule: Rule) -> _EvaluationOutcome:
    hours = float(rule.condition_config['hours'])
    target_sensor_id = int(rule.condition_config['sensor_id']) if 'sensor_id' in rule.condition_config else None
    now = _utcnow()
    sensors = sensor_service.list_sensors(session)
    if target_sensor_id is not None:
        sensors = [sensor for sensor in sensors if sensor.id == target_sensor_id]

    stale_sensors = []
    for sensor in sensors:
        if sensor.last_recorded_at is None:
            stale_sensors.append(sensor)
        elif (now - sensor.last_recorded_at).total_seconds() > hours * 3600:
            stale_sensors.append(sensor)

    first_sensor = stale_sensors[0] if stale_sensors else (sensors[0] if sensors else None)
    return _EvaluationOutcome(
        matched=bool(stale_sensors),
        evaluation_summary={
            'hours': hours,
            'checked_sensor_count': len(sensors),
            'stale_sensor_count': len(stale_sensors),
            'stale_sensor_ids': [sensor.id for sensor in stale_sensors],
        },
        template_context={
            'sensor_id': first_sensor.id if first_sensor else '',
            'sensor_name': first_sensor.name if first_sensor else 'unknown sensor',
            'reactor_id': first_sensor.reactor_id if first_sensor and first_sensor.reactor_id is not None else '',
            'reactor_name': first_sensor.reactor_name if first_sensor and first_sensor.reactor_name else '',
            'hours': hours,
            'count': len(stale_sensors),
        },
    )


def _evaluate_overdue_tasks(session: Session, rule: Rule) -> _EvaluationOutcome:
    threshold_count = int(rule.condition_config['count'])
    overdue_by_hours = float(rule.condition_config.get('overdue_by_hours', 0))
    now = _utcnow()
    tasks = [
        task
        for task in task_service.list_tasks(session)
        if task.status != TaskStatus.done and task.due_at is not None and task.due_at < now - timedelta(hours=overdue_by_hours)
    ]
    tasks.sort(key=lambda task: task.due_at or now)
    first_task = tasks[0] if tasks else None
    matched = len(tasks) > threshold_count
    return _EvaluationOutcome(
        matched=matched,
        evaluation_summary={
            'threshold_count': threshold_count,
            'overdue_task_count': len(tasks),
            'overdue_by_hours': overdue_by_hours,
            'matched': matched,
        },
        template_context={
            'count': len(tasks),
            'oldest_task_title': first_task.title if first_task else 'keine Aufgabe',
            'charge_id': first_task.charge_id if first_task and first_task.charge_id is not None else '',
            'charge_name': first_task.charge_name if first_task and first_task.charge_name else '',
            'reactor_id': first_task.reactor_id if first_task and first_task.reactor_id is not None else '',
            'reactor_name': first_task.reactor_name if first_task and first_task.reactor_name else '',
        },
    )


def _evaluate_reactor_status(session: Session, rule: Rule) -> _EvaluationOutcome:
    reactor_id = int(rule.condition_config['reactor_id'])
    expected_status = str(rule.condition_config['status'])
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Referenced reactor does not exist')

    matched = reactor.status == expected_status
    return _EvaluationOutcome(
        matched=matched,
        evaluation_summary={
            'reactor_id': reactor.id,
            'reactor_name': reactor.name,
            'reactor_status': reactor.status,
            'expected_status': expected_status,
            'matched': matched,
        },
        template_context={
            'reactor_id': reactor.id,
            'reactor_name': reactor.name,
            'status': reactor.status,
        },
    )


def _execute_action(session: Session, rule: Rule, template_context: dict[str, Any]) -> dict[str, Any]:
    action_type = RuleActionType(rule.action_type)
    if action_type == RuleActionType.create_alert:
        return _execute_create_alert(session, rule, template_context)
    if action_type == RuleActionType.create_task:
        return _execute_create_task(session, rule, template_context)
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Unsupported rule action')


def _execute_create_alert(session: Session, rule: Rule, template_context: dict[str, Any]) -> dict[str, Any]:
    title = _render_template(str(rule.action_config['title_template']), template_context)
    message = _render_template(str(rule.action_config['message_template']), template_context)
    severity = str(rule.action_config['severity'])
    source_type = str(rule.action_config.get('source_type', 'system'))
    source_id = _derive_source_id(rule.action_config.get('source_id'), source_type, template_context)

    recent_cutoff = _utcnow() - timedelta(hours=_ALERT_DUPLICATE_WINDOW_HOURS)
    duplicate = session.exec(
        select(Alert).where(
            Alert.title == title,
            Alert.message == message,
            Alert.status != AlertStatus.resolved.value,
            Alert.created_at >= recent_cutoff,
        )
    ).first()
    if duplicate is not None:
        return {'executed': False, 'duplicate_skipped': True, 'alert_id': duplicate.id}

    created = alert_service.create_alert(
        session,
        AlertCreate(
            title=title,
            message=message,
            severity=severity,
            source_type=source_type,
            source_id=source_id,
        ),
    )
    return {'executed': True, 'entity_type': 'alert', 'alert_id': created.id}


def _execute_create_task(session: Session, rule: Rule, template_context: dict[str, Any]) -> dict[str, Any]:
    title = _render_template(str(rule.action_config['title_template']), template_context)
    description_template = str(rule.action_config.get('description_template', ''))
    description = _render_template(description_template, template_context) if description_template else None
    priority = str(rule.action_config['priority'])
    due_in_hours = rule.action_config.get('due_in_hours')
    due_at = _utcnow() + timedelta(hours=float(due_in_hours)) if due_in_hours is not None else None
    charge_id = _derive_reference_id(rule.action_config.get('charge_id'), template_context, 'charge_id')
    reactor_id = _derive_reference_id(rule.action_config.get('reactor_id'), template_context, 'reactor_id')

    duplicate = session.exec(
        select(Task).where(
            Task.title == title,
            Task.status.in_(['open', 'doing', 'blocked']),
        )
    ).first()
    if duplicate is not None:
        return {'executed': False, 'duplicate_skipped': True, 'task_id': duplicate.id}

    created = task_service.create_task(
        session,
        TaskCreate(
            title=title,
            description=description,
            priority=priority,
            due_at=due_at,
            charge_id=charge_id,
            reactor_id=reactor_id,
        ),
    )
    return {'executed': True, 'entity_type': 'task', 'task_id': created.id}


def _create_execution(
    session: Session,
    *,
    rule: Rule,
    status_value: str,
    dry_run: bool,
    evaluation_summary: dict[str, Any],
    action_result: dict[str, Any],
) -> RuleExecutionRead:
    tagged_result = dict(action_result)
    tagged_result.setdefault('execution_origin', EXECUTION_ORIGIN_LOCAL)
    execution = RuleExecution(
        rule_id=rule.id,
        status=status_value,
        dry_run=dry_run,
        evaluation_summary=evaluation_summary,
        action_result=tagged_result,
    )
    session.add(execution)
    session.commit()
    session.refresh(execution)
    return _serialize_executions(session, [execution])[0]


def _serialize_executions(session: Session, executions: list[RuleExecution]) -> list[RuleExecutionRead]:
    if not executions:
        return []
    rule_ids = sorted({execution.rule_id for execution in executions})
    rules = {rule.id: rule.name for rule in session.exec(select(Rule).where(Rule.id.in_(rule_ids))).all()}
    return [
        RuleExecutionRead(
            id=execution.id,
            rule_id=execution.rule_id,
            rule_name=rules.get(execution.rule_id),
            status=execution.status,
            dry_run=execution.dry_run,
            evaluation_summary=execution.evaluation_summary,
            action_result=execution.action_result,
            created_at=execution.created_at,
        )
        for execution in executions
    ]


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ''


def _render_template(template: str, context: dict[str, Any]) -> str:
    normalized_context = {key: '' if value is None else value for key, value in context.items()}
    return template.format_map(_SafeDict(normalized_context)).strip()


def _derive_reference_id(raw_value: Any, context: dict[str, Any], fallback_key: str) -> int | None:
    if raw_value is None or raw_value == '':
        value = context.get(fallback_key)
    elif isinstance(raw_value, str) and raw_value.startswith('{') and raw_value.endswith('}'):
        value = context.get(raw_value[1:-1])
    else:
        value = raw_value
    if value in (None, '', 'None'):
        return None
    return int(value)


def _derive_source_id(raw_value: Any, source_type: str, context: dict[str, Any]) -> int | None:
    if raw_value is not None:
        return _derive_reference_id(raw_value, context, 'source_id')
    if source_type == 'sensor':
        return _derive_reference_id(None, context, 'sensor_id')
    if source_type == 'reactor':
        return _derive_reference_id(None, context, 'reactor_id')
    if source_type == 'charge':
        return _derive_reference_id(None, context, 'charge_id')
    return None
