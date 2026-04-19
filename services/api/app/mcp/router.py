"""HTTP transport for the LabOS MCP Server.

Exposes a single JSON-RPC endpoint `POST /api/v1/mcp` plus two optional
GET helpers for debugging / human inspection.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session

from ..auth import get_current_user, require_authenticated_user
from ..config import settings
from ..db import get_session
from ..schemas import UserRead
from . import context as mcp_context
from . import server as mcp_server
from . import tools as mcp_tools

router = APIRouter(
    prefix='/mcp',
    tags=['mcp'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post('')
def mcp_rpc(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='MCP server disabled',
        )
    response = mcp_server.handle(session, current_user, payload)
    return response.model_dump(exclude_none=True)


@router.get('/tools')
def mcp_list_tools():
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='MCP server disabled',
        )
    return {'tools': [tool.model_dump() for tool in mcp_tools.list_tools()]}


@router.get('/resources')
def mcp_list_resources():
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='MCP server disabled',
        )
    return {'resources': [res.model_dump() for res in mcp_context.list_resources()]}
