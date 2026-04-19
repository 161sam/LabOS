"""ROS2 bridge — TRANSPORT ONLY.

Boundary Hardening V1: mirrors the design of `mqtt_bridge` but for
ROS2. The rclpy dependency is optional — in dev/CI environments where
rclpy is not available, the bridge degrades to a stub that records its
status and does not attempt to spin a node. This is intentional so the
main API process starts cleanly everywhere.

Inbound ROS service callbacks must route through
`ros_actions.dispatch_ros_command`, which itself calls
`abrain_execution.execute_action`. The bridge does NOT execute
commands directly.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock

from ..config import settings

try:  # pragma: no cover - optional runtime dependency
    import rclpy  # type: ignore
except ImportError:  # pragma: no cover - exercised via status checks in dev/CI
    rclpy = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class RosBridgeStatus:
    enabled: bool
    dependency_available: bool
    running: bool
    node_name: str
    namespace: str
    last_event_at: datetime | None
    last_error: str | None


class RosBridge:
    """Minimal ROS bridge scaffold. Starts a rclpy context + node when
    the dependency is available and `settings.ros_enabled` is true;
    otherwise it stays dormant and reports its status."""

    def __init__(self) -> None:
        self._context = None
        self._node = None
        self._started = False
        self._running = False
        self._last_event_at: datetime | None = None
        self._last_error: str | None = None
        self._lock = Lock()

    @property
    def dependency_available(self) -> bool:
        return rclpy is not None

    def start(self) -> None:
        if not settings.ros_enabled:
            logger.info('ROS bridge disabled by configuration')
            return
        if rclpy is None:
            self._set_last_error('rclpy dependency not installed')
            logger.warning('ROS bridge disabled because rclpy is not available')
            return
        with self._lock:
            if self._started:
                return
            try:  # pragma: no cover - runtime only; rclpy not present in CI
                context = rclpy.Context()
                rclpy.init(context=context)
                node = rclpy.create_node(
                    settings.ros_node_name,
                    namespace=settings.ros_namespace,
                    context=context,
                )
                self._context = context
                self._node = node
                self._started = True
                self._running = True
                self._last_error = None
                logger.info(
                    'ROS bridge started as %s in namespace %s',
                    settings.ros_node_name,
                    settings.ros_namespace,
                )
            except Exception as exc:  # pragma: no cover - depends on runtime
                self._set_last_error(f'Failed to start ROS bridge: {exc}')
                logger.warning('ROS bridge start failed: %s', exc)
                self._context = None
                self._node = None
                self._started = False
                self._running = False

    def stop(self) -> None:
        with self._lock:
            node = self._node
            context = self._context
            self._node = None
            self._context = None
            self._started = False
            self._running = False
        if rclpy is None:
            return
        try:  # pragma: no cover - runtime only
            if node is not None:
                node.destroy_node()
            if context is not None:
                rclpy.shutdown(context=context)
        except Exception as exc:  # pragma: no cover - best effort during shutdown
            logger.warning('ROS bridge stop encountered an error: %s', exc)

    def status(self) -> RosBridgeStatus:
        return RosBridgeStatus(
            enabled=settings.ros_enabled,
            dependency_available=self.dependency_available,
            running=self._running,
            node_name=settings.ros_node_name,
            namespace=settings.ros_namespace,
            last_event_at=self._last_event_at,
            last_error=self._last_error,
        )

    def mark_event(self) -> None:
        self._last_event_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def _set_last_error(self, message: str) -> None:
        self._last_error = message


_ros_bridge = RosBridge()


def get_ros_bridge() -> RosBridge:
    return _ros_bridge


__all__ = ['RosBridge', 'RosBridgeStatus', 'get_ros_bridge']
