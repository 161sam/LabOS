"""ROS action/service dispatch — DELEGATES TO abrain_execution.

Any ROS service callback that represents a reactor command MUST call
`dispatch_ros_command` here. That builds an `ABrainExecuteRequest`
(source='ros_bridge', requested_via='ros') and hands it to
`abrain_execution.execute_action`, so Safety Guards, Role Checks,
Approval Gate and Trace Layer all still apply. ROS is NOT authorized
to execute commands directly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlmodel import Session

from ..schemas import (
    ABrainExecuteRequest,
    ABrainExecutionResult,
    UserRead,
)
from ..services import abrain_execution

ROS_SOURCE = 'ros_bridge'
ROS_REQUESTED_VIA = 'ros'


# Known LabOS command types that map 1:1 to ROS service names. This is a
# whitelist — unknown commands are rejected at the ROS boundary before
# they ever reach `abrain_execution`.
ROS_COMMAND_TYPES: frozenset[str] = frozenset(
    {
        'light_on',
        'light_off',
        'pump_on',
        'pump_off',
        'aeration_start',
        'aeration_stop',
        'sample_capture',
    }
)


@dataclass
class RosCommandDispatchResult:
    accepted: bool
    result: ABrainExecutionResult | None
    rejection_reason: str | None = None


def resolve_command_type_from_ros(command_type: str) -> str | None:
    if command_type in ROS_COMMAND_TYPES:
        return command_type
    return None


def dispatch_ros_command(
    session: Session,
    user: UserRead,
    *,
    reactor_id: int,
    command_type: str,
    params: dict[str, Any] | None = None,
    trace_id: str | None = None,
    reason: str | None = None,
    approve: bool = False,
) -> RosCommandDispatchResult:
    resolved = resolve_command_type_from_ros(command_type)
    if resolved is None:
        return RosCommandDispatchResult(
            accepted=False,
            result=None,
            rejection_reason=f'unknown_ros_command_type: {command_type}',
        )

    merged_params: dict[str, Any] = {'reactor_id': reactor_id, 'command_type': resolved}
    if params:
        for key, value in params.items():
            if key in {'reactor_id', 'command_type'}:
                continue
            merged_params[key] = value

    request = ABrainExecuteRequest(
        action='labos.create_reactor_command',
        params=merged_params,
        trace_id=trace_id,
        source=ROS_SOURCE,
        reason=reason,
        requested_via=ROS_REQUESTED_VIA,
        approve=approve,
    )
    result = abrain_execution.execute_action(session, request, user)
    return RosCommandDispatchResult(accepted=True, result=result)


__all__ = [
    'ROS_COMMAND_TYPES',
    'ROS_REQUESTED_VIA',
    'ROS_SOURCE',
    'RosCommandDispatchResult',
    'dispatch_ros_command',
    'resolve_command_type_from_ros',
]
