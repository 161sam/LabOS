"""ROS2 Compatibility Layer — TRANSPORT + MAPPING ONLY.

Boundary Hardening V1 applies here just like it does to the MQTT
bridge: the ROS layer is an *additional* transport adapter for
telemetry, device-node status and reactor commands. It contains NO
interpretation, decision or autonomy logic:

- Outgoing telemetry/state is mirrored verbatim to the ROS topic tree,
- Incoming commands are translated into `ABrainExecuteRequest`s and
  dispatched through `abrain_execution.execute_action` — so Safety
  Guards, Role Checks, Approval Gate and Trace Layer all still apply,
- The bridge does NOT replace MQTT; both run in parallel.
"""

from .ros_topics import (
    RosCommandMatch,
    RosNodeMatch,
    RosTelemetryMatch,
    build_ros_command_service,
    build_ros_namespace,
    build_ros_node_topic,
    build_ros_telemetry_topic,
    mqtt_telemetry_to_ros,
    parse_ros_command_service,
    parse_ros_telemetry_topic,
    ros_telemetry_to_mqtt,
)
from .ros_actions import (
    RosCommandDispatchResult,
    dispatch_ros_command,
    resolve_command_type_from_ros,
)
from .ros_registry import (
    build_ros_node_name,
    list_ros_nodes,
    resolve_device_node_by_ros_name,
)
from .ros_bridge import RosBridge, get_ros_bridge

__all__ = [
    'RosBridge',
    'RosCommandDispatchResult',
    'RosCommandMatch',
    'RosNodeMatch',
    'RosTelemetryMatch',
    'build_ros_command_service',
    'build_ros_namespace',
    'build_ros_node_name',
    'build_ros_node_topic',
    'build_ros_telemetry_topic',
    'dispatch_ros_command',
    'get_ros_bridge',
    'list_ros_nodes',
    'mqtt_telemetry_to_ros',
    'parse_ros_command_service',
    'parse_ros_telemetry_topic',
    'resolve_command_type_from_ros',
    'resolve_device_node_by_ros_name',
    'ros_telemetry_to_mqtt',
]
