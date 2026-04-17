from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import WikiPage

router = APIRouter(prefix='/wiki', tags=['wiki'])


@router.get('/pages')
def list_wiki_pages(session: Session = Depends(get_session)):
    return session.exec(select(WikiPage)).all()
