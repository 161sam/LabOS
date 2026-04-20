from collections import Counter

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import (
    Asset,
    AutonomousModule,
    DeviceNode,
    ModuleCapability,
    Reactor,
    SafetyIncident,
    _utcnow,
)
from ..schemas import (
    AutonomousModuleAssetRef,
    AutonomousModuleCreate,
    AutonomousModuleDetailRead,
    AutonomousModuleDeviceNodeRef,
    AutonomousModuleOverviewRead,
    AutonomousModuleRead,
    AutonomousModuleReactorRef,
    AutonomousModuleStatusUpdate,
    AutonomousModuleUpdate,
    ModuleAutonomyLevel,
    ModuleCapabilityPayload,
    ModuleCapabilityRead,
    ModuleCapabilityType,
    ModuleStatus,
    ModuleType,
)


def list_modules(
    session: Session,
    module_type: ModuleType | None = None,
    status_filter: ModuleStatus | None = None,
    autonomy_level: ModuleAutonomyLevel | None = None,
    reactor_id: int | None = None,
    asset_id: int | None = None,
    device_node_id: int | None = None,
    zone: str | None = None,
) -> list[AutonomousModuleRead]:
    statement = select(AutonomousModule)
    if module_type is not None:
        statement = statement.where(AutonomousModule.module_type == module_type.value)
    if status_filter is not None:
        statement = statement.where(AutonomousModule.status == status_filter.value)
    if autonomy_level is not None:
        statement = statement.where(AutonomousModule.autonomy_level == autonomy_level.value)
    if reactor_id is not None:
        statement = statement.where(AutonomousModule.reactor_id == reactor_id)
    if asset_id is not None:
        statement = statement.where(AutonomousModule.asset_id == asset_id)
    if device_node_id is not None:
        statement = statement.where(AutonomousModule.device_node_id == device_node_id)
    if zone:
        statement = statement.where(AutonomousModule.zone.ilike(f'%{zone.strip()}%'))

    modules = list(
        session.exec(
            statement.order_by(AutonomousModule.name.asc(), AutonomousModule.id.asc())
        ).all()
    )
    return _serialize_modules(session, modules)


def get_module_or_404(session: Session, module_id: int) -> AutonomousModule:
    module = session.get(AutonomousModule, module_id)
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Autonomous module not found')
    return module


def get_module_read(session: Session, module_id: int) -> AutonomousModuleRead:
    module = get_module_or_404(session, module_id)
    return _serialize_modules(session, [module])[0]


def get_module_detail_read(session: Session, module_id: int) -> AutonomousModuleDetailRead:
    module = get_module_or_404(session, module_id)
    module_read = _serialize_modules(session, [module])[0]
    capabilities = _load_capabilities(session, module.id)
    reactor_ref = _reactor_ref(session, module.reactor_id)
    asset_ref = _asset_ref(session, module.asset_id)
    device_node_ref = _device_node_ref(session, module.device_node_id)
    open_incident_count = _open_incident_count(session, module)
    return AutonomousModuleDetailRead(
        **module_read.model_dump(),
        capabilities=capabilities,
        reactor=reactor_ref,
        asset=asset_ref,
        device_node=device_node_ref,
        open_incident_count=open_incident_count,
    )


def create_module(session: Session, payload: AutonomousModuleCreate) -> AutonomousModuleDetailRead:
    _validate_refs(session, payload.reactor_id, payload.asset_id, payload.device_node_id)
    _ensure_unique_module_id(session, payload.module_id)

    module = AutonomousModule(
        module_id=payload.module_id,
        name=payload.name,
        module_type=payload.module_type.value,
        status=payload.status.value,
        autonomy_level=payload.autonomy_level.value,
        reactor_id=payload.reactor_id,
        asset_id=payload.asset_id,
        device_node_id=payload.device_node_id,
        zone=payload.zone,
        location=payload.location,
        description=payload.description,
        ros_node_name=payload.ros_node_name,
        mqtt_node_id=payload.mqtt_node_id,
        wiki_ref=payload.wiki_ref,
    )
    session.add(module)
    session.flush()

    _replace_capabilities(session, module.id, payload.capabilities)
    session.commit()
    session.refresh(module)
    return get_module_detail_read(session, module.id)


def update_module(
    session: Session, module: AutonomousModule, payload: AutonomousModuleUpdate
) -> AutonomousModuleDetailRead:
    _validate_refs(session, payload.reactor_id, payload.asset_id, payload.device_node_id)
    if payload.module_id != module.module_id:
        _ensure_unique_module_id(session, payload.module_id)

    module.module_id = payload.module_id
    module.name = payload.name
    module.module_type = payload.module_type.value
    module.status = payload.status.value
    module.autonomy_level = payload.autonomy_level.value
    module.reactor_id = payload.reactor_id
    module.asset_id = payload.asset_id
    module.device_node_id = payload.device_node_id
    module.zone = payload.zone
    module.location = payload.location
    module.description = payload.description
    module.ros_node_name = payload.ros_node_name
    module.mqtt_node_id = payload.mqtt_node_id
    module.wiki_ref = payload.wiki_ref
    module.updated_at = _utcnow()
    session.add(module)
    session.commit()
    session.refresh(module)
    return get_module_detail_read(session, module.id)


def update_module_status(
    session: Session, module: AutonomousModule, payload: AutonomousModuleStatusUpdate
) -> AutonomousModuleDetailRead:
    module.status = payload.status.value
    module.updated_at = _utcnow()
    session.add(module)
    session.commit()
    session.refresh(module)
    return get_module_detail_read(session, module.id)


def replace_capabilities(
    session: Session,
    module: AutonomousModule,
    capabilities: list[ModuleCapabilityPayload],
) -> list[ModuleCapabilityRead]:
    _replace_capabilities(session, module.id, capabilities)
    module.updated_at = _utcnow()
    session.add(module)
    session.commit()
    return _load_capabilities(session, module.id)


def get_module_overview(session: Session) -> AutonomousModuleOverviewRead:
    modules = list(session.exec(select(AutonomousModule)).all())
    status_counter: Counter[str] = Counter(m.status for m in modules)
    type_counter: Counter[str] = Counter(m.module_type for m in modules)
    autonomy_counter: Counter[str] = Counter(m.autonomy_level for m in modules)
    return AutonomousModuleOverviewRead(
        total_modules=len(modules),
        nominal_modules=status_counter.get(ModuleStatus.nominal.value, 0),
        attention_modules=status_counter.get(ModuleStatus.attention.value, 0),
        warning_modules=status_counter.get(ModuleStatus.warning.value, 0),
        incident_modules=status_counter.get(ModuleStatus.incident.value, 0),
        offline_modules=status_counter.get(ModuleStatus.offline.value, 0),
        maintenance_modules=status_counter.get(ModuleStatus.maintenance.value, 0),
        disabled_modules=status_counter.get(ModuleStatus.disabled.value, 0),
        by_type=dict(type_counter),
        by_autonomy_level=dict(autonomy_counter),
    )


def _serialize_modules(
    session: Session, modules: list[AutonomousModule]
) -> list[AutonomousModuleRead]:
    if not modules:
        return []
    module_ids = [m.id for m in modules if m.id is not None]
    counts: dict[int, int] = {}
    if module_ids:
        rows = session.exec(
            select(ModuleCapability.autonomous_module_id).where(
                ModuleCapability.autonomous_module_id.in_(module_ids)
            )
        ).all()
        for row in rows:
            counts[row] = counts.get(row, 0) + 1

    return [
        AutonomousModuleRead(
            id=module.id,
            module_id=module.module_id,
            name=module.name,
            module_type=ModuleType(module.module_type),
            status=ModuleStatus(module.status),
            autonomy_level=ModuleAutonomyLevel(module.autonomy_level),
            reactor_id=module.reactor_id,
            asset_id=module.asset_id,
            device_node_id=module.device_node_id,
            zone=module.zone,
            location=module.location,
            description=module.description,
            ros_node_name=module.ros_node_name,
            mqtt_node_id=module.mqtt_node_id,
            wiki_ref=module.wiki_ref,
            created_at=module.created_at,
            updated_at=module.updated_at,
            capability_count=counts.get(module.id or 0, 0),
        )
        for module in modules
    ]


def _load_capabilities(session: Session, module_id: int) -> list[ModuleCapabilityRead]:
    rows = list(
        session.exec(
            select(ModuleCapability)
            .where(ModuleCapability.autonomous_module_id == module_id)
            .order_by(ModuleCapability.capability_type.asc())
        ).all()
    )
    return [
        ModuleCapabilityRead(
            id=row.id,
            autonomous_module_id=row.autonomous_module_id,
            capability_type=ModuleCapabilityType(row.capability_type),
            is_enabled=row.is_enabled,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def _replace_capabilities(
    session: Session,
    module_id: int,
    capabilities: list[ModuleCapabilityPayload],
) -> None:
    seen: set[str] = set()
    deduped: list[ModuleCapabilityPayload] = []
    for item in capabilities:
        key = item.capability_type.value
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Duplicate capability: {key}',
            )
        seen.add(key)
        deduped.append(item)

    existing = list(
        session.exec(
            select(ModuleCapability).where(ModuleCapability.autonomous_module_id == module_id)
        ).all()
    )
    for row in existing:
        session.delete(row)
    session.flush()

    now = _utcnow()
    for item in deduped:
        session.add(
            ModuleCapability(
                autonomous_module_id=module_id,
                capability_type=item.capability_type.value,
                is_enabled=item.is_enabled,
                notes=item.notes,
                created_at=now,
                updated_at=now,
            )
        )
    session.flush()


def _ensure_unique_module_id(session: Session, module_id: str) -> None:
    existing = session.exec(
        select(AutonomousModule.id).where(AutonomousModule.module_id == module_id)
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Module with module_id={module_id} already exists',
        )


def _validate_refs(
    session: Session,
    reactor_id: int | None,
    asset_id: int | None,
    device_node_id: int | None,
) -> None:
    if reactor_id is not None and session.get(Reactor, reactor_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='reactor_id not found')
    if asset_id is not None and session.get(Asset, asset_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='asset_id not found')
    if device_node_id is not None and session.get(DeviceNode, device_node_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='device_node_id not found')


def _reactor_ref(session: Session, reactor_id: int | None) -> AutonomousModuleReactorRef | None:
    if reactor_id is None:
        return None
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        return None
    return AutonomousModuleReactorRef(id=reactor.id, name=reactor.name, status=reactor.status)


def _asset_ref(session: Session, asset_id: int | None) -> AutonomousModuleAssetRef | None:
    if asset_id is None:
        return None
    asset = session.get(Asset, asset_id)
    if asset is None:
        return None
    return AutonomousModuleAssetRef(
        id=asset.id, name=asset.name, asset_type=asset.asset_type, status=asset.status
    )


def _device_node_ref(
    session: Session, device_node_id: int | None
) -> AutonomousModuleDeviceNodeRef | None:
    if device_node_id is None:
        return None
    node = session.get(DeviceNode, device_node_id)
    if node is None:
        return None
    return AutonomousModuleDeviceNodeRef(
        id=node.id,
        name=node.name,
        node_id=node.node_id,
        node_type=node.node_type,
        status=node.status,
    )


def _open_incident_count(session: Session, module: AutonomousModule) -> int:
    if module.reactor_id is None and module.device_node_id is None and module.asset_id is None:
        return 0
    clauses = []
    if module.reactor_id is not None:
        clauses.append(SafetyIncident.reactor_id == module.reactor_id)
    if module.device_node_id is not None:
        clauses.append(SafetyIncident.device_node_id == module.device_node_id)
    if module.asset_id is not None:
        clauses.append(SafetyIncident.asset_id == module.asset_id)
    if not clauses:
        return 0
    from sqlalchemy import or_

    rows = session.exec(
        select(SafetyIncident.id).where(or_(*clauses), SafetyIncident.status == 'open')
    ).all()
    return len(rows)
