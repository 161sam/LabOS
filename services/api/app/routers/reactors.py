from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Reactor
from ..schemas import ReactorCreate

router = APIRouter(prefix='/reactors', tags=['reactors'])


@router.get('')
def list_reactors(session: Session = Depends(get_session)):
    return session.exec(select(Reactor)).all()


@router.post('')
def create_reactor(payload: ReactorCreate, session: Session = Depends(get_session)):
    reactor = Reactor(**payload.model_dump())
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    return reactor
