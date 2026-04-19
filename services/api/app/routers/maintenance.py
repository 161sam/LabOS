from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    MaintenanceOverviewRead,
    MaintenanceRecordCreate,
    MaintenanceRecordRead,
    MaintenanceRecordUpdate,
    MaintenanceStatus,
    MaintenanceTargetType,
)
from ..services import maintenance as maintenance_service

router = APIRouter(
    prefix='/maintenance',
    tags=['maintenance'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[MaintenanceRecordRead])
def list_maintenance_records(
    target_type: MaintenanceTargetType | None = Query(default=None),
    target_id: int | None = Query(default=None, ge=1),
    maint_status: MaintenanceStatus | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return maintenance_service.list_maintenance_records(
        session,
        target_type=target_type,
        target_id=target_id,
        maint_status=maint_status,
        limit=limit,
    )


@router.post('', response_model=MaintenanceRecordRead, status_code=status.HTTP_201_CREATED)
def create_maintenance_record(
    payload: MaintenanceRecordCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return maintenance_service.create_maintenance_record(
        session, payload, performed_by_user_id=current_user.id
    )


@router.patch('/{record_id}', response_model=MaintenanceRecordRead)
def update_maintenance_record(
    record_id: int,
    payload: MaintenanceRecordUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return maintenance_service.update_maintenance_record(
        session, record_id, payload, performed_by_user_id=current_user.id
    )


@router.get('/overview', response_model=MaintenanceOverviewRead)
def get_maintenance_overview(session: Session = Depends(get_session)):
    return maintenance_service.get_maintenance_overview(session)
