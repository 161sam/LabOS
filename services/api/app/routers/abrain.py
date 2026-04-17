from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..db import get_session
from ..schemas import (
    ABrainContextRead,
    ABrainContextSection,
    ABrainPresetRead,
    ABrainQueryRequest,
    ABrainQueryResponse,
    ABrainStatusRead,
)
from ..services import abrain as abrain_service

router = APIRouter(prefix='/abrain', tags=['abrain'])


@router.get('/status', response_model=ABrainStatusRead)
def abrain_status():
    return abrain_service.get_status()


@router.get('/presets', response_model=list[ABrainPresetRead])
def abrain_presets():
    return abrain_service.list_presets()


@router.get('/context', response_model=ABrainContextRead)
def abrain_context(
    include_sections: list[ABrainContextSection] | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return abrain_service.build_lab_context(session, include_sections=include_sections)


@router.post('/query', response_model=ABrainQueryResponse)
def abrain_query(payload: ABrainQueryRequest, session: Session = Depends(get_session)):
    return abrain_service.query(session, payload)
