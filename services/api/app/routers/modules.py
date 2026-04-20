from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    AutonomousModuleCreate,
    AutonomousModuleDetailRead,
    AutonomousModuleOverviewRead,
    AutonomousModuleRead,
    AutonomousModuleStatusUpdate,
    AutonomousModuleUpdate,
    ModuleAutonomyLevel,
    ModuleCapabilityPayload,
    ModuleCapabilityRead,
    ModuleStatus,
    ModuleType,
)
from ..services import modules as module_service

router = APIRouter(
    prefix='/modules', tags=['modules'], dependencies=[Depends(require_authenticated_user)]
)


@router.get('', response_model=list[AutonomousModuleRead])
def list_modules(
    module_type: ModuleType | None = Query(default=None),
    status_filter: ModuleStatus | None = Query(default=None, alias='status'),
    autonomy_level: ModuleAutonomyLevel | None = Query(default=None),
    reactor_id: int | None = Query(default=None),
    asset_id: int | None = Query(default=None),
    device_node_id: int | None = Query(default=None),
    zone: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return module_service.list_modules(
        session,
        module_type=module_type,
        status_filter=status_filter,
        autonomy_level=autonomy_level,
        reactor_id=reactor_id,
        asset_id=asset_id,
        device_node_id=device_node_id,
        zone=zone,
    )


@router.get('/overview', response_model=AutonomousModuleOverviewRead)
def get_module_overview(session: Session = Depends(get_session)):
    return module_service.get_module_overview(session)


@router.get('/{module_id}', response_model=AutonomousModuleDetailRead)
def get_module(module_id: int, session: Session = Depends(get_session)):
    return module_service.get_module_detail_read(session, module_id)


@router.post('', response_model=AutonomousModuleDetailRead, status_code=status.HTTP_201_CREATED)
def create_module(
    payload: AutonomousModuleCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return module_service.create_module(session, payload)


@router.put('/{module_id}', response_model=AutonomousModuleDetailRead)
def update_module(
    module_id: int,
    payload: AutonomousModuleUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    module = module_service.get_module_or_404(session, module_id)
    return module_service.update_module(session, module, payload)


@router.patch('/{module_id}/status', response_model=AutonomousModuleDetailRead)
def update_module_status(
    module_id: int,
    payload: AutonomousModuleStatusUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    module = module_service.get_module_or_404(session, module_id)
    return module_service.update_module_status(session, module, payload)


@router.put('/{module_id}/capabilities', response_model=list[ModuleCapabilityRead])
def replace_capabilities(
    module_id: int,
    payload: list[ModuleCapabilityPayload],
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    module = module_service.get_module_or_404(session, module_id)
    return module_service.replace_capabilities(session, module, payload)
