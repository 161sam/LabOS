from datetime import date

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Charge, Reactor
from ..schemas import ChargeCreate, ChargeStatusUpdate, ChargeUpdate


def list_charges(session: Session) -> list[Charge]:
    statement = select(Charge).order_by(Charge.start_date.desc(), Charge.id.desc())
    return list(session.exec(statement).all())


def get_charge_or_404(session: Session, charge_id: int) -> Charge:
    charge = session.get(Charge, charge_id)
    if charge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Charge not found')
    return charge


def create_charge(session: Session, payload: ChargeCreate) -> Charge:
    _validate_reactor_reference(session, payload.reactor_id)
    charge = Charge(
        name=payload.name,
        species=payload.species,
        status=payload.status.value,
        volume_l=payload.volume_l,
        reactor_id=payload.reactor_id,
        start_date=payload.start_date or date.today(),
        notes=payload.notes,
    )
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return charge


def update_charge(session: Session, charge: Charge, payload: ChargeUpdate) -> Charge:
    _validate_reactor_reference(session, payload.reactor_id)
    charge.name = payload.name
    charge.species = payload.species
    charge.status = payload.status.value
    charge.volume_l = payload.volume_l
    charge.reactor_id = payload.reactor_id
    charge.start_date = payload.start_date or charge.start_date
    charge.notes = payload.notes
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return charge


def update_charge_status(session: Session, charge: Charge, payload: ChargeStatusUpdate) -> Charge:
    charge.status = payload.status.value
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return charge


def _validate_reactor_reference(session: Session, reactor_id: int | None) -> None:
    if reactor_id is None:
        return

    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced reactor does not exist',
        )
