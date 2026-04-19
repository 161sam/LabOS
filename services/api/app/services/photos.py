import re
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select

from ..config import settings
from ..models import Asset, Charge, Photo, Reactor, _utcnow
from ..schemas import PhotoRead, PhotoUpdate, PhotoUploadData
from . import reactor_health as reactor_health_service
from . import vision as vision_service

_ALLOWED_MIME_EXTENSIONS = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}


def list_photos(
    session: Session,
    charge_id: int | None = None,
    reactor_id: int | None = None,
    asset_id: int | None = None,
    latest: bool = False,
    limit: int | None = None,
) -> list[PhotoRead]:
    statement = select(Photo)
    if charge_id is not None:
        statement = statement.where(Photo.charge_id == charge_id)
    if reactor_id is not None:
        statement = statement.where(Photo.reactor_id == reactor_id)
    if asset_id is not None:
        statement = statement.where(Photo.asset_id == asset_id)

    statement = statement.order_by(Photo.created_at.desc(), Photo.id.desc())
    if limit is not None:
        statement = statement.limit(limit)
    elif latest:
        statement = statement.limit(8)

    photos = list(session.exec(statement).all())
    return _serialize_photos(session, photos)


def count_photos(session: Session) -> int:
    return len(session.exec(select(Photo.id)).all())


def count_recent_uploads(session: Session, days: int = 7) -> int:
    since = _utcnow() - timedelta(days=days)
    return len(session.exec(select(Photo.id).where(Photo.created_at >= since)).all())


def get_photo_or_404(session: Session, photo_id: int) -> Photo:
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


def get_photo_read(session: Session, photo_id: int) -> PhotoRead:
    photo = get_photo_or_404(session, photo_id)
    return _serialize_photos(session, [photo])[0]


async def create_photo_upload(
    session: Session,
    upload: UploadFile,
    payload: PhotoUploadData,
) -> PhotoRead:
    _validate_references(session, payload.charge_id, payload.reactor_id, payload.asset_id)
    _validate_upload(upload)

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Uploaded file is empty')
    if len(file_bytes) > settings.photo_max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'Photo exceeds max size of {settings.photo_max_upload_bytes} bytes',
        )

    relative_storage_path, filename = _store_file(upload, file_bytes)
    photo = Photo(
        filename=filename,
        original_filename=_safe_original_filename(upload.filename),
        mime_type=upload.content_type or 'application/octet-stream',
        size_bytes=len(file_bytes),
        storage_path=relative_storage_path,
        title=payload.title,
        notes=payload.notes,
        charge_id=payload.charge_id,
        reactor_id=payload.reactor_id,
        asset_id=payload.asset_id,
        uploaded_by=payload.uploaded_by,
        captured_at=payload.captured_at,
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)
    try:
        vision_service.analyze_photo(session, photo)
    except Exception:
        session.rollback()
    if photo.reactor_id is not None:
        try:
            reactor_health_service.assess_reactor(session, photo.reactor_id)
        except Exception:
            session.rollback()
    return get_photo_read(session, photo.id)


def update_photo(session: Session, photo: Photo, payload: PhotoUpdate) -> PhotoRead:
    _validate_references(session, payload.charge_id, payload.reactor_id, payload.asset_id)
    photo.title = payload.title
    photo.notes = payload.notes
    photo.charge_id = payload.charge_id
    photo.reactor_id = payload.reactor_id
    photo.asset_id = payload.asset_id
    photo.uploaded_by = payload.uploaded_by
    photo.captured_at = payload.captured_at
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return get_photo_read(session, photo.id)


def get_photo_file_path(photo: Photo) -> Path:
    file_path = Path(settings.storage_path) / photo.storage_path
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stored photo file not found')
    return file_path


def _store_file(upload: UploadFile, file_bytes: bytes) -> tuple[str, str]:
    now = _utcnow()
    extension = _ALLOWED_MIME_EXTENSIONS[upload.content_type or '']
    filename = f'{uuid4().hex}{extension}'
    relative_directory = Path('photos') / f'{now:%Y}' / f'{now:%m}'
    absolute_directory = Path(settings.storage_path) / relative_directory
    absolute_directory.mkdir(parents=True, exist_ok=True)

    file_path = absolute_directory / filename
    file_path.write_bytes(file_bytes)
    return str(relative_directory / filename), filename


def _validate_upload(upload: UploadFile) -> None:
    if upload.filename is None or not upload.filename.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Photo filename is required')
    if upload.content_type not in _ALLOWED_MIME_EXTENSIONS:
        allowed_types = ', '.join(sorted(_ALLOWED_MIME_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f'Unsupported photo type. Allowed: {allowed_types}',
        )


def _safe_original_filename(filename: str | None) -> str:
    if not filename:
        return 'upload'
    normalized = Path(filename).name
    sanitized = re.sub(r'[^A-Za-z0-9._-]+', '_', normalized).strip('._')
    return sanitized or 'upload'


def _serialize_photos(session: Session, photos: list[Photo]) -> list[PhotoRead]:
    if not photos:
        return []

    photo_ids = [photo.id for photo in photos if photo.id is not None]
    charge_ids = sorted({photo.charge_id for photo in photos if photo.charge_id is not None})
    reactor_ids = sorted({photo.reactor_id for photo in photos if photo.reactor_id is not None})
    asset_ids = sorted({photo.asset_id for photo in photos if photo.asset_id is not None})
    vision_by_photo = vision_service.get_latest_for_photos(session, photo_ids)
    charge_names = (
        {charge.id: charge.name for charge in session.exec(select(Charge).where(Charge.id.in_(charge_ids))).all()}
        if charge_ids
        else {}
    )
    reactor_names = (
        {
            reactor.id: reactor.name
            for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
        }
        if reactor_ids
        else {}
    )
    asset_names = (
        {asset.id: asset.name for asset in session.exec(select(Asset).where(Asset.id.in_(asset_ids))).all()}
        if asset_ids
        else {}
    )

    return [
        PhotoRead(
            id=photo.id,
            filename=photo.filename,
            original_filename=photo.original_filename,
            mime_type=photo.mime_type,
            size_bytes=photo.size_bytes,
            storage_path=photo.storage_path,
            title=photo.title,
            notes=photo.notes,
            charge_id=photo.charge_id,
            reactor_id=photo.reactor_id,
            asset_id=photo.asset_id,
            created_at=photo.created_at,
            uploaded_by=photo.uploaded_by,
            captured_at=photo.captured_at,
            charge_name=charge_names.get(photo.charge_id),
            reactor_name=reactor_names.get(photo.reactor_id),
            asset_name=asset_names.get(photo.asset_id),
            file_url=f'/api/v1/photos/{photo.id}/file',
            latest_vision=(
                vision_service.to_read(vision_by_photo[photo.id])
                if photo.id in vision_by_photo
                else None
            ),
        )
        for photo in photos
    ]


def _validate_references(
    session: Session,
    charge_id: int | None,
    reactor_id: int | None,
    asset_id: int | None,
) -> None:
    if charge_id is not None and session.get(Charge, charge_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced charge does not exist',
        )
    if reactor_id is not None and session.get(Reactor, reactor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced reactor does not exist',
        )
    if asset_id is not None and session.get(Asset, asset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced asset does not exist',
        )
