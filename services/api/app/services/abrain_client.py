"""ABrain Client V1.

Thin HTTP wrapper fuer das externe ABrain. LabOS bleibt bewusst an den
Rand: Request senden, Response annehmen oder als fallback markieren.
Keine Businesslogik, kein Planning, kein Tool-Dispatch hier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from ..config import settings


@dataclass(frozen=True)
class ABrainClientResult:
    success: bool
    payload: dict[str, Any] | None
    mode: str
    error: str | None = None
    trace_id: str | None = None


def is_enabled() -> bool:
    return settings.abrain_enabled


def mode() -> str:
    return settings.abrain_mode or 'auto'


def base_url() -> str:
    return settings.abrain_base_url.rstrip('/')


def ping() -> ABrainClientResult:
    if not is_enabled() or settings.abrain_use_stub or mode() == 'local':
        return ABrainClientResult(success=False, payload=None, mode='local', error='external-disabled')
    try:
        with httpx.Client(timeout=settings.abrain_timeout_seconds) as client:
            response = client.get(f'{base_url()}/healthz')
            response.raise_for_status()
        return ABrainClientResult(success=True, payload=response.json() if _is_json(response) else None, mode='external')
    except Exception as exc:
        return ABrainClientResult(success=False, payload=None, mode='external', error=str(exc))


def query(request_payload: dict[str, Any]) -> ABrainClientResult:
    if not is_enabled() or settings.abrain_use_stub or mode() == 'local':
        return ABrainClientResult(success=False, payload=None, mode='local', error='external-disabled')
    try:
        with httpx.Client(timeout=settings.abrain_timeout_seconds) as client:
            response = client.post(f'{base_url()}/query', json=request_payload)
            response.raise_for_status()
            data = response.json() if _is_json(response) else {}
        return ABrainClientResult(
            success=True,
            payload=data,
            mode='external',
            trace_id=str(data.get('trace_id')) if isinstance(data, dict) and data.get('trace_id') is not None else None,
        )
    except Exception as exc:
        return ABrainClientResult(success=False, payload=None, mode='external', error=str(exc))


def reason(reasoning_mode: str, request_payload: dict[str, Any]) -> ABrainClientResult:
    """Call the ABrain V2 LabOS reasoning surface for the given mode.

    Convention (matches `abrain.reason_labos_<mode>` MCP tool names):
    `POST {base_url}/reason/labos_{mode}` with a JSON lab_context body.
    """
    if not is_enabled() or settings.abrain_use_stub or mode() == 'local':
        return ABrainClientResult(success=False, payload=None, mode='local', error='external-disabled')
    try:
        url = f'{base_url()}/reason/labos_{reasoning_mode}'
        with httpx.Client(timeout=settings.abrain_timeout_seconds) as client:
            response = client.post(url, json=request_payload)
            response.raise_for_status()
            data = response.json() if _is_json(response) else {}
        return ABrainClientResult(
            success=True,
            payload=data if isinstance(data, dict) else None,
            mode='external',
            trace_id=str(data.get('trace_id')) if isinstance(data, dict) and data.get('trace_id') is not None else None,
        )
    except Exception as exc:
        return ABrainClientResult(success=False, payload=None, mode='external', error=str(exc))


def _is_json(response: httpx.Response) -> bool:
    content_type = response.headers.get('content-type', '')
    return 'application/json' in content_type
