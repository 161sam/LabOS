"""JSON-RPC 2.0 core for the LabOS MCP Server.

Handles a narrow set of MCP methods:

  - initialize
  - tools/list
  - tools/call
  - resources/list
  - resources/read

All business logic lives in `tools.py`, `context.py`, and the underlying
`abrain_*` services. This module only does dispatch + JSON-RPC framing.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError
from sqlmodel import Session

from ..schemas import UserRead, UserRole
from . import context as mcp_context
from . import tools as mcp_tools
from .schemas import (
    ERROR_FORBIDDEN,
    ERROR_INTERNAL,
    ERROR_INVALID_PARAMS,
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_NOT_FOUND,
    MCPError,
    MCPRequest,
    MCPResponse,
    MCPToolCall,
)


_PROTOCOL_VERSION = '2025-03-26'
_SERVER_INFO = {
    'name': 'labos-mcp',
    'version': '1.0.0',
}
_CAPABILITIES = {
    'tools': {'listChanged': False},
    'resources': {'listChanged': False, 'subscribe': False},
}


def handle(session: Session, user: UserRead, raw: dict[str, Any]) -> MCPResponse:
    """Dispatch a single JSON-RPC request.

    Never raises for normal error paths — it encodes them as MCPResponse
    with an `error` field. Unexpected exceptions are wrapped as
    ERROR_INTERNAL so the transport layer can still return HTTP 200.
    """

    request_id = raw.get('id') if isinstance(raw, dict) else None
    try:
        request = MCPRequest.model_validate(raw)
    except ValidationError as exc:
        return _error(request_id, ERROR_INVALID_REQUEST, 'Invalid JSON-RPC request', {'errors': exc.errors()})

    request_id = request.id
    method = request.method
    params = request.params or {}

    try:
        if method == 'initialize':
            return _ok(request_id, _handle_initialize(params))
        if method == 'tools/list':
            return _ok(request_id, _handle_tools_list())
        if method == 'tools/call':
            return _handle_tools_call(request_id, session, user, params)
        if method == 'resources/list':
            return _ok(request_id, _handle_resources_list())
        if method == 'resources/read':
            return _handle_resources_read(request_id, session, params)
    except ValidationError as exc:
        return _error(request_id, ERROR_INVALID_PARAMS, 'Invalid params', {'errors': exc.errors()})
    except Exception as exc:  # noqa: BLE001 — boundary; surfaced as JSON-RPC error
        return _error(request_id, ERROR_INTERNAL, f'Internal error: {exc.__class__.__name__}')

    return _error(request_id, ERROR_METHOD_NOT_FOUND, f'Unknown method: {method}')


def _handle_initialize(_params: dict[str, Any]) -> dict[str, Any]:
    return {
        'protocolVersion': _PROTOCOL_VERSION,
        'serverInfo': _SERVER_INFO,
        'capabilities': _CAPABILITIES,
    }


def _handle_tools_list() -> dict[str, Any]:
    return {
        'tools': [tool.model_dump() for tool in mcp_tools.list_tools()],
    }


def _handle_tools_call(
    request_id: int | str | None,
    session: Session,
    user: UserRead,
    params: dict[str, Any],
) -> MCPResponse:
    call = MCPToolCall.model_validate(params)
    try:
        result = mcp_tools.call_tool(
            session,
            user=user,
            name=call.name,
            arguments=call.arguments,
            trace_id=call.trace_id,
            reason=call.reason,
            approve=call.approve,
        )
    except PermissionError as exc:
        return _error(request_id, ERROR_FORBIDDEN, str(exc))
    except LookupError as exc:
        return _error(request_id, ERROR_NOT_FOUND, str(exc))

    payload = result.model_dump(mode='json')
    is_error = result.status.value in {'blocked', 'failed', 'rejected'}
    return _ok(
        request_id,
        {
            'isError': is_error,
            'content': [{'type': 'json', 'data': payload}],
            'structuredContent': payload,
        },
    )


def _handle_resources_list() -> dict[str, Any]:
    return {
        'resources': [res.model_dump() for res in mcp_context.list_resources()],
    }


def _handle_resources_read(
    request_id: int | str | None,
    session: Session,
    params: dict[str, Any],
) -> MCPResponse:
    uri = params.get('uri')
    if not isinstance(uri, str) or not uri:
        return _error(request_id, ERROR_INVALID_PARAMS, 'uri is required')
    try:
        data = mcp_context.read_resource(session, uri)
    except LookupError as exc:
        return _error(request_id, ERROR_NOT_FOUND, str(exc))
    return _ok(
        request_id,
        {'contents': [{'uri': uri, 'mimeType': 'application/json', 'json': data}]},
    )


def _ok(request_id: int | str | None, result: dict[str, Any]) -> MCPResponse:
    return MCPResponse(id=request_id, result=result)


def _error(
    request_id: int | str | None,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
) -> MCPResponse:
    return MCPResponse(id=request_id, error=MCPError(code=code, message=message, data=data))


# UserRole import kept so linters see the dependency even though role checks
# live inside tools.call_tool now.
_ = UserRole

__all__ = ['handle']
