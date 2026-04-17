from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Asset, Photo, Task, _utcnow
from ..schemas import (
    AssetCreate,
    AssetDetailRead,
    AssetOverviewRead,
    AssetRead,
    AssetStatus,
    AssetStatusUpdate,
    AssetUpdate,
)
from . import photos as photo_service
from . import tasks as task_service


def list_assets(
    session: Session,
    status_filter: AssetStatus | None = None,
    category_filter: str | None = None,
    location_filter: str | None = None,
    zone_filter: str | None = None,
) -> list[AssetRead]:
    statement = select(Asset)
    if status_filter is not None:
        statement = statement.where(Asset.status == status_filter.value)
    if category_filter:
        statement = statement.where(Asset.category.ilike(f'%{category_filter.strip()}%'))
    if location_filter:
        statement = statement.where(Asset.location.ilike(f'%{location_filter.strip()}%'))
    if zone_filter:
        statement = statement.where(Asset.zone.ilike(f'%{zone_filter.strip()}%'))

    assets = list(session.exec(statement.order_by(Asset.name.asc(), Asset.id.asc())).all())
    return _serialize_assets(session, assets)


def get_asset_or_404(session: Session, asset_id: int) -> Asset:
    asset = session.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Asset not found')
    return asset


def get_asset_read(session: Session, asset_id: int) -> AssetRead:
    asset = get_asset_or_404(session, asset_id)
    return _serialize_assets(session, [asset])[0]


def get_asset_detail_read(session: Session, asset_id: int) -> AssetDetailRead:
    asset_read = get_asset_read(session, asset_id)
    open_tasks = [task for task in task_service.list_tasks(session, asset_id=asset_id) if task.status != 'done']
    recent_photos = photo_service.list_photos(session, asset_id=asset_id, latest=True, limit=4)
    return AssetDetailRead(
        **asset_read.model_dump(),
        open_tasks=open_tasks,
        recent_photos=recent_photos,
    )


def create_asset(session: Session, payload: AssetCreate) -> AssetRead:
    asset = Asset(
        name=payload.name,
        asset_type=payload.asset_type.value,
        category=payload.category,
        status=payload.status.value,
        location=payload.location,
        zone=payload.zone,
        serial_number=payload.serial_number,
        manufacturer=payload.manufacturer,
        model=payload.model,
        notes=payload.notes,
        maintenance_notes=payload.maintenance_notes,
        last_maintenance_at=payload.last_maintenance_at,
        next_maintenance_at=payload.next_maintenance_at,
        wiki_ref=payload.wiki_ref,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return get_asset_read(session, asset.id)


def update_asset(session: Session, asset: Asset, payload: AssetUpdate) -> AssetRead:
    asset.name = payload.name
    asset.asset_type = payload.asset_type.value
    asset.category = payload.category
    asset.status = payload.status.value
    asset.location = payload.location
    asset.zone = payload.zone
    asset.serial_number = payload.serial_number
    asset.manufacturer = payload.manufacturer
    asset.model = payload.model
    asset.notes = payload.notes
    asset.maintenance_notes = payload.maintenance_notes
    asset.last_maintenance_at = payload.last_maintenance_at
    asset.next_maintenance_at = payload.next_maintenance_at
    asset.wiki_ref = payload.wiki_ref
    asset.updated_at = _utcnow()
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return get_asset_read(session, asset.id)


def update_asset_status(session: Session, asset: Asset, payload: AssetStatusUpdate) -> AssetRead:
    asset.status = payload.status.value
    asset.updated_at = _utcnow()
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return get_asset_read(session, asset.id)


def get_asset_overview(session: Session) -> AssetOverviewRead:
    active_assets = len(session.exec(select(Asset.id).where(Asset.status == AssetStatus.active.value)).all())
    assets_in_maintenance = len(
        session.exec(select(Asset.id).where(Asset.status == AssetStatus.maintenance.value)).all()
    )
    assets_in_error = len(session.exec(select(Asset.id).where(Asset.status == AssetStatus.error.value)).all())
    upcoming_assets = list(
        session.exec(
            select(Asset)
            .where(Asset.next_maintenance_at.is_not(None), Asset.status != AssetStatus.retired.value)
            .order_by(Asset.next_maintenance_at.asc(), Asset.name.asc())
            .limit(5)
        ).all()
    )
    return AssetOverviewRead(
        active_assets=active_assets,
        assets_in_maintenance=assets_in_maintenance,
        assets_in_error=assets_in_error,
        upcoming_maintenance_assets=_serialize_assets(session, upcoming_assets),
    )


def _serialize_assets(session: Session, assets: list[Asset]) -> list[AssetRead]:
    if not assets:
        return []

    asset_ids = [asset.id for asset in assets if asset.id is not None]
    open_task_counts: dict[int, int] = {}
    photo_counts: dict[int, int] = {}

    if asset_ids:
        task_rows = session.exec(
            select(Task.asset_id, Task.status).where(Task.asset_id.in_(asset_ids))
        ).all()
        for asset_id, task_status in task_rows:
            if asset_id is not None and task_status != 'done':
                open_task_counts[asset_id] = open_task_counts.get(asset_id, 0) + 1

        photo_rows = session.exec(select(Photo.asset_id).where(Photo.asset_id.in_(asset_ids))).all()
        for asset_id in photo_rows:
            if asset_id is not None:
                photo_counts[asset_id] = photo_counts.get(asset_id, 0) + 1

    return [
        AssetRead(
            id=asset.id,
            name=asset.name,
            asset_type=asset.asset_type,
            category=asset.category,
            status=asset.status,
            location=asset.location,
            zone=asset.zone,
            serial_number=asset.serial_number,
            manufacturer=asset.manufacturer,
            model=asset.model,
            notes=asset.notes,
            maintenance_notes=asset.maintenance_notes,
            last_maintenance_at=asset.last_maintenance_at,
            next_maintenance_at=asset.next_maintenance_at,
            wiki_ref=asset.wiki_ref,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            open_task_count=open_task_counts.get(asset.id or 0, 0),
            photo_count=photo_counts.get(asset.id or 0, 0),
        )
        for asset in assets
    ]
