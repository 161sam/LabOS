from datetime import timedelta

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from ..auth import require_authenticated_user
from ..config import settings
from ..db import get_session
from ..schemas import AuthLoginRequest, AuthLoginResponse, UserRead
from ..security import create_auth_token
from ..services import users as user_service

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=AuthLoginResponse)
def login(payload: AuthLoginRequest, response: Response, session: Session = Depends(get_session)):
    user = user_service.authenticate_user(session, payload)
    user = user_service.touch_last_login(session, user)
    access_token = create_auth_token(user_id=user.id, username=user.username, role=user.role)
    _set_auth_cookie(response, access_token)
    return AuthLoginResponse(access_token=access_token, user=user_service.get_user_read(session, user.id))


@router.get('/me', response_model=UserRead)
def me(current_user: UserRead = Depends(require_authenticated_user)):
    return current_user


@router.post('/logout')
def logout(response: Response):
    response.delete_cookie(settings.auth_cookie_name, path='/', httponly=True, samesite='lax')
    return {'status': 'ok'}


def _set_auth_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=access_token,
        max_age=int(timedelta(hours=settings.auth_token_ttl_hours).total_seconds()),
        httponly=True,
        samesite='lax',
        secure=settings.auth_cookie_secure,
        path='/',
    )
