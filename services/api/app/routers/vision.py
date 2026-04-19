from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import VisionAnalysisRead
from ..services import photos as photo_service
from ..services import vision as vision_service

router = APIRouter(
    prefix='/vision',
    tags=['vision'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('/photos/{photo_id}', response_model=VisionAnalysisRead)
def get_photo_vision(photo_id: int, session: Session = Depends(get_session)):
    photo_service.get_photo_or_404(session, photo_id)
    analysis = vision_service.get_analysis_or_404(session, photo_id)
    return vision_service.to_read(analysis)


@router.get('/photos/{photo_id}/history', response_model=list[VisionAnalysisRead])
def list_photo_vision_history(photo_id: int, session: Session = Depends(get_session)):
    photo_service.get_photo_or_404(session, photo_id)
    analyses = vision_service.list_analyses(session, photo_id)
    return [vision_service.to_read(analysis) for analysis in analyses]


@router.post(
    '/analyze/{photo_id}',
    response_model=VisionAnalysisRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
def analyze_photo(photo_id: int, session: Session = Depends(get_session)):
    photo = photo_service.get_photo_or_404(session, photo_id)
    analysis = vision_service.analyze_photo(session, photo)
    return vision_service.to_read(analysis)
