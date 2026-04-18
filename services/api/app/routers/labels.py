from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    LabelActiveUpdate,
    LabelCreate,
    LabelOverviewRead,
    LabelRead,
    LabelTargetRead,
    LabelTargetType,
    LabelUpdate,
)
from ..services import labels as label_service

router = APIRouter(prefix='/labels', tags=['labels'], dependencies=[Depends(require_authenticated_user)])


@router.get('', response_model=list[LabelRead])
def list_labels(
    target_type: LabelTargetType | None = Query(default=None),
    active: bool | None = Query(default=None),
    target_id: int | None = Query(default=None, ge=1),
    session: Session = Depends(get_session),
):
    return label_service.list_labels(
        session,
        target_type_filter=target_type,
        active_filter=active,
        target_id_filter=target_id,
    )


@router.get('/overview', response_model=LabelOverviewRead)
def get_label_overview(session: Session = Depends(get_session)):
    return label_service.get_label_overview(session)


@router.get('/{label_code}/target', response_model=LabelTargetRead)
def get_label_target(label_code: str, session: Session = Depends(get_session)):
    return label_service.get_label_target(session, label_code)


@router.get('/{label_code}/qr')
def get_label_qr(label_code: str, session: Session = Depends(get_session)):
    svg = label_service.render_label_qr_svg(session, label_code)
    return Response(content=svg, media_type='image/svg+xml')


@router.get('/{label_id:int}', response_model=LabelRead)
def get_label_by_id(label_id: int, session: Session = Depends(get_session)):
    label = label_service.get_label_by_id_or_404(session, label_id)
    return label_service.get_label_read(session, label.label_code)


@router.get('/{label_code}', response_model=LabelRead)
def get_label(label_code: str, session: Session = Depends(get_session)):
    return label_service.get_label_read(session, label_code)


@router.post('', response_model=LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(
    payload: LabelCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return label_service.create_label(session, payload)


@router.put('/{label_id:int}', response_model=LabelRead)
def update_label(
    label_id: int,
    payload: LabelUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    label = label_service.get_label_by_id_or_404(session, label_id)
    return label_service.update_label(session, label, payload)


@router.patch('/{label_id:int}/active', response_model=LabelRead)
def update_label_active(
    label_id: int,
    payload: LabelActiveUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    label = label_service.get_label_by_id_or_404(session, label_id)
    return label_service.update_label_active(session, label, payload)
