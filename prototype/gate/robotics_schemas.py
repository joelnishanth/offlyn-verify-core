"""Robotics-specific action schema for ROS 2 integration.

Extends the base Verify Core schemas with rover-specific fields for
velocity commands, zone awareness, and human proximity detection.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RobotAction(str, Enum):
    MOVE = "move"
    STOP = "stop"
    TURN = "turn"
    EMERGENCY_STOP = "emergency_stop"


class Zone(str, Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    HUMAN_ZONE = "human_zone"
    LOADING_DOCK = "loading_dock"


class Position(BaseModel):
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0


class RoboticsActionRequest(BaseModel):
    """A proposed robot action submitted by the autonomy layer.

    This is the canonical input to the Verify Core policy gate for
    ROS 2 rover commands. The gate evaluates this against active policy
    before allowing publication to /cmd_vel.
    """

    robot_id: str = Field(min_length=1)
    action: RobotAction
    source: str = Field(min_length=1)

    linear_x: Optional[float] = Field(default=None, ge=-10.0, le=10.0)
    angular_z: Optional[float] = Field(default=None, ge=-6.28, le=6.28)

    zone: Zone = Zone.NORMAL
    human_nearby: bool = False

    mission_id: Optional[str] = None
    position: Optional[Position] = None
    timestamp: float = Field(default_factory=time.time)
    nonce: str = Field(default_factory=lambda: uuid.uuid4().hex)
    policy_epoch: int = Field(default=1, ge=1)

    @field_validator("linear_x")
    @classmethod
    def move_requires_linear_x(cls, v, info):
        return v

    def model_post_init(self, __context) -> None:
        if self.action == RobotAction.MOVE and self.linear_x is None:
            raise ValueError("linear_x is required for 'move' actions")
        if self.action == RobotAction.TURN and self.angular_z is None:
            raise ValueError("angular_z is required for 'turn' actions")

    def to_gate_request(self):
        """Convert to the base ActionRequest format for gate evaluation."""
        from gate.schemas import ActionRequest

        parameters = {}
        if self.linear_x is not None:
            parameters["speed"] = abs(self.linear_x)
            parameters["linear_x"] = self.linear_x
        if self.angular_z is not None:
            parameters["angular_z"] = self.angular_z

        context = {
            "zone": self.zone.value,
            "human_nearby": self.human_nearby,
        }
        if self.position:
            context["position"] = self.position.model_dump()

        return ActionRequest(
            actor=self.robot_id,
            action=self.action.value,
            target="cmd_vel",
            parameters=parameters,
            context=context,
            nonce=self.nonce,
            timestamp=self.timestamp,
            policy_epoch=self.policy_epoch,
        )
