from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..auth import require_admin_user
from ..db import get_session
from ..schemas import (
    UserActiveUpdate,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserRoleUpdate,
    UserUpdate,
)
from ..services import users as user_service

router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(require_admin_user)],
)


@router.get('', response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    return user_service.list_users(session)


@router.post('', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    return user_service.create_user(session, payload)


@router.put('/{user_id}', response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_session)):
    user = user_service.get_user_or_404(session, user_id)
    return user_service.update_user(session, user, payload)


@router.patch('/{user_id}/active', response_model=UserRead)
def update_user_active(user_id: int, payload: UserActiveUpdate, session: Session = Depends(get_session)):
    user = user_service.get_user_or_404(session, user_id)
    return user_service.update_user_active(session, user, payload)


@router.patch('/{user_id}/role', response_model=UserRead)
def update_user_role(user_id: int, payload: UserRoleUpdate, session: Session = Depends(get_session)):
    user = user_service.get_user_or_404(session, user_id)
    return user_service.update_user_role(session, user, payload)


@router.patch('/{user_id}/password', response_model=UserRead)
def update_user_password(user_id: int, payload: UserPasswordUpdate, session: Session = Depends(get_session)):
    user = user_service.get_user_or_404(session, user_id)
    return user_service.update_user_password(session, user, payload)
