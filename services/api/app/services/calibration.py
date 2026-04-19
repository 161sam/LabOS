from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import CalibrationRecord, Reactor, DeviceNode, Asset, UserAccount, _utcnow
from ..schemas import (
    CalibrationRecordCreate,
    CalibrationRecordRead,
    CalibrationRecordUpdate,
    CalibrationOverviewRead,
    CalibrationStatus,
    CalibrationTargetType,
)


def list_calibration_records(
    session: Session,
    *,
    target_type: CalibrationTargetType | None = None,
    target_id: int | None = None,
    cal_status: CalibrationStatus | None = None,
    limit: int = 100,
) -> list[CalibrationRecordRead]:
    statement = select(CalibrationRecord)
    if target_type is not None:
        statement = statement.where(CalibrationRecord.target_type == target_type.value)
    if target_id is not None:
        statement = statement.where(CalibrationRecord.target_id == target_id)
    if cal_status is not None:
        statement = statement.where(CalibrationRecord.status == cal_status.value)
    statement = statement.order_by(CalibrationRecord.created_at.desc(), CalibrationRecord.id.desc()).limit(limit)
    records = list(session.exec(statement).all())
    return _serialize_records(session, records)


def create_calibration_record(
    session: Session,
    payload: CalibrationRecordCreate,
    *,
    performed_by_user_id: int | None = None,
) -> CalibrationRecordRead:
    _validate_target(session, payload.target_type.value, payload.target_id)
    record = CalibrationRecord(
        target_type=payload.target_type.value,
        target_id=payload.target_id,
        parameter=payload.parameter,
        status=payload.status.value,
        calibrated_at=payload.calibrated_at,
        due_at=payload.due_at,
        calibration_value=payload.calibration_value,
        reference_value=payload.reference_value,
        performed_by_user_id=performed_by_user_id,
        note=payload.note,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_records(session, [record])[0]


def update_calibration_record(
    session: Session,
    record_id: int,
    payload: CalibrationRecordUpdate,
    *,
    performed_by_user_id: int | None = None,
) -> CalibrationRecordRead:
    record = get_calibration_record_or_404(session, record_id)
    if payload.status is not None:
        record.status = payload.status.value
    if 'calibrated_at' in payload.model_fields_set:
        record.calibrated_at = payload.calibrated_at
    if 'due_at' in payload.model_fields_set:
        record.due_at = payload.due_at
    if 'calibration_value' in payload.model_fields_set:
        record.calibration_value = payload.calibration_value
    if 'reference_value' in payload.model_fields_set:
        record.reference_value = payload.reference_value
    if 'note' in payload.model_fields_set:
        record.note = payload.note
    if performed_by_user_id is not None:
        record.performed_by_user_id = performed_by_user_id
    record.updated_at = _utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_records(session, [record])[0]


def get_calibration_overview(session: Session) -> CalibrationOverviewRead:
    records = list(session.exec(select(CalibrationRecord)).all())
    counts: dict[str, int] = {s.value: 0 for s in CalibrationStatus}
    for r in records:
        if r.status in counts:
            counts[r.status] += 1
    return CalibrationOverviewRead(
        total=len(records),
        valid=counts['valid'],
        due=counts['due'],
        expired=counts['expired'],
        failed=counts['failed'],
        unknown=counts['unknown'],
        due_or_expired=counts['due'] + counts['expired'],
    )


def count_due_or_expired(session: Session) -> int:
    return len(
        session.exec(
            select(CalibrationRecord.id).where(
                CalibrationRecord.status.in_(['due', 'expired'])
            )
        ).all()
    )


def has_expired_calibration_for_target(
    session: Session,
    target_type: str,
    target_id: int,
    parameter: str | None = None,
) -> bool:
    statement = select(CalibrationRecord.id).where(
        CalibrationRecord.target_type == target_type,
        CalibrationRecord.target_id == target_id,
        CalibrationRecord.status.in_(['expired', 'failed']),
    )
    if parameter is not None:
        statement = statement.where(CalibrationRecord.parameter == parameter)
    return session.exec(statement).first() is not None


def get_calibration_record_or_404(session: Session, record_id: int) -> CalibrationRecord:
    record = session.get(CalibrationRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Calibration record not found')
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


def _serialize_records(session: Session, records: list[CalibrationRecord]) -> list[CalibrationRecordRead]:
    if not records:
        return []
    user_ids = sorted({r.performed_by_user_id for r in records if r.performed_by_user_id is not None})
    user_map = {
        u.id: u.username
        for u in session.exec(select(UserAccount).where(UserAccount.id.in_(user_ids))).all()
    } if user_ids else {}
    return [
        CalibrationRecordRead(
            id=r.id,
            target_type=r.target_type,
            target_id=r.target_id,
            target_name=_resolve_target_name(session, r.target_type, r.target_id),
            parameter=r.parameter,
            status=r.status,
            calibrated_at=r.calibrated_at,
            due_at=r.due_at,
            calibration_value=r.calibration_value,
            reference_value=r.reference_value,
            performed_by_user_id=r.performed_by_user_id,
            performed_by_username=user_map.get(r.performed_by_user_id) if r.performed_by_user_id else None,
            note=r.note,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]
