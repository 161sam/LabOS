from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from .config import settings
from .db import get_session
from .models import UserAccount
from .schemas import UserRead, UserRole
from .security import decode_auth_token
from .services import users as user_service


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> UserRead:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')

    payload = decode_auth_token(token)
    user_id = payload.get('sub')
    if not isinstance(user_id, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')

    user = session.get(UserAccount, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User account is inactive')
    return user_service.get_user_read(session, user.id)


def require_authenticated_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user


def require_operator_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    if current_user.role not in {UserRole.admin, UserRole.operator}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Operator role required')
    return current_user


def require_admin_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin role required')
    return current_user


def _extract_token(request: Request) -> str | None:
    authorization = request.headers.get('Authorization')
    if authorization and authorization.startswith('Bearer '):
        return authorization[7:].strip()
    return request.cookies.get(settings.auth_cookie_name)
