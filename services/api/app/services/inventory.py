from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlmodel import Session, select

from ..models import Asset, InventoryItem, _utcnow
from ..schemas import (
    InventoryCreate,
    InventoryOverviewRead,
    InventoryRead,
    InventoryStatus,
    InventoryStatusUpdate,
    InventoryUpdate,
)
from . import assets as asset_service

_DECIMAL_STEP = Decimal('0.001')


def list_inventory(
    session: Session,
    status_filter: InventoryStatus | None = None,
    category_filter: str | None = None,
    location_filter: str | None = None,
    zone_filter: str | None = None,
    search: str | None = None,
    low_stock_only: bool = False,
) -> list[InventoryRead]:
    statement = select(InventoryItem)
    if status_filter is not None:
        statement = statement.where(InventoryItem.status == status_filter.value)
    if category_filter:
        statement = statement.where(InventoryItem.category.ilike(f'%{category_filter.strip()}%'))
    if location_filter:
        statement = statement.where(InventoryItem.location.ilike(f'%{location_filter.strip()}%'))
    if zone_filter:
        statement = statement.where(InventoryItem.zone.ilike(f'%{zone_filter.strip()}%'))
    if search:
        search_term = f'%{search.strip()}%'
        statement = statement.where(
            or_(
                InventoryItem.name.ilike(search_term),
                InventoryItem.category.ilike(search_term),
                InventoryItem.location.ilike(search_term),
                InventoryItem.zone.ilike(search_term),
                InventoryItem.supplier.ilike(search_term),
                InventoryItem.sku.ilike(search_term),
            )
        )
    if low_stock_only:
        statement = statement.where(_needs_restock_sql())

    items = list(session.exec(statement.order_by(InventoryItem.name.asc(), InventoryItem.id.asc())).all())
    return _serialize_inventory(session, items)


def get_inventory_or_404(session: Session, inventory_id: int) -> InventoryItem:
    item = session.get(InventoryItem, inventory_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Inventory item not found')
    return item


def get_inventory_read(session: Session, inventory_id: int) -> InventoryRead:
    item = get_inventory_or_404(session, inventory_id)
    return _serialize_inventory(session, [item])[0]


def create_inventory_item(session: Session, payload: InventoryCreate) -> InventoryRead:
    _validate_asset_reference(session, payload.asset_id)

    item = InventoryItem(
        name=payload.name,
        category=payload.category,
        status=_resolve_status(payload.status, payload.quantity, payload.min_quantity).value,
        quantity=_to_decimal(payload.quantity),
        unit=payload.unit,
        min_quantity=_to_optional_decimal(payload.min_quantity),
        location=payload.location,
        zone=payload.zone,
        supplier=payload.supplier,
        sku=payload.sku,
        notes=payload.notes,
        asset_id=payload.asset_id,
        wiki_ref=payload.wiki_ref,
        last_restocked_at=payload.last_restocked_at,
        expiry_date=payload.expiry_date,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return get_inventory_read(session, item.id)


def update_inventory_item(session: Session, item: InventoryItem, payload: InventoryUpdate) -> InventoryRead:
    _validate_asset_reference(session, payload.asset_id)

    item.name = payload.name
    item.category = payload.category
    item.status = _resolve_status(payload.status, payload.quantity, payload.min_quantity).value
    item.quantity = _to_decimal(payload.quantity)
    item.unit = payload.unit
    item.min_quantity = _to_optional_decimal(payload.min_quantity)
    item.location = payload.location
    item.zone = payload.zone
    item.supplier = payload.supplier
    item.sku = payload.sku
    item.notes = payload.notes
    item.asset_id = payload.asset_id
    item.wiki_ref = payload.wiki_ref
    item.last_restocked_at = payload.last_restocked_at
    item.expiry_date = payload.expiry_date
    item.updated_at = _utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return get_inventory_read(session, item.id)


def update_inventory_status(session: Session, item: InventoryItem, payload: InventoryStatusUpdate) -> InventoryRead:
    item.status = _resolve_status(payload.status, float(item.quantity), _decimal_to_float(item.min_quantity)).value
    item.updated_at = _utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return get_inventory_read(session, item.id)


def get_inventory_overview(session: Session) -> InventoryOverviewRead:
    items = list(session.exec(select(InventoryItem).order_by(InventoryItem.name.asc(), InventoryItem.id.asc())).all())
    serialized_items = _serialize_inventory(session, items)

    low_stock_items = [item for item in serialized_items if item.is_low_stock]
    out_of_stock_items = [item for item in serialized_items if item.is_out_of_stock]
    critical_items = [
        item
        for item in serialized_items
        if item.needs_restock and item.status != InventoryStatus.archived
    ]
    critical_items.sort(key=lambda item: (not item.is_out_of_stock, item.quantity, item.name.lower()))

    return InventoryOverviewRead(
        total_items=len(serialized_items),
        low_stock_items=len(low_stock_items),
        out_of_stock_items=len(out_of_stock_items),
        critical_items=critical_items[:5],
    )


def _serialize_inventory(session: Session, items: list[InventoryItem]) -> list[InventoryRead]:
    if not items:
        return []

    asset_ids = sorted({item.asset_id for item in items if item.asset_id is not None})
    asset_name_by_id: dict[int, str] = {}
    if asset_ids:
        assets = session.exec(select(Asset.id, Asset.name).where(Asset.id.in_(asset_ids))).all()
        asset_name_by_id = {asset_id: asset_name for asset_id, asset_name in assets}

    return [
        InventoryRead(
            id=item.id,
            name=item.name,
            category=item.category,
            status=item.status,
            quantity=_decimal_to_float(item.quantity),
            unit=item.unit,
            min_quantity=_decimal_to_float(item.min_quantity),
            location=item.location,
            zone=item.zone,
            supplier=item.supplier,
            sku=item.sku,
            notes=item.notes,
            asset_id=item.asset_id,
            asset_name=asset_name_by_id.get(item.asset_id or 0),
            wiki_ref=item.wiki_ref,
            last_restocked_at=item.last_restocked_at,
            expiry_date=item.expiry_date,
            created_at=item.created_at,
            updated_at=item.updated_at,
            is_low_stock=_is_low_stock(item.quantity, item.min_quantity),
            is_out_of_stock=_is_out_of_stock(item.quantity),
            needs_restock=_needs_restock(item.quantity, item.min_quantity),
        )
        for item in items
    ]


def _validate_asset_reference(session: Session, asset_id: int | None) -> None:
    if asset_id is not None:
        asset_service.get_asset_or_404(session, asset_id)


def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(_DECIMAL_STEP, rounding=ROUND_HALF_UP)


def _to_optional_decimal(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return _to_decimal(value)


def _decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _is_out_of_stock(quantity: Decimal) -> bool:
    return quantity <= 0


def _is_low_stock(quantity: Decimal, min_quantity: Decimal | None) -> bool:
    return quantity > 0 and min_quantity is not None and quantity <= min_quantity


def _needs_restock(quantity: Decimal, min_quantity: Decimal | None) -> bool:
    return _is_out_of_stock(quantity) or _is_low_stock(quantity, min_quantity)


def _needs_restock_sql():
    return or_(
        InventoryItem.quantity <= 0,
        and_(InventoryItem.min_quantity.is_not(None), InventoryItem.quantity <= InventoryItem.min_quantity),
    )


def _resolve_status(
    requested_status: InventoryStatus,
    quantity: float,
    min_quantity: float | None,
) -> InventoryStatus:
    if requested_status in {InventoryStatus.reserved, InventoryStatus.expired, InventoryStatus.archived}:
        return requested_status
    if quantity <= 0:
        return InventoryStatus.out_of_stock
    if min_quantity is not None and quantity <= min_quantity:
        return InventoryStatus.low_stock
    return InventoryStatus.available
