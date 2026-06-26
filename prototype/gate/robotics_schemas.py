"""Pydantic model for Phase 1 ROS 2 robotics action schema."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RoboticsActionType(str, Enum):
    MOVE = "move"
    STOP = "stop"
    TURN = "turn"
    EMERGENCY_STOP = "emergency_stop"


class ZoneType(str, Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    HUMAN_ZONE = "human_zone"


class RoboticsAction(BaseModel):
    """Structured robot action for Verify Core policy evaluation."""

    robot_id: str = Field(min_length=1)
    action: RoboticsActionType
    source: str = Field(min_length=1)
    mission_id: str | None = None
    linear_x: float | None = Field(default=None, ge=-2.0, le=2.0)
    angular_z: float | None = Field(default=None, ge=-3.14, le=3.14)
    zone: ZoneType | None = None
    human_nearby: bool | None = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_action_params(self) -> RoboticsAction:
        if self.action == RoboticsActionType.MOVE:
            if self.linear_x is None or self.angular_z is None:
                raise ValueError("move requires linear_x and angular_z")
        elif self.action == RoboticsActionType.TURN:
            if self.angular_z is None:
                raise ValueError("turn requires angular_z")
        return self
