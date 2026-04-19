from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import MaintenanceRecord, Reactor, DeviceNode, Asset, UserAccount, _utcnow
from ..schemas import (
    MaintenanceRecordCreate,
    MaintenanceRecordRead,
    MaintenanceRecordUpdate,
    MaintenanceOverviewRead,
    MaintenanceStatus,
    MaintenanceTargetType,
)


def list_maintenance_records(
    session: Session,
    *,
    target_type: MaintenanceTargetType | None = None,
    target_id: int | None = None,
    maint_status: MaintenanceStatus | None = None,
    limit: int = 100,
) -> list[MaintenanceRecordRead]:
    statement = select(MaintenanceRecord)
    if target_type is not None:
        statement = statement.where(MaintenanceRecord.target_type == target_type.value)
    if target_id is not None:
        statement = statement.where(MaintenanceRecord.target_id == target_id)
    if maint_status is not None:
        statement = statement.where(MaintenanceRecord.status == maint_status.value)
    statement = statement.order_by(MaintenanceRecord.created_at.desc(), MaintenanceRecord.id.desc()).limit(limit)
    records = list(session.exec(statement).all())
    return _serialize_records(session, records)


def create_maintenance_record(
    session: Session,
    payload: MaintenanceRecordCreate,
    *,
    performed_by_user_id: int | None = None,
) -> MaintenanceRecordRead:
    _validate_target(session, payload.target_type.value, payload.target_id)
    record = MaintenanceRecord(
        target_type=payload.target_type.value,
        target_id=payload.target_id,
        maintenance_type=payload.maintenance_type.value,
        status=payload.status.value,
        performed_at=payload.performed_at,
        due_at=payload.due_at,
        performed_by_user_id=performed_by_user_id,
        note=payload.note,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_records(session, [record])[0]


def update_maintenance_record(
    session: Session,
    record_id: int,
    payload: MaintenanceRecordUpdate,
    *,
    performed_by_user_id: int | None = None,
) -> MaintenanceRecordRead:
    record = get_maintenance_record_or_404(session, record_id)
    if payload.maintenance_type is not None:
        record.maintenance_type = payload.maintenance_type.value
    if payload.status is not None:
        record.status = payload.status.value
    if 'performed_at' in payload.model_fields_set:
        record.performed_at = payload.performed_at
    if 'due_at' in payload.model_fields_set:
        record.due_at = payload.due_at
    if 'note' in payload.model_fields_set:
        record.note = payload.note
    if performed_by_user_id is not None:
        record.performed_by_user_id = performed_by_user_id
    record.updated_at = _utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_records(session, [record])[0]


def get_maintenance_overview(session: Session) -> MaintenanceOverviewRead:
    records = list(session.exec(select(MaintenanceRecord)).all())
    counts: dict[str, int] = {s.value: 0 for s in MaintenanceStatus}
    for r in records:
        if r.status in counts:
            counts[r.status] += 1
    return MaintenanceOverviewRead(
        total=len(records),
        scheduled=counts['scheduled'],
        done=counts['done'],
        overdue=counts['overdue'],
        skipped=counts['skipped'],
    )


def count_overdue(session: Session) -> int:
    return len(
        session.exec(
            select(MaintenanceRecord.id).where(MaintenanceRecord.status == 'overdue')
        ).all()
    )


def get_maintenance_record_or_404(session: Session, record_id: int) -> MaintenanceRecord:
    record = session.get(MaintenanceRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Maintenance record not found')
    return record


def _validate_target(session: Session, target_type: str, target_id: int) -> None:
    if target_type == 'reactor':
        if session.get(Reactor, target_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    elif target_type == 'device_node':
        if session.get(DeviceNode, target_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device node not found')
    elif target_type == 'asset':
        if session.get(Asset, target_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Asset not found')


def _resolve_target_name(session: Session, target_type: str, target_id: int) -> str | None:
    if target_type == 'reactor':
        obj = session.get(Reactor, target_id)
        return obj.name if obj else None
    if target_type == 'device_node':
        obj = session.get(DeviceNode, target_id)
        return obj.name if obj else None
    if target_type == 'asset':
        obj = session.get(Asset, target_id)
        return obj.name if obj else None
    return None


def _serialize_records(session: Session, records: list[MaintenanceRecord]) -> list[MaintenanceRecordRead]:
    if not records:
        return []
    user_ids = sorted({r.performed_by_user_id for r in records if r.performed_by_user_id is not None})
    user_map = {
        u.id: u.username
        for u in session.exec(select(UserAccount).where(UserAccount.id.in_(user_ids))).all()
    } if user_ids else {}
    return [
        MaintenanceRecordRead(
            id=r.id,
            target_type=r.target_type,
            target_id=r.target_id,
            target_name=_resolve_target_name(session, r.target_type, r.target_id),
            maintenance_type=r.maintenance_type,
            status=r.status,
            performed_at=r.performed_at,
            due_at=r.due_at,
            performed_by_user_id=r.performed_by_user_id,
            performed_by_username=user_map.get(r.performed_by_user_id) if r.performed_by_user_id else None,
            note=r.note,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]
