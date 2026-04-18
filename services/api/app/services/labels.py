from __future__ import annotations

from io import BytesIO
import re
import secrets
from urllib.parse import quote

from fastapi import HTTPException, status
import segno
from sqlmodel import Session, select

from ..config import settings
from ..models import Label, _utcnow
from ..schemas import (
    LabelActiveUpdate,
    LabelCreate,
    LabelOverviewRead,
    LabelRead,
    LabelTargetRead,
    LabelTargetType,
    LabelType,
    LabelUpdate,
)
from . import assets as asset_service
from . import inventory as inventory_service

_LABEL_CODE_PATTERN = re.compile(r'^[A-Z0-9][A-Z0-9._-]{2,79}$')


def list_labels(
    session: Session,
    target_type_filter: LabelTargetType | None = None,
    active_filter: bool | None = None,
    target_id_filter: int | None = None,
) -> list[LabelRead]:
    statement = select(Label)
    if target_type_filter is not None:
        statement = statement.where(Label.target_type == target_type_filter.value)
    if active_filter is not None:
        statement = statement.where(Label.is_active == active_filter)
    if target_id_filter is not None:
        statement = statement.where(Label.target_id == target_id_filter)

    labels = list(session.exec(statement.order_by(Label.created_at.desc(), Label.id.desc())).all())
    return [_build_label_read(session, label) for label in labels]


def get_label_by_id_or_404(session: Session, label_id: int) -> Label:
    label = session.get(Label, label_id)
    if label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Label not found')
    return label


def get_label_by_code_or_404(session: Session, label_code: str) -> Label:
    normalized_code = _normalize_label_code(label_code)
    label = session.exec(select(Label).where(Label.label_code == normalized_code)).first()
    if label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Label not found')
    return label


def get_label_read(session: Session, label_code: str) -> LabelRead:
    label = get_label_by_code_or_404(session, label_code)
    return _build_label_read(session, label)


def get_label_target(session: Session, label_code: str) -> LabelTargetRead:
    label = get_label_by_code_or_404(session, label_code)
    label_read = _build_label_read(session, label)
    if label.target_type == LabelTargetType.asset.value:
        return LabelTargetRead(
            label=label_read,
            asset=asset_service.get_asset_read(session, label.target_id),
        )
    if label.target_type == LabelTargetType.inventory_item.value:
        return LabelTargetRead(
            label=label_read,
            inventory_item=inventory_service.get_inventory_read(session, label.target_id),
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsupported label target type')


def create_label(session: Session, payload: LabelCreate) -> LabelRead:
    normalized_code = _ensure_unique_label_code(session, payload.label_code, target_type=payload.target_type)
    target_summary = _resolve_target_summary(session, payload.target_type, payload.target_id)

    label = Label(
        label_code=normalized_code,
        label_type=payload.label_type.value,
        target_type=payload.target_type.value,
        target_id=payload.target_id,
        display_name=payload.display_name or target_summary['target_name'],
        location_snapshot=payload.location_snapshot or target_summary['target_location'],
        note=payload.note,
        is_active=payload.is_active,
    )
    session.add(label)
    session.commit()
    session.refresh(label)
    return _build_label_read(session, label)


def update_label(session: Session, label: Label, payload: LabelUpdate) -> LabelRead:
    normalized_code = _ensure_unique_label_code(
        session,
        payload.label_code or label.label_code,
        target_type=payload.target_type,
        exclude_id=label.id,
    )
    target_summary = _resolve_target_summary(session, payload.target_type, payload.target_id)

    label.label_code = normalized_code
    label.label_type = payload.label_type.value
    label.target_type = payload.target_type.value
    label.target_id = payload.target_id
    label.display_name = payload.display_name or target_summary['target_name']
    label.location_snapshot = payload.location_snapshot or target_summary['target_location']
    label.note = payload.note
    label.is_active = payload.is_active
    label.updated_at = _utcnow()
    session.add(label)
    session.commit()
    session.refresh(label)
    return _build_label_read(session, label)


def update_label_active(session: Session, label: Label, payload: LabelActiveUpdate) -> LabelRead:
    label.is_active = payload.is_active
    label.updated_at = _utcnow()
    session.add(label)
    session.commit()
    session.refresh(label)
    return _build_label_read(session, label)


def get_label_overview(session: Session) -> LabelOverviewRead:
    active_labels = list(session.exec(select(Label).where(Label.is_active.is_(True))).all())
    labeled_assets = len({label.target_id for label in active_labels if label.target_type == LabelTargetType.asset.value})
    labeled_inventory_items = len(
        {label.target_id for label in active_labels if label.target_type == LabelTargetType.inventory_item.value}
    )
    recent_labels = list(session.exec(select(Label).order_by(Label.created_at.desc(), Label.id.desc()).limit(4)).all())
    return LabelOverviewRead(
        labeled_assets=labeled_assets,
        labeled_inventory_items=labeled_inventory_items,
        recent_labels=[_build_label_read(session, label) for label in recent_labels],
    )


def render_label_qr_svg(session: Session, label_code: str) -> str:
    label = get_label_by_code_or_404(session, label_code)
    qr = segno.make(_scan_url(label.label_code), micro=False)
    buffer = BytesIO()
    qr.save(buffer, kind='svg', scale=5, border=2, xmldecl=False, svgns=True)
    return buffer.getvalue().decode('utf-8')


def _build_label_read(session: Session, label: Label) -> LabelRead:
    target_summary = _resolve_target_summary(
        session,
        LabelTargetType(label.target_type),
        label.target_id,
    )
    scan_path = _scan_path(label.label_code)
    qr_path = _qr_path(label.label_code)
    target_manager_path = target_summary['manager_path']
    return LabelRead(
        id=label.id,
        label_code=label.label_code,
        label_type=label.label_type,
        target_type=label.target_type,
        target_id=label.target_id,
        display_name=label.display_name,
        location_snapshot=label.location_snapshot,
        note=label.note,
        is_active=label.is_active,
        created_at=label.created_at,
        updated_at=label.updated_at,
        target_name=target_summary['target_name'],
        target_location=target_summary['target_location'],
        target_status=target_summary['target_status'],
        scan_path=scan_path,
        scan_url=_scan_url(label.label_code),
        target_manager_path=target_manager_path,
        target_manager_url=f"{settings.public_web_base_url.rstrip('/')}{target_manager_path}",
        qr_path=qr_path,
        qr_url=f"{settings.public_api_base_url.rstrip('/')}{qr_path}",
    )


def _resolve_target_summary(session: Session, target_type: LabelTargetType, target_id: int) -> dict[str, str | None]:
    if target_type == LabelTargetType.asset:
        asset = asset_service.get_asset_read(session, target_id)
        return {
            'target_name': asset.name,
            'target_location': _join_location(asset.location, asset.zone),
            'target_status': asset.status,
            'manager_path': '/assets',
        }
    if target_type == LabelTargetType.inventory_item:
        item = inventory_service.get_inventory_read(session, target_id)
        return {
            'target_name': item.name,
            'target_location': _join_location(item.location, item.zone),
            'target_status': item.status,
            'manager_path': '/inventory',
        }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsupported label target type')


def _join_location(location: str | None, zone: str | None) -> str | None:
    parts = [location, zone]
    resolved = ' / '.join(part for part in parts if part)
    return resolved or None


def _scan_path(label_code: str) -> str:
    return f"/scan/{quote(label_code)}"


def _scan_url(label_code: str) -> str:
    return f"{settings.public_web_base_url.rstrip('/')}{_scan_path(label_code)}"


def _qr_path(label_code: str) -> str:
    return f"/api/v1/labels/{quote(label_code)}/qr"


def _normalize_label_code(label_code: str) -> str:
    normalized = label_code.strip().upper().replace(' ', '-')
    if not _LABEL_CODE_PATTERN.match(normalized):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='label_code must use only A-Z, 0-9, dot, dash or underscore',
        )
    return normalized


def _ensure_unique_label_code(
    session: Session,
    label_code: str | None,
    *,
    target_type: LabelTargetType,
    exclude_id: int | None = None,
) -> str:
    if label_code:
        normalized_code = _normalize_label_code(label_code)
        _assert_label_code_available(session, normalized_code, exclude_id=exclude_id)
        return normalized_code

    prefix = 'AST' if target_type == LabelTargetType.asset else 'INV'
    for _ in range(12):
        candidate = f'LBL-{prefix}-{secrets.token_hex(4).upper()}'
        existing = session.exec(select(Label.id).where(Label.label_code == candidate)).first()
        if existing is None:
            return candidate
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to generate unique label code')


def _assert_label_code_available(session: Session, label_code: str, *, exclude_id: int | None = None) -> None:
    statement = select(Label).where(Label.label_code == label_code)
    existing = session.exec(statement).first()
    if existing is None:
        return
    if exclude_id is not None and existing.id == exclude_id:
        return
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Label code already exists')
