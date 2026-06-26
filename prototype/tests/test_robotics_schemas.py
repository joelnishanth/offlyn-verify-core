"""Tests for Phase 1 robotics action schema validation."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from gate.robotics_schemas import RoboticsAction, RoboticsActionType

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas" / "examples"


@pytest.mark.parametrize(
    "filename",
    [
        "move_normal.json",
        "stop.json",
        "turn.json",
        "emergency_stop.json",
        "move_slow_near_human.json",
    ],
)
def test_valid_examples_parse(filename: str) -> None:
    data = json.loads((SCHEMAS_DIR / "valid" / filename).read_text())
    action = RoboticsAction.model_validate(data)
    assert action.robot_id
    assert action.action in RoboticsActionType


@pytest.mark.parametrize(
    "filename",
    [
        "missing_robot_id.json",
        "missing_source.json",
        "move_missing_linear_x.json",
        "invalid_action_type.json",
        "speed_out_of_range.json",
        "turn_missing_angular_z.json",
    ],
)
def test_invalid_examples_rejected(filename: str) -> None:
    data = json.loads((SCHEMAS_DIR / "invalid" / filename).read_text())
    with pytest.raises(ValidationError):
        RoboticsAction.model_validate(data)
