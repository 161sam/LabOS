from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..db import get_session
from ..schemas import ChargeCreate, ChargeRead, ChargeStatusUpdate, ChargeUpdate
from ..services import charges as charge_service

router = APIRouter(prefix='/charges', tags=['charges'])


@router.get('', response_model=list[ChargeRead])
def list_charges(session: Session = Depends(get_session)):
    return charge_service.list_charges(session)


@router.get('/{charge_id}', response_model=ChargeRead)
def get_charge(charge_id: int, session: Session = Depends(get_session)):
    return charge_service.get_charge_or_404(session, charge_id)


@router.post('', response_model=ChargeRead, status_code=status.HTTP_201_CREATED)
def create_charge(payload: ChargeCreate, session: Session = Depends(get_session)):
    return charge_service.create_charge(session, payload)


@router.put('/{charge_id}', response_model=ChargeRead)
def update_charge(charge_id: int, payload: ChargeUpdate, session: Session = Depends(get_session)):
    charge = charge_service.get_charge_or_404(session, charge_id)
    return charge_service.update_charge(session, charge, payload)


@router.patch('/{charge_id}/status', response_model=ChargeRead)
def update_charge_status(
    charge_id: int,
    payload: ChargeStatusUpdate,
    session: Session = Depends(get_session),
):
    charge = charge_service.get_charge_or_404(session, charge_id)
    return charge_service.update_charge_status(session, charge, payload)
