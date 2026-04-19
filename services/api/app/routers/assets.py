from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    AssetCreate,
    AssetDetailRead,
    AssetOverviewRead,
    AssetRead,
    AssetStatus,
    AssetStatusUpdate,
    AssetUpdate,
)
from ..services import assets as asset_service

router = APIRouter(prefix='/assets', tags=['assets'], dependencies=[Depends(require_authenticated_user)])


@router.get('', response_model=list[AssetRead])
def list_assets(
    status_filter: AssetStatus | None = Query(default=None, alias='status'),
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    zone: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return asset_service.list_assets(
        session,
        status_filter=status_filter,
        category_filter=category,
        location_filter=location,
        zone_filter=zone,
    )


@router.get('/overview', response_model=AssetOverviewRead)
def get_asset_overview(session: Session = Depends(get_session)):
    return asset_service.get_asset_overview(session)


@router.get('/{asset_id}', response_model=AssetDetailRead)
def get_asset(asset_id: int, session: Session = Depends(get_session)):
    return asset_service.get_asset_detail_read(session, asset_id)


@router.post('', response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return asset_service.create_asset(session, payload)


@router.put('/{asset_id}', response_model=AssetRead)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    asset = asset_service.get_asset_or_404(session, asset_id)
    return asset_service.update_asset(session, asset, payload)


@router.patch('/{asset_id}/status', response_model=AssetRead)
def update_asset_status(
    asset_id: int,
    payload: AssetStatusUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    asset = asset_service.get_asset_or_404(session, asset_id)
    return asset_service.update_asset_status(session, asset, payload)
