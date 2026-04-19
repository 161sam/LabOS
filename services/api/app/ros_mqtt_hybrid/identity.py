"""Unified node identity across LabOS / MQTT / ROS.

One physical device (an ESP32, a Pi, a ROS node) should be
addressable by the same `node_id` everywhere. This module turns a
`DeviceNode` row into a `NodeIdentity` that fixes the ROS node name
and MQTT client id deterministically so the three systems agree on
who is who.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from sqlmodel import Session, select

from ..models import DeviceNode
from ..ros.ros_registry import build_ros_node_name


@dataclass(frozen=True)
class NodeIdentity:
    node_id: str
    ros_node: str
    mqtt_client_id: str
    reactor_id: int | None
    type: str


def identity_from_device_node(device: DeviceNode, *, prefix: str = 'labos') -> NodeIdentity:
    node_id = device.node_id or str(device.id or device.name)
    return NodeIdentity(
        node_id=node_id,
        ros_node=build_ros_node_name(device, prefix=prefix),
        mqtt_client_id=node_id,
        reactor_id=device.reactor_id,
        type=device.node_type,
    )


class IdentityRegistry:
    """Process-local cache. Refreshed on demand from the DeviceNode table.

    The registry is an optional accelerator for routing — DeviceNode
    remains the source of truth. Never write back into DB from here.
    """

    def __init__(self) -> None:
        self._by_node_id: dict[str, NodeIdentity] = {}
        self._by_ros_node: dict[str, NodeIdentity] = {}
        self._lock = Lock()

    def reload(self, session: Session, *, prefix: str = 'labos') -> None:
        devices = list(session.exec(select(DeviceNode)).all())
        by_node_id: dict[str, NodeIdentity] = {}
        by_ros: dict[str, NodeIdentity] = {}
        for device in devices:
            ident = identity_from_device_node(device, prefix=prefix)
            by_node_id[ident.node_id] = ident
            by_ros[ident.ros_node] = ident
        with self._lock:
            self._by_node_id = by_node_id
            self._by_ros_node = by_ros

    def get_by_node_id(self, node_id: str) -> NodeIdentity | None:
        with self._lock:
            return self._by_node_id.get(node_id)

    def get_by_ros_node(self, ros_node: str) -> NodeIdentity | None:
        with self._lock:
            return self._by_ros_node.get(ros_node)

    def all(self) -> list[NodeIdentity]:
        with self._lock:
            return list(self._by_node_id.values())


_registry = IdentityRegistry()


def get_identity_registry() -> IdentityRegistry:
    return _registry


__all__ = [
    'IdentityRegistry',
    'NodeIdentity',
    'get_identity_registry',
    'identity_from_device_node',
]
