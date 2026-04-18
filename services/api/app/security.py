from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets
from typing import Any

from fastapi import HTTPException, status

from .config import settings

_PBKDF2_ALGORITHM = 'sha256'
_PBKDF2_ITERATIONS = 310000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM,
        password.encode('utf-8'),
        salt.encode('utf-8'),
        _PBKDF2_ITERATIONS,
    )
    return f'pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${base64.urlsafe_b64encode(derived).decode("ascii")}'


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt, encoded_hash = password_hash.split('$', 3)
    except ValueError:
        return False

    if algorithm != 'pbkdf2_sha256':
        return False

    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM,
        password.encode('utf-8'),
        salt.encode('utf-8'),
        int(iterations_str),
    )
    expected_hash = base64.urlsafe_b64encode(derived).decode('ascii')
    return hmac.compare_digest(expected_hash, encoded_hash)


def create_auth_token(*, user_id: int, username: str, role: str, ttl_hours: int | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours or settings.auth_token_ttl_hours)
    payload = {
        'sub': user_id,
        'username': username,
        'role': role,
        'exp': int(expires_at.timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_segment = _b64encode(payload_bytes)
    signature_segment = _sign(payload_segment.encode('ascii'))
    return f'{payload_segment}.{signature_segment}'


def decode_auth_token(token: str) -> dict[str, Any]:
    try:
        payload_segment, signature_segment = token.split('.', 1)
    except ValueError as exc:
        raise _unauthorized('Invalid authentication token') from exc

    expected_signature = _sign(payload_segment.encode('ascii'))
    if not hmac.compare_digest(expected_signature, signature_segment):
        raise _unauthorized('Invalid authentication token')

    try:
        payload_bytes = _b64decode(payload_segment)
        payload = json.loads(payload_bytes)
    except (json.JSONDecodeError, ValueError) as exc:
        raise _unauthorized('Invalid authentication token') from exc

    if not isinstance(payload, dict):
        raise _unauthorized('Invalid authentication token')

    exp = payload.get('exp')
    if not isinstance(exp, int):
        raise _unauthorized('Invalid authentication token')

    if datetime.now(timezone.utc).timestamp() > exp:
        raise _unauthorized('Authentication token expired')

    return payload


def _sign(value: bytes) -> str:
    digest = hmac.new(settings.auth_secret_key.encode('utf-8'), value, hashlib.sha256).digest()
    return _b64encode(digest)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode('ascii').rstrip('=')


def _b64decode(value: str) -> bytes:
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode(f'{value}{padding}'.encode('ascii'))


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
