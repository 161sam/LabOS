"""Tool catalog for the LabOS MCP Server.

The catalog is strictly derived from `abrain_actions._ACTIONS` and
`abrain_execution.ACTION_MAP` — no dynamic discovery, no extra tools. If
an action descriptor is not also present in `ACTION_MAP`, it is skipped
(there is no way to execute it, so we do not advertise it).

Input schemas are hand-authored per tool. We keep them narrow and
consistent with the existing LabOS request schemas so that ABrain can
validate on its side before even calling `tools/call`.
"""

from __future__ import annotations

from typing import Any

from sqlmodel import Session

from ..schemas import (
    ABrainActionDescriptor,
    ABrainExecuteRequest,
    ABrainExecutionResult,
    UserRead,
    UserRole,
)
from ..services import abrain_actions, abrain_execution
from .schemas import MCPToolDefinition


def _tool_input_schema(action: ABrainActionDescriptor) -> dict[str, Any]:
    """Convert the action's informal argument hints into a JSON Schema."""

    hand_authored: dict[str, dict[str, Any]] = {
        'labos.create_task': {
            'type': 'object',
            'additionalProperties': True,
            'required': ['title'],
            'properties': {
                'title': {'type': 'string', 'minLength': 1, 'maxLength': 200},
                'description': {'type': 'string'},
                'priority': {'type': 'string', 'enum': ['low', 'normal', 'high', 'critical']},
                'due_at': {'type': 'string', 'format': 'date-time'},
                'charge_id': {'type': 'integer'},
                'reactor_id': {'type': 'integer'},
                'asset_id': {'type': 'integer'},
            },
        },
        'labos.create_alert': {
            'type': 'object',
            'additionalProperties': True,
            'required': ['title', 'message'],
            'properties': {
                'title': {'type': 'string', 'minLength': 1, 'maxLength': 200},
                'message': {'type': 'string', 'minLength': 1},
                'severity': {'type': 'string', 'enum': ['info', 'warning', 'high', 'critical']},
                'source_type': {'type': 'string', 'enum': ['sensor', 'charge', 'reactor', 'manual']},
                'source_id': {'type': 'integer'},
            },
        },
        'labos.create_reactor_command': {
            'type': 'object',
            'additionalProperties': True,
            'required': ['reactor_id', 'command_type'],
            'properties': {
                'reactor_id': {'type': 'integer'},
                'command_type': {
                    'type': 'string',
                    'enum': [
                        'light_on', 'light_off',
                        'pump_on', 'pump_off',
                        'aeration_on', 'aeration_off',
                        'sample_capture',
                    ],
                },
                'channel': {'type': 'string'},
                'params': {'type': 'object', 'additionalProperties': True},
            },
        },
        'labos.retry_reactor_command': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['command_id'],
            'properties': {'command_id': {'type': 'integer'}},
        },
        'labos.ack_safety_incident': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['incident_id'],
            'properties': {
                'incident_id': {'type': 'integer'},
                'note': {'type': 'string'},
            },
        },
    }
    if action.name in hand_authored:
        return hand_authored[action.name]
    # Generic fallback: permissive object with the declared keys.
    return {
        'type': 'object',
        'additionalProperties': True,
        'properties': {key: {'description': hint} for key, hint in (action.arguments or {}).items()},
    }


def list_tools() -> list[MCPToolDefinition]:
    catalog = abrain_actions.get_catalog()
    exposed: list[MCPToolDefinition] = []
    for action in catalog.actions:
        if action.name not in abrain_execution.ACTION_MAP:
            # No static executor -> never exposed as an MCP tool.
            continue
        exposed.append(
            MCPToolDefinition(
                name=action.name,
                description=action.description,
                inputSchema=_tool_input_schema(action),
                annotations={
                    'domain': action.domain.value,
                    'risk_level': action.risk_level.value,
                    'requires_approval': action.requires_approval,
                    'allowed_roles': list(action.allowed_roles or []),
                    'guarded_by': list(action.guarded_by or []),
                },
            )
        )
    return exposed


def call_tool(
    session: Session,
    *,
    user: UserRead,
    name: str,
    arguments: dict[str, Any],
    trace_id: str | None,
    reason: str | None,
    approve: bool,
) -> ABrainExecutionResult:
    """Route an MCP tools/call to `abrain_execution.execute_action`.

    The MCP layer intentionally does NO role-check of its own here —
    `abrain_execution.execute_action` + the action catalog are authoritative.
    We only forbid viewers from calling any tool; read-only access goes
    through `resources/read`.
    """

    if user.role == UserRole.viewer:
        raise PermissionError('viewers cannot execute tools')

    if name not in abrain_execution.ACTION_MAP:
        raise LookupError(f'unknown tool: {name}')

    payload = ABrainExecuteRequest(
        action=name,
        params=dict(arguments or {}),
        trace_id=trace_id,
        source='mcp',
        reason=reason,
        requested_via='mcp',
        approve=bool(approve),
    )
    return abrain_execution.execute_action(session, payload, user)


__all__ = ['list_tools', 'call_tool']
