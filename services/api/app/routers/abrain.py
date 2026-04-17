from fastapi import APIRouter

from ..config import settings

router = APIRouter(prefix='/abrain', tags=['abrain'])


@router.get('/status')
def abrain_status():
    return {
        'connected': False,
        'base_url': settings.abrain_base_url,
        'note': 'ABrain-Connector ist als V1-Platzhalter vorbereitet.'
    }
