from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Reactor
from ..schemas import ReactorCreate, ReactorStatusUpdate, ReactorUpdate
from . import reactor_ops as reactor_ops_service


def list_reactors(session: Session) -> list[Reactor]:
    statement = select(Reactor).order_by(Reactor.name.asc(), Reactor.id.asc())
    return list(session.exec(statement).all())


def get_reactor_or_404(session: Session, reactor_id: int) -> Reactor:
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    return reactor


def create_reactor(session: Session, payload: ReactorCreate) -> Reactor:
    reactor = Reactor(
        name=payload.name,
        reactor_type=payload.reactor_type,
        status=payload.status.value,
        volume_l=payload.volume_l,
        location=payload.location,
        last_cleaned_at=payload.last_cleaned_at,
        notes=payload.notes,
    )
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    reactor_ops_service.create_default_twin_for_reactor(session, reactor.id)
    return reactor


def update_reactor(session: Session, reactor: Reactor, payload: ReactorUpdate) -> Reactor:
    reactor.name = payload.name
    reactor.reactor_type = payload.reactor_type
    reactor.status = payload.status.value
    reactor.volume_l = payload.volume_l
    reactor.location = payload.location
    reactor.last_cleaned_at = payload.last_cleaned_at
    reactor.notes = payload.notes
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    return reactor


def update_reactor_status(session: Session, reactor: Reactor, payload: ReactorStatusUpdate) -> Reactor:
    reactor.status = payload.status.value
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    return reactor
