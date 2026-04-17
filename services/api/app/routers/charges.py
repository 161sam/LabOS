from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Charge
from ..schemas import ChargeCreate

router = APIRouter(prefix='/charges', tags=['charges'])


@router.get('')
def list_charges(session: Session = Depends(get_session)):
    return session.exec(select(Charge)).all()


@router.post('')
def create_charge(payload: ChargeCreate, session: Session = Depends(get_session)):
    charge = Charge(
        name=payload.name,
        species=payload.species,
        status=payload.status,
        volume_l=payload.volume_l,
        reactor_id=payload.reactor_id,
        start_date=payload.start_date or date.today(),
        notes=payload.notes,
    )
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return charge
