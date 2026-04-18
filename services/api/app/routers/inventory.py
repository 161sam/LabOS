from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    InventoryCreate,
    InventoryOverviewRead,
    InventoryRead,
    InventoryStatus,
    InventoryStatusUpdate,
    InventoryUpdate,
)
from ..services import inventory as inventory_service

router = APIRouter(prefix='/inventory', tags=['inventory'], dependencies=[Depends(require_authenticated_user)])


@router.get('', response_model=list[InventoryRead])
def list_inventory(
    status_filter: InventoryStatus | None = Query(default=None, alias='status'),
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    zone: str | None = Query(default=None),
    search: str | None = Query(default=None),
    low_stock: bool = Query(default=False),
    session: Session = Depends(get_session),
):
    return inventory_service.list_inventory(
        session,
        status_filter=status_filter,
        category_filter=category,
        location_filter=location,
        zone_filter=zone,
        search=search,
        low_stock_only=low_stock,
    )


@router.get('/overview', response_model=InventoryOverviewRead)
def get_inventory_overview(session: Session = Depends(get_session)):
    return inventory_service.get_inventory_overview(session)


@router.get('/{inventory_id}', response_model=InventoryRead)
def get_inventory_item(inventory_id: int, session: Session = Depends(get_session)):
    return inventory_service.get_inventory_read(session, inventory_id)


@router.post('', response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return inventory_service.create_inventory_item(session, payload)


@router.put('/{inventory_id}', response_model=InventoryRead)
def update_inventory_item(
    inventory_id: int,
    payload: InventoryUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    item = inventory_service.get_inventory_or_404(session, inventory_id)
    return inventory_service.update_inventory_item(session, item, payload)


@router.patch('/{inventory_id}/status', response_model=InventoryRead)
def update_inventory_status(
    inventory_id: int,
    payload: InventoryStatusUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    item = inventory_service.get_inventory_or_404(session, inventory_id)
    return inventory_service.update_inventory_status(session, item, payload)
