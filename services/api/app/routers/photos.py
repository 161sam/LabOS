from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import PhotoAnalysisStatusRead, PhotoRead, PhotoUpdate, PhotoUploadData
from ..services import photos as photo_service

router = APIRouter(
    prefix='/photos',
    tags=['photos'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[PhotoRead])
def list_photos(
    charge_id: int | None = Query(default=None, ge=1),
    reactor_id: int | None = Query(default=None, ge=1),
    asset_id: int | None = Query(default=None, ge=1),
    latest: bool = False,
    limit: int | None = Query(default=None, ge=1, le=50),
    session: Session = Depends(get_session),
):
    return photo_service.list_photos(
        session,
        charge_id=charge_id,
        reactor_id=reactor_id,
        asset_id=asset_id,
        latest=latest,
        limit=limit,
    )


@router.post(
    '/upload',
    response_model=PhotoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
async def upload_photo(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    charge_id: int | None = Form(default=None),
    reactor_id: int | None = Form(default=None),
    asset_id: int | None = Form(default=None),
    uploaded_by: str | None = Form(default=None),
    captured_at: datetime | None = Form(default=None),
    session: Session = Depends(get_session),
):
    payload = PhotoUploadData(
        title=title,
        notes=notes,
        charge_id=charge_id,
        reactor_id=reactor_id,
        asset_id=asset_id,
        uploaded_by=uploaded_by,
        captured_at=captured_at,
    )
    return await photo_service.create_photo_upload(session, file, payload)


@router.get('/{photo_id}/file')
def get_photo_file(photo_id: int, session: Session = Depends(get_session)):
    photo = photo_service.get_photo_or_404(session, photo_id)
    file_path = photo_service.get_photo_file_path(photo)
    return FileResponse(path=file_path, media_type=photo.mime_type, filename=photo.original_filename)


@router.get('/{photo_id}/analysis-status', response_model=PhotoAnalysisStatusRead)
def get_photo_analysis_status(photo_id: int, session: Session = Depends(get_session)):
    photo_service.get_photo_or_404(session, photo_id)
    return {
        'photo_id': photo_id,
        'status': 'pending',
        'detail': 'Vision analysis is not active yet for Photo Upload + Vision Basis V1.',
    }


@router.get('/{photo_id}', response_model=PhotoRead)
def get_photo(photo_id: int, session: Session = Depends(get_session)):
    return photo_service.get_photo_read(session, photo_id)


@router.put(
    '/{photo_id}',
    response_model=PhotoRead,
    dependencies=[Depends(require_operator_user)],
)
def update_photo(photo_id: int, payload: PhotoUpdate, session: Session = Depends(get_session)):
    photo = photo_service.get_photo_or_404(session, photo_id)
    return photo_service.update_photo(session, photo, payload)
