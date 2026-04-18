from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import UserAccount, _utcnow
from ..schemas import (
    AuthLoginRequest,
    UserActiveUpdate,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserRole,
    UserRoleUpdate,
    UserUpdate,
)
from ..security import hash_password, verify_password


def list_users(session: Session) -> list[UserRead]:
    users = list(session.exec(select(UserAccount).order_by(UserAccount.username.asc(), UserAccount.id.asc())).all())
    return [_to_user_read(user) for user in users]


def get_user_or_404(session: Session, user_id: int) -> UserAccount:
    user = session.get(UserAccount, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


def get_user_by_username(session: Session, username: str) -> UserAccount | None:
    normalized_username = username.strip().lower()
    return session.exec(select(UserAccount).where(UserAccount.username == normalized_username)).first()


def get_user_read(session: Session, user_id: int) -> UserRead:
    return _to_user_read(get_user_or_404(session, user_id))


def create_user(session: Session, payload: UserCreate) -> UserRead:
    _ensure_username_available(session, payload.username)
    user = UserAccount(
        username=payload.username,
        display_name=payload.display_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role.value,
        is_active=payload.is_active,
        auth_source='local',
        note=payload.note,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_user_read(user)


def update_user(session: Session, user: UserAccount, payload: UserUpdate) -> UserRead:
    _ensure_username_available(session, payload.username, exclude_id=user.id)
    _ensure_admin_not_removed(session, user, next_role=payload.role, next_is_active=payload.is_active)

    user.username = payload.username
    user.display_name = payload.display_name
    user.email = payload.email
    user.role = payload.role.value
    user.is_active = payload.is_active
    user.note = payload.note
    user.updated_at = _utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_user_read(user)


def update_user_role(session: Session, user: UserAccount, payload: UserRoleUpdate) -> UserRead:
    _ensure_admin_not_removed(session, user, next_role=payload.role, next_is_active=user.is_active)
    user.role = payload.role.value
    user.updated_at = _utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_user_read(user)


def update_user_active(session: Session, user: UserAccount, payload: UserActiveUpdate) -> UserRead:
    _ensure_admin_not_removed(session, user, next_role=UserRole(user.role), next_is_active=payload.is_active)
    user.is_active = payload.is_active
    user.updated_at = _utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_user_read(user)


def update_user_password(session: Session, user: UserAccount, payload: UserPasswordUpdate) -> UserRead:
    user.password_hash = hash_password(payload.password)
    user.updated_at = _utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_user_read(user)


def authenticate_user(session: Session, payload: AuthLoginRequest) -> UserAccount:
    user = get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User account is inactive')
    return user


def touch_last_login(session: Session, user: UserAccount) -> UserAccount:
    user.last_login_at = _utcnow()
    user.updated_at = _utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _to_user_read(user: UserAccount) -> UserRead:
    return UserRead(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        auth_source=user.auth_source,
        note=user.note,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
    )


def _ensure_username_available(session: Session, username: str, exclude_id: int | None = None) -> None:
    existing = get_user_by_username(session, username)
    if existing is None:
        return
    if exclude_id is not None and existing.id == exclude_id:
        return
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists')


def _ensure_admin_not_removed(
    session: Session,
    user: UserAccount,
    *,
    next_role: UserRole,
    next_is_active: bool,
) -> None:
    if user.role != UserRole.admin.value:
        return
    if next_role == UserRole.admin and next_is_active:
        return

    other_active_admins = list(
        session.exec(
            select(UserAccount.id).where(
                UserAccount.role == UserRole.admin.value,
                UserAccount.is_active.is_(True),
                UserAccount.id != user.id,
            )
        ).all()
    )
    if other_active_admins:
        return
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='At least one active admin must remain')
