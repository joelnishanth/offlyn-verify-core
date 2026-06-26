"""Tests for the robotics action schema validation."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gate.robotics_schemas import (
    Position,
    RobotAction,
    RoboticsActionRequest,
    Zone,
)


class TestValidActions:
    def test_move_forward(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.MOVE,
            source="autonomy_planner",
            linear_x=0.4,
            angular_z=0.0,
            zone=Zone.NORMAL,
            human_nearby=False,
        )
        assert action.action == RobotAction.MOVE
        assert action.linear_x == 0.4
        assert action.zone == Zone.NORMAL

    def test_turn(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.TURN,
            source="autonomy_planner",
            angular_z=1.0,
        )
        assert action.action == RobotAction.TURN
        assert action.angular_z == 1.0

    def test_stop(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.STOP,
            source="autonomy_planner",
        )
        assert action.action == RobotAction.STOP

    def test_emergency_stop(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.EMERGENCY_STOP,
            source="safety_monitor",
            human_nearby=True,
            zone=Zone.HUMAN_ZONE,
        )
        assert action.action == RobotAction.EMERGENCY_STOP
        assert action.human_nearby is True

    def test_move_with_position(self):
        action = RoboticsActionRequest(
            robot_id="rover-02",
            action=RobotAction.MOVE,
            source="teleop",
            linear_x=0.1,
            position=Position(x=5.0, y=3.2, heading=1.57),
        )
        assert action.position.x == 5.0
        assert action.position.heading == 1.57

    def test_nonce_auto_generated(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.STOP,
            source="autonomy_planner",
        )
        assert len(action.nonce) >= 8


class TestInvalidActions:
    def test_missing_robot_id(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="",
                action=RobotAction.MOVE,
                source="autonomy_planner",
                linear_x=0.5,
            )

    def test_missing_source(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.MOVE,
                source="",
                linear_x=0.5,
            )

    def test_invalid_action_type(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01",
                action="fly",
                source="autonomy_planner",
            )

    def test_move_missing_linear_x(self):
        with pytest.raises(ValueError, match="linear_x is required"):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.MOVE,
                source="autonomy_planner",
            )

    def test_turn_missing_angular_z(self):
        with pytest.raises(ValueError, match="angular_z is required"):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.TURN,
                source="autonomy_planner",
            )

    def test_speed_out_of_range(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.MOVE,
                source="autonomy_planner",
                linear_x=15.0,
            )

    def test_angular_out_of_range(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.TURN,
                source="autonomy_planner",
                angular_z=10.0,
            )

    def test_invalid_zone(self):
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01",
                action=RobotAction.STOP,
                source="autonomy_planner",
                zone="secret_tunnel",
            )


class TestConversion:
    def test_to_gate_request_move(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.MOVE,
            source="autonomy_planner",
            linear_x=0.4,
            zone=Zone.NORMAL,
            human_nearby=False,
            policy_epoch=1,
        )
        gate_req = action.to_gate_request()
        assert gate_req.actor == "rover-01"
        assert gate_req.action == "move"
        assert gate_req.target == "cmd_vel"
        assert gate_req.parameters["speed"] == 0.4
        assert gate_req.context["zone"] == "normal"
        assert gate_req.context["human_nearby"] is False
        assert gate_req.policy_epoch == 1

    def test_to_gate_request_with_position(self):
        action = RoboticsActionRequest(
            robot_id="rover-01",
            action=RobotAction.MOVE,
            source="autonomy_planner",
            linear_x=0.2,
            position=Position(x=1.0, y=2.0, heading=0.5),
        )
        gate_req = action.to_gate_request()
        assert gate_req.context["position"]["x"] == 1.0
        assert gate_req.context["position"]["y"] == 2.0


class TestJsonSchemaExamples:
    """Validate that JSON example files parse correctly."""

    SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"

    def _load_valid_examples(self):
        valid_dir = self.SCHEMA_DIR / "examples" / "valid"
        return list(valid_dir.glob("*.json"))

    def _load_invalid_examples(self):
        invalid_dir = self.SCHEMA_DIR / "examples" / "invalid"
        return list(invalid_dir.glob("*.json"))

    def test_valid_examples_exist(self):
        examples = self._load_valid_examples()
        assert len(examples) >= 5, f"Expected at least 5 valid examples, found {len(examples)}"

    def test_invalid_examples_exist(self):
        examples = self._load_invalid_examples()
        assert len(examples) >= 5, f"Expected at least 5 invalid examples, found {len(examples)}"

    @pytest.mark.parametrize("example_file", [
        "move_forward.json",
        "turn_left.json",
        "stop_command.json",
        "emergency_stop.json",
        "move_slow_human_zone.json",
        "move_loading_dock.json",
    ])
    def test_valid_example_parses(self, example_file):
        path = self.SCHEMA_DIR / "examples" / "valid" / example_file
        data = json.loads(path.read_text())
        action = RoboticsActionRequest(**data)
        assert action.robot_id
        assert action.source
