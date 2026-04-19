from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    CalibrationOverviewRead,
    CalibrationRecordCreate,
    CalibrationRecordRead,
    CalibrationRecordUpdate,
    CalibrationStatus,
    CalibrationTargetType,
)
from ..services import calibration as calibration_service

router = APIRouter(
    prefix='/calibration',
    tags=['calibration'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[CalibrationRecordRead])
def list_calibration_records(
    target_type: CalibrationTargetType | None = Query(default=None),
    target_id: int | None = Query(default=None, ge=1),
    cal_status: CalibrationStatus | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return calibration_service.list_calibration_records(
        session,
        target_type=target_type,
        target_id=target_id,
        cal_status=cal_status,
        limit=limit,
    )


@router.post('', response_model=CalibrationRecordRead, status_code=status.HTTP_201_CREATED)
def create_calibration_record(
    payload: CalibrationRecordCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return calibration_service.create_calibration_record(
        session, payload, performed_by_user_id=current_user.id
    )


@router.patch('/{record_id}', response_model=CalibrationRecordRead)
def update_calibration_record(
    record_id: int,
    payload: CalibrationRecordUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return calibration_service.update_calibration_record(
        session, record_id, payload, performed_by_user_id=current_user.id
    )


@router.get('/overview', response_model=CalibrationOverviewRead)
def get_calibration_overview(session: Session = Depends(get_session)):
    return calibration_service.get_calibration_overview(session)
