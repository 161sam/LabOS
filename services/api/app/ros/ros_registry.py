"""ROS node registry mapping — DeviceNode ↔ ROS Node name.

Pure lookup / naming. Does NOT create rows; DeviceNode inserts stay
owned by `reactor_control.upsert_device_node_by_node_id`, which the
MQTT bridge and any future ROS-side sync will both go through.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from sqlmodel import Session, select

from ..models import DeviceNode


_NAMESPACE_SAFE = re.compile(r'[^a-zA-Z0-9_]+')


def _sanitize(value: str) -> str:
    cleaned = _NAMESPACE_SAFE.sub('_', value).strip('_')
    return cleaned or 'node'


def build_ros_node_name(device: DeviceNode, *, prefix: str = 'labos') -> str:
    base = device.node_id or device.name
    slug = _sanitize(base)
    return f'{_sanitize(prefix)}_node_{device.id or 0}_{slug}'


def resolve_device_node_by_ros_name(
    session: Session,
    ros_name: str,
    *,
    prefix: str = 'labos',
) -> DeviceNode | None:
    marker = f'{_sanitize(prefix)}_node_'
    if not ros_name.startswith(marker):
        return None
    rest = ros_name[len(marker) :]
    id_part, _, _ = rest.partition('_')
    if not id_part.isdigit():
        return None
    return session.get(DeviceNode, int(id_part))


@dataclass(frozen=True)
class RosNodeEntry:
    device_id: int
    node_id: str | None
    name: str
    node_type: str
    ros_node_name: str
    status: str
    reactor_id: int | None


def list_ros_nodes(session: Session, *, prefix: str = 'labos') -> list[RosNodeEntry]:
    devices = list(session.exec(select(DeviceNode).order_by(DeviceNode.id)).all())
    entries: list[RosNodeEntry] = []
    for device in devices:
        if device.id is None:
            continue
        entries.append(
            RosNodeEntry(
                device_id=device.id,
                node_id=device.node_id,
                name=device.name,
                node_type=device.node_type,
                ros_node_name=build_ros_node_name(device, prefix=prefix),
                status=device.status,
                reactor_id=device.reactor_id,
            )
        )
    return entries


__all__ = [
    'RosNodeEntry',
    'build_ros_node_name',
    'list_ros_nodes',
    'resolve_device_node_by_ros_name',
]
