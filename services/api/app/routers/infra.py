from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    BackupRecordCreate,
    BackupRecordRead,
    BackupStatus,
    InfraNodeCreate,
    InfraNodeDetailRead,
    InfraNodeRead,
    InfraNodeRole,
    InfraNodeStatus,
    InfraNodeStatusUpdate,
    InfraNodeType,
    InfraNodeUpdate,
    InfraOverviewRead,
    InfraServiceCreate,
    InfraServiceRead,
    InfraServiceStatus,
    InfraServiceType,
    InfraServiceUpdate,
    StorageVolumeCreate,
    StorageVolumeRead,
    StorageVolumeStatus,
    StorageVolumeUpdate,
)
from ..services import infra as infra_service

router = APIRouter(
    prefix='/infra',
    tags=['infra'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('/nodes', response_model=list[InfraNodeRead])
def list_nodes(
    node_type: InfraNodeType | None = Query(default=None),
    status_filter: InfraNodeStatus | None = Query(default=None, alias='status'),
    role: InfraNodeRole | None = Query(default=None),
    zone: str | None = Query(default=None),
    has_gpu: bool | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return infra_service.list_infra_nodes(
        session,
        node_type=node_type,
        status_filter=status_filter,
        role=role,
        zone=zone,
        has_gpu=has_gpu,
    )


@router.get('/overview', response_model=InfraOverviewRead)
def overview(session: Session = Depends(get_session)):
    return infra_service.get_overview(session)


@router.get('/nodes/{node_id}', response_model=InfraNodeDetailRead)
def get_node(node_id: int, session: Session = Depends(get_session)):
    return infra_service.get_node_detail(session, node_id)


@router.post('/nodes', response_model=InfraNodeDetailRead, status_code=status.HTTP_201_CREATED)
def create_node(
    payload: InfraNodeCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return infra_service.create_node(session, payload)


@router.put('/nodes/{node_id}', response_model=InfraNodeDetailRead)
def update_node(
    node_id: int,
    payload: InfraNodeUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    node = infra_service.get_node_or_404(session, node_id)
    return infra_service.update_node(session, node, payload)


@router.patch('/nodes/{node_id}/status', response_model=InfraNodeDetailRead)
def update_node_status(
    node_id: int,
    payload: InfraNodeStatusUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    node = infra_service.get_node_or_404(session, node_id)
    return infra_service.update_node_status(session, node, payload)


@router.get('/services', response_model=list[InfraServiceRead])
def list_services(
    service_type: InfraServiceType | None = Query(default=None),
    status_filter: InfraServiceStatus | None = Query(default=None, alias='status'),
    session: Session = Depends(get_session),
):
    return infra_service.list_all_services(
        session, service_type=service_type, status_filter=status_filter
    )


@router.get('/nodes/{node_id}/services', response_model=list[InfraServiceRead])
def list_services_for_node(node_id: int, session: Session = Depends(get_session)):
    return infra_service.list_services_for_node(session, node_id)


@router.post('/services', response_model=InfraServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: InfraServiceCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return infra_service.create_service(session, payload)


@router.put('/services/{service_id}', response_model=InfraServiceRead)
def update_service(
    service_id: int,
    payload: InfraServiceUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    service = infra_service.get_service_or_404(session, service_id)
    return infra_service.update_service(session, service, payload)


@router.get('/storage', response_model=list[StorageVolumeRead])
def list_volumes(
    status_filter: StorageVolumeStatus | None = Query(default=None, alias='status'),
    session: Session = Depends(get_session),
):
    return infra_service.list_all_volumes(session, status_filter=status_filter)


@router.post('/storage', response_model=StorageVolumeRead, status_code=status.HTTP_201_CREATED)
def create_volume(
    payload: StorageVolumeCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return infra_service.create_volume(session, payload)


@router.put('/storage/{volume_id}', response_model=StorageVolumeRead)
def update_volume(
    volume_id: int,
    payload: StorageVolumeUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    volume = infra_service.get_volume_or_404(session, volume_id)
    return infra_service.update_volume(session, volume, payload)


@router.get('/backups', response_model=list[BackupRecordRead])
def list_backups(
    status_filter: BackupStatus | None = Query(default=None, alias='status'),
    limit: int = Query(default=50, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return infra_service.list_backup_records(session, status_filter=status_filter, limit=limit)


@router.post('/backups', response_model=BackupRecordRead, status_code=status.HTTP_201_CREATED)
def create_backup(
    payload: BackupRecordCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return infra_service.create_backup_record(session, payload)
