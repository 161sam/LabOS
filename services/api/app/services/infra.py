from collections import Counter
from datetime import timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import (
    Asset,
    AutonomousModule,
    BackupRecord,
    InfraNode,
    InfraService,
    StorageVolume,
    _utcnow,
)
from ..schemas import (
    BackupRecordCreate,
    BackupRecordRead,
    BackupStatus,
    InfraNodeAssetRef,
    InfraNodeCreate,
    InfraNodeDetailRead,
    InfraNodeModuleRef,
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


DEGRADED_SERVICE_STATUS = {
    InfraServiceStatus.degraded.value,
    InfraServiceStatus.warning.value,
    InfraServiceStatus.offline.value,
}
STORAGE_ISSUE_STATUS = {
    StorageVolumeStatus.attention.value,
    StorageVolumeStatus.warning.value,
    StorageVolumeStatus.offline.value,
}


def list_infra_nodes(
    session: Session,
    node_type: InfraNodeType | None = None,
    status_filter: InfraNodeStatus | None = None,
    role: InfraNodeRole | None = None,
    zone: str | None = None,
    has_gpu: bool | None = None,
) -> list[InfraNodeRead]:
    statement = select(InfraNode)
    if node_type is not None:
        statement = statement.where(InfraNode.node_type == node_type.value)
    if status_filter is not None:
        statement = statement.where(InfraNode.status == status_filter.value)
    if role is not None:
        statement = statement.where(InfraNode.role == role.value)
    if zone:
        statement = statement.where(InfraNode.zone.ilike(f'%{zone.strip()}%'))
    if has_gpu is not None:
        statement = statement.where(InfraNode.has_gpu == has_gpu)

    nodes = list(
        session.exec(statement.order_by(InfraNode.name.asc(), InfraNode.id.asc())).all()
    )
    return _serialize_nodes(session, nodes)


def get_node_or_404(session: Session, node_id: int) -> InfraNode:
    node = session.get(InfraNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Infra node not found')
    return node


def get_node_detail(session: Session, node_id: int) -> InfraNodeDetailRead:
    node = get_node_or_404(session, node_id)
    node_read = _serialize_nodes(session, [node])[0]
    services = _list_services(session, node.id)
    volumes = _list_volumes(session, node.id)
    backups = _list_recent_backups(session, node.id, limit=5)
    asset_ref = _asset_ref(session, node.asset_id)
    module_ref = _module_ref(session, node.autonomous_module_id)
    return InfraNodeDetailRead(
        **node_read.model_dump(),
        services=services,
        storage_volumes=volumes,
        recent_backups=backups,
        asset=asset_ref,
        autonomous_module=module_ref,
    )


def create_node(session: Session, payload: InfraNodeCreate) -> InfraNodeDetailRead:
    _ensure_unique_node_id(session, payload.node_id)
    _validate_refs(session, payload.asset_id, payload.autonomous_module_id)

    node = InfraNode(
        node_id=payload.node_id,
        name=payload.name,
        node_type=payload.node_type.value,
        status=payload.status.value,
        role=payload.role.value,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        zone=payload.zone,
        location=payload.location,
        os_family=payload.os_family,
        architecture=payload.architecture,
        has_gpu=payload.has_gpu,
        ros_enabled=payload.ros_enabled,
        mqtt_enabled=payload.mqtt_enabled,
        notes=payload.notes,
        asset_id=payload.asset_id,
        autonomous_module_id=payload.autonomous_module_id,
        wiki_ref=payload.wiki_ref,
    )
    session.add(node)
    session.commit()
    session.refresh(node)
    return get_node_detail(session, node.id)


def update_node(
    session: Session, node: InfraNode, payload: InfraNodeUpdate
) -> InfraNodeDetailRead:
    if payload.node_id != node.node_id:
        _ensure_unique_node_id(session, payload.node_id)
    _validate_refs(session, payload.asset_id, payload.autonomous_module_id)

    node.node_id = payload.node_id
    node.name = payload.name
    node.node_type = payload.node_type.value
    node.status = payload.status.value
    node.role = payload.role.value
    node.hostname = payload.hostname
    node.ip_address = payload.ip_address
    node.zone = payload.zone
    node.location = payload.location
    node.os_family = payload.os_family
    node.architecture = payload.architecture
    node.has_gpu = payload.has_gpu
    node.ros_enabled = payload.ros_enabled
    node.mqtt_enabled = payload.mqtt_enabled
    node.notes = payload.notes
    node.asset_id = payload.asset_id
    node.autonomous_module_id = payload.autonomous_module_id
    node.wiki_ref = payload.wiki_ref
    node.updated_at = _utcnow()
    session.add(node)
    session.commit()
    session.refresh(node)
    return get_node_detail(session, node.id)


def update_node_status(
    session: Session, node: InfraNode, payload: InfraNodeStatusUpdate
) -> InfraNodeDetailRead:
    node.status = payload.status.value
    node.updated_at = _utcnow()
    session.add(node)
    session.commit()
    session.refresh(node)
    return get_node_detail(session, node.id)


def list_all_services(
    session: Session,
    service_type: InfraServiceType | None = None,
    status_filter: InfraServiceStatus | None = None,
) -> list[InfraServiceRead]:
    statement = select(InfraService)
    if service_type is not None:
        statement = statement.where(InfraService.service_type == service_type.value)
    if status_filter is not None:
        statement = statement.where(InfraService.status == status_filter.value)
    rows = list(session.exec(statement.order_by(InfraService.service_name.asc())).all())
    return [_serialize_service(row) for row in rows]


def list_services_for_node(session: Session, node_id: int) -> list[InfraServiceRead]:
    get_node_or_404(session, node_id)
    return _list_services(session, node_id)


def get_service_or_404(session: Session, service_id: int) -> InfraService:
    service = session.get(InfraService, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Infra service not found')
    return service


def create_service(session: Session, payload: InfraServiceCreate) -> InfraServiceRead:
    get_node_or_404(session, payload.infra_node_id)
    _ensure_unique_service_name(session, payload.infra_node_id, payload.service_name)
    service = InfraService(
        infra_node_id=payload.infra_node_id,
        service_name=payload.service_name,
        service_type=payload.service_type.value,
        status=payload.status.value,
        endpoint=payload.endpoint,
        port=payload.port,
        healthcheck_url=payload.healthcheck_url,
        version=payload.version,
        notes=payload.notes,
    )
    session.add(service)
    session.commit()
    session.refresh(service)
    return _serialize_service(service)


def update_service(
    session: Session, service: InfraService, payload: InfraServiceUpdate
) -> InfraServiceRead:
    if payload.infra_node_id != service.infra_node_id:
        get_node_or_404(session, payload.infra_node_id)
    if (
        payload.infra_node_id != service.infra_node_id
        or payload.service_name != service.service_name
    ):
        _ensure_unique_service_name(
            session, payload.infra_node_id, payload.service_name, exclude_id=service.id
        )

    service.infra_node_id = payload.infra_node_id
    service.service_name = payload.service_name
    service.service_type = payload.service_type.value
    service.status = payload.status.value
    service.endpoint = payload.endpoint
    service.port = payload.port
    service.healthcheck_url = payload.healthcheck_url
    service.version = payload.version
    service.notes = payload.notes
    service.updated_at = _utcnow()
    session.add(service)
    session.commit()
    session.refresh(service)
    return _serialize_service(service)


def list_all_volumes(
    session: Session, status_filter: StorageVolumeStatus | None = None
) -> list[StorageVolumeRead]:
    statement = select(StorageVolume)
    if status_filter is not None:
        statement = statement.where(StorageVolume.status == status_filter.value)
    rows = list(session.exec(statement.order_by(StorageVolume.name.asc())).all())
    return [_serialize_volume(row) for row in rows]


def create_volume(session: Session, payload: StorageVolumeCreate) -> StorageVolumeRead:
    get_node_or_404(session, payload.infra_node_id)
    volume = StorageVolume(
        infra_node_id=payload.infra_node_id,
        name=payload.name,
        mount_path=payload.mount_path,
        volume_type=payload.volume_type,
        status=payload.status.value,
        capacity_gb=payload.capacity_gb,
        free_gb=payload.free_gb,
        notes=payload.notes,
    )
    session.add(volume)
    session.commit()
    session.refresh(volume)
    return _serialize_volume(volume)


def get_volume_or_404(session: Session, volume_id: int) -> StorageVolume:
    volume = session.get(StorageVolume, volume_id)
    if volume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Storage volume not found')
    return volume


def update_volume(
    session: Session, volume: StorageVolume, payload: StorageVolumeUpdate
) -> StorageVolumeRead:
    if payload.infra_node_id != volume.infra_node_id:
        get_node_or_404(session, payload.infra_node_id)
    volume.infra_node_id = payload.infra_node_id
    volume.name = payload.name
    volume.mount_path = payload.mount_path
    volume.volume_type = payload.volume_type
    volume.status = payload.status.value
    volume.capacity_gb = payload.capacity_gb
    volume.free_gb = payload.free_gb
    volume.notes = payload.notes
    volume.updated_at = _utcnow()
    session.add(volume)
    session.commit()
    session.refresh(volume)
    return _serialize_volume(volume)


def list_backup_records(
    session: Session,
    status_filter: BackupStatus | None = None,
    limit: int = 50,
) -> list[BackupRecordRead]:
    statement = select(BackupRecord)
    if status_filter is not None:
        statement = statement.where(BackupRecord.status == status_filter.value)
    rows = list(
        session.exec(
            statement.order_by(BackupRecord.created_at.desc(), BackupRecord.id.desc()).limit(limit)
        ).all()
    )
    return [_serialize_backup(row) for row in rows]


def create_backup_record(session: Session, payload: BackupRecordCreate) -> BackupRecordRead:
    if payload.infra_node_id is not None:
        get_node_or_404(session, payload.infra_node_id)
    record = BackupRecord(
        infra_node_id=payload.infra_node_id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        backup_type=payload.backup_type,
        status=payload.status.value,
        started_at=payload.started_at,
        finished_at=payload.finished_at,
        notes=payload.notes,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_backup(record)


def get_overview(session: Session) -> InfraOverviewRead:
    nodes = list(session.exec(select(InfraNode)).all())
    status_counter: Counter[str] = Counter(n.status for n in nodes)
    type_counter: Counter[str] = Counter(n.node_type for n in nodes)
    role_counter: Counter[str] = Counter(n.role for n in nodes)

    services = list(session.exec(select(InfraService)).all())
    degraded_services = sum(1 for s in services if s.status in DEGRADED_SERVICE_STATUS)

    volumes = list(session.exec(select(StorageVolume)).all())
    storage_issues = sum(1 for v in volumes if v.status in STORAGE_ISSUE_STATUS)

    cutoff = _utcnow() - timedelta(days=14)
    backup_failures = len(
        session.exec(
            select(BackupRecord.id).where(
                BackupRecord.status == BackupStatus.failed.value,
                BackupRecord.created_at >= cutoff,
            )
        ).all()
    )

    return InfraOverviewRead(
        total_nodes=len(nodes),
        nominal_nodes=status_counter.get(InfraNodeStatus.nominal.value, 0),
        attention_nodes=status_counter.get(InfraNodeStatus.attention.value, 0),
        warning_nodes=status_counter.get(InfraNodeStatus.warning.value, 0),
        incident_nodes=status_counter.get(InfraNodeStatus.incident.value, 0),
        offline_nodes=status_counter.get(InfraNodeStatus.offline.value, 0),
        maintenance_nodes=status_counter.get(InfraNodeStatus.maintenance.value, 0),
        disabled_nodes=status_counter.get(InfraNodeStatus.disabled.value, 0),
        degraded_services=degraded_services,
        total_services=len(services),
        storage_issues=storage_issues,
        recent_backup_failures=backup_failures,
        by_type=dict(type_counter),
        by_role=dict(role_counter),
    )


def count_offline_nodes(session: Session) -> int:
    rows = session.exec(
        select(InfraNode.id).where(
            InfraNode.status.in_([InfraNodeStatus.offline.value, InfraNodeStatus.incident.value])
        )
    ).all()
    return len(rows)


def count_degraded_services(session: Session) -> int:
    rows = session.exec(
        select(InfraService.id).where(InfraService.status.in_(list(DEGRADED_SERVICE_STATUS)))
    ).all()
    return len(rows)


def count_recent_backup_failures(session: Session, days: int = 14) -> int:
    cutoff = _utcnow() - timedelta(days=days)
    rows = session.exec(
        select(BackupRecord.id).where(
            BackupRecord.status == BackupStatus.failed.value,
            BackupRecord.created_at >= cutoff,
        )
    ).all()
    return len(rows)


def _serialize_nodes(session: Session, nodes: list[InfraNode]) -> list[InfraNodeRead]:
    if not nodes:
        return []
    node_ids = [n.id for n in nodes if n.id is not None]
    service_counts: dict[int, int] = {}
    storage_counts: dict[int, int] = {}
    if node_ids:
        for row in session.exec(
            select(InfraService.infra_node_id).where(InfraService.infra_node_id.in_(node_ids))
        ).all():
            service_counts[row] = service_counts.get(row, 0) + 1
        for row in session.exec(
            select(StorageVolume.infra_node_id).where(StorageVolume.infra_node_id.in_(node_ids))
        ).all():
            storage_counts[row] = storage_counts.get(row, 0) + 1

    return [
        InfraNodeRead(
            id=n.id,
            node_id=n.node_id,
            name=n.name,
            node_type=InfraNodeType(n.node_type),
            status=InfraNodeStatus(n.status),
            role=InfraNodeRole(n.role),
            hostname=n.hostname,
            ip_address=n.ip_address,
            zone=n.zone,
            location=n.location,
            os_family=n.os_family,
            architecture=n.architecture,
            has_gpu=n.has_gpu,
            ros_enabled=n.ros_enabled,
            mqtt_enabled=n.mqtt_enabled,
            notes=n.notes,
            asset_id=n.asset_id,
            autonomous_module_id=n.autonomous_module_id,
            wiki_ref=n.wiki_ref,
            created_at=n.created_at,
            updated_at=n.updated_at,
            service_count=service_counts.get(n.id or 0, 0),
            storage_count=storage_counts.get(n.id or 0, 0),
        )
        for n in nodes
    ]


def _list_services(session: Session, node_id: int) -> list[InfraServiceRead]:
    rows = list(
        session.exec(
            select(InfraService)
            .where(InfraService.infra_node_id == node_id)
            .order_by(InfraService.service_name.asc())
        ).all()
    )
    return [_serialize_service(row) for row in rows]


def _list_volumes(session: Session, node_id: int) -> list[StorageVolumeRead]:
    rows = list(
        session.exec(
            select(StorageVolume)
            .where(StorageVolume.infra_node_id == node_id)
            .order_by(StorageVolume.name.asc())
        ).all()
    )
    return [_serialize_volume(row) for row in rows]


def _list_recent_backups(session: Session, node_id: int, limit: int) -> list[BackupRecordRead]:
    rows = list(
        session.exec(
            select(BackupRecord)
            .where(BackupRecord.infra_node_id == node_id)
            .order_by(BackupRecord.created_at.desc(), BackupRecord.id.desc())
            .limit(limit)
        ).all()
    )
    return [_serialize_backup(row) for row in rows]


def _serialize_service(row: InfraService) -> InfraServiceRead:
    return InfraServiceRead(
        id=row.id,
        infra_node_id=row.infra_node_id,
        service_name=row.service_name,
        service_type=InfraServiceType(row.service_type),
        status=InfraServiceStatus(row.status),
        endpoint=row.endpoint,
        port=row.port,
        healthcheck_url=row.healthcheck_url,
        version=row.version,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _serialize_volume(row: StorageVolume) -> StorageVolumeRead:
    return StorageVolumeRead(
        id=row.id,
        infra_node_id=row.infra_node_id,
        name=row.name,
        mount_path=row.mount_path,
        volume_type=row.volume_type,
        status=StorageVolumeStatus(row.status),
        capacity_gb=row.capacity_gb,
        free_gb=row.free_gb,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _serialize_backup(row: BackupRecord) -> BackupRecordRead:
    return BackupRecordRead(
        id=row.id,
        infra_node_id=row.infra_node_id,
        target_type=row.target_type,
        target_id=row.target_id,
        backup_type=row.backup_type,
        status=BackupStatus(row.status),
        started_at=row.started_at,
        finished_at=row.finished_at,
        notes=row.notes,
        created_at=row.created_at,
    )


def _ensure_unique_node_id(session: Session, node_id: str) -> None:
    existing = session.exec(select(InfraNode.id).where(InfraNode.node_id == node_id)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Infra node with node_id={node_id} already exists',
        )


def _ensure_unique_service_name(
    session: Session, infra_node_id: int, service_name: str, exclude_id: int | None = None
) -> None:
    statement = select(InfraService.id).where(
        InfraService.infra_node_id == infra_node_id,
        InfraService.service_name == service_name,
    )
    if exclude_id is not None:
        statement = statement.where(InfraService.id != exclude_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Service {service_name!r} already registered on this node',
        )


def _validate_refs(
    session: Session, asset_id: int | None, autonomous_module_id: int | None
) -> None:
    if asset_id is not None and session.get(Asset, asset_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='asset_id not found')
    if (
        autonomous_module_id is not None
        and session.get(AutonomousModule, autonomous_module_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='autonomous_module_id not found'
        )


def _asset_ref(session: Session, asset_id: int | None) -> InfraNodeAssetRef | None:
    if asset_id is None:
        return None
    asset = session.get(Asset, asset_id)
    if asset is None:
        return None
    return InfraNodeAssetRef(
        id=asset.id, name=asset.name, asset_type=asset.asset_type, status=asset.status
    )


def _module_ref(session: Session, module_id: int | None) -> InfraNodeModuleRef | None:
    if module_id is None:
        return None
    module = session.get(AutonomousModule, module_id)
    if module is None:
        return None
    return InfraNodeModuleRef(
        id=module.id,
        module_id=module.module_id,
        name=module.name,
        module_type=module.module_type,
        status=module.status,
    )
