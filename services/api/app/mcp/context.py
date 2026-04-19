"""Resource adapter for the LabOS MCP Server.

Exposes a small, curated set of MCP resources that map directly onto the
existing `abrain_context.build_adapter_context()` output. MCP resources
are read-only, JSON, and intentionally narrow — ABrain reads them
deterministically as context for planning.
"""

from __future__ import annotations

from typing import Any, Callable

from sqlmodel import Session

from ..services import abrain_context
from .schemas import MCPResourceDescriptor


_RESOURCES: list[tuple[str, str, str, str]] = [
    (
        'labos://overview',
        'LabOS Overview',
        'Aggregate summary: open tasks, alerts, online reactors, recent photos.',
        'summary',
    ),
    (
        'labos://reactors',
        'LabOS Reactors',
        'Reactor digital twins incl. per-reactor telemetry and health status.',
        'reactors',
    ),
    (
        'labos://operations',
        'LabOS Operations',
        'Overdue tasks, open safety incidents, blocked/failed commands.',
        'operations',
    ),
    (
        'labos://resources',
        'LabOS Resources',
        'Inventory signals, asset attention, offline device nodes.',
        'resources',
    ),
    (
        'labos://schedule',
        'LabOS Schedules',
        'Active schedules with next run and recent failed runs.',
        'schedule',
    ),
    (
        'labos://photos',
        'LabOS Recent Photos',
        'Recent photo observations with vision labels.',
        'photos',
    ),
]


def list_resources() -> list[MCPResourceDescriptor]:
    return [
        MCPResourceDescriptor(uri=uri, name=name, description=description)
        for (uri, name, description, _section) in _RESOURCES
    ]


def read_resource(session: Session, uri: str) -> dict[str, Any]:
    """Read a resource by URI; returns a JSON-serializable dict.

    Raises LookupError for unknown URIs so the server can map to a
    proper MCP error code.
    """

    section = _resolve_section(uri)
    if section is None:
        raise LookupError(f'unknown resource: {uri}')

    context = abrain_context.build_adapter_context(session)
    payload = context.model_dump(mode='json')

    extractors: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
        'summary': lambda p: {
            'generated_at': p.get('generated_at'),
            'summary': p.get('summary'),
        },
        'reactors': lambda p: {
            'generated_at': p.get('generated_at'),
            'reactors': p.get('reactors', []),
        },
        'operations': lambda p: {
            'generated_at': p.get('generated_at'),
            'operations': p.get('operations', {}),
        },
        'resources': lambda p: {
            'generated_at': p.get('generated_at'),
            'resources': p.get('resources', {}),
        },
        'schedule': lambda p: {
            'generated_at': p.get('generated_at'),
            'schedule': p.get('schedule', {}),
        },
        'photos': lambda p: {
            'generated_at': p.get('generated_at'),
            'photos': p.get('photos', []),
        },
    }
    return extractors[section](payload)


def _resolve_section(uri: str) -> str | None:
    for (resource_uri, _name, _description, section) in _RESOURCES:
        if resource_uri == uri:
            return section
    return None


__all__ = ['list_resources', 'read_resource']
