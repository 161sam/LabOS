"""Unified topic / namespace mapping for the ROS + MQTT hybrid.

Single place where naming conventions for both transports are
collected. The intent is that any component that needs the "MQTT
topic for reactor N's temperature" and the matching "ROS topic for
reactor N's temperature" consults this module and nothing else —
otherwise the two worlds drift.

Canonical conventions:

- MQTT telemetry:  `labos/reactor/{id}/telemetry/{sensor_type}`
- ROS  telemetry:  `/labos/reactor/{id}/{sensor_type}`
- MQTT command:    `labos/reactor/{id}/control/{channel}`
- ROS  command:    `/labos/reactor/{id}/{command_type}`
"""
from __future__ import annotations

from dataclasses import dataclass

from ..config import settings
from ..ros import ros_topics as ros_topics_mod
from ..services import mqtt_topics as mqtt_topics_mod


@dataclass(frozen=True)
class HybridTopicMapping:
    mqtt_prefix: str
    ros_namespace: str

    def mqtt_telemetry_topic(self, *, reactor_id: int, sensor_type: str) -> str:
        prefix_parts = mqtt_topics_mod.normalize_topic_prefix(self.mqtt_prefix)
        return '/'.join([*prefix_parts, 'reactor', str(reactor_id), 'telemetry', sensor_type])

    def ros_telemetry_topic(self, *, reactor_id: int, sensor_type: str) -> str:
        return ros_topics_mod.build_ros_telemetry_topic(
            self.ros_namespace,
            reactor_id=reactor_id,
            sensor_type=sensor_type,
        )

    def mqtt_command_topic(self, *, reactor_id: int, command_type: str) -> str:
        return mqtt_topics_mod.build_control_topic(
            self.mqtt_prefix,
            reactor_id=reactor_id,
            command_type=command_type,
        )

    def ros_command_service(self, *, reactor_id: int, command_type: str) -> str:
        return ros_topics_mod.build_ros_command_service(
            self.ros_namespace,
            reactor_id=reactor_id,
            command_type=command_type,
        )

    def mqtt_to_ros_telemetry(self, mqtt_topic: str) -> str | None:
        return ros_topics_mod.mqtt_telemetry_to_ros(
            mqtt_topic,
            mqtt_prefix=self.mqtt_prefix,
            ros_namespace=self.ros_namespace,
        )

    def ros_to_mqtt_telemetry(self, ros_topic: str) -> str | None:
        return ros_topics_mod.ros_telemetry_to_mqtt(
            ros_topic,
            ros_namespace=self.ros_namespace,
            mqtt_prefix=self.mqtt_prefix,
        )


def default_mapping() -> HybridTopicMapping:
    return HybridTopicMapping(
        mqtt_prefix=settings.mqtt_topic_prefix,
        ros_namespace=settings.ros_namespace,
    )


def build_mqtt_telemetry_topic(reactor_id: int, sensor_type: str) -> str:
    return default_mapping().mqtt_telemetry_topic(
        reactor_id=reactor_id, sensor_type=sensor_type
    )


def build_mqtt_command_topic(reactor_id: int, command_type: str) -> str:
    return default_mapping().mqtt_command_topic(
        reactor_id=reactor_id, command_type=command_type
    )


__all__ = [
    'HybridTopicMapping',
    'build_mqtt_command_topic',
    'build_mqtt_telemetry_topic',
    'default_mapping',
]
