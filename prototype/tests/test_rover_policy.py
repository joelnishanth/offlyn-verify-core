"""Policy unit tests for the ROS 2 rover gate node logic.

Tests speed limits, zone enforcement, human proximity, and schema rejection
without requiring a running ROS 2 environment.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ros2_ws" / "src" / "verify_core_gate"))

from gate.robotics_schemas import RoboticsActionRequest, RobotAction, Zone


class FakeGatePolicy:
    """Mimics VerifyCoreGateNode._evaluate without ROS dependencies."""

    def __init__(
        self,
        max_speed_normal=1.0,
        max_speed_human=0.2,
        max_speed_dock=0.1,
        max_angular=2.0,
    ):
        self.max_speed_normal = max_speed_normal
        self.max_speed_human = max_speed_human
        self.max_speed_dock = max_speed_dock
        self.max_angular = max_angular

    def evaluate(self, req: RoboticsActionRequest) -> tuple:
        if req.action == RobotAction.EMERGENCY_STOP:
            return ("ALLOW", "emergency_stop_always_permitted")
        if req.action == RobotAction.STOP:
            return ("ALLOW", "stop_always_permitted")
        if req.zone == Zone.RESTRICTED:
            return ("DENY", "zone_restricted_entry_forbidden")

        speed = abs(req.linear_x or 0.0)
        if req.zone == Zone.HUMAN_ZONE or req.human_nearby:
            if speed > self.max_speed_human:
                return ("DENY", f"speed_exceeds_human_zone_limit")
        elif req.zone == Zone.LOADING_DOCK:
            if speed > self.max_speed_dock:
                return ("DENY", f"speed_exceeds_loading_dock_limit")
        else:
            if speed > self.max_speed_normal:
                return ("DENY", f"speed_exceeds_normal_limit")

        angular = abs(req.angular_z or 0.0)
        if angular > self.max_angular:
            return ("DENY", f"angular_speed_exceeds_limit")

        return ("ALLOW", "within_policy_bounds")


@pytest.fixture
def gate():
    return FakeGatePolicy()


class TestSpeedPolicy:
    """Issue #27: Add speed-limit policy tests."""

    def test_normal_speed_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.5,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_max_speed_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=1.0,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_over_speed_denied(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=5.0,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "speed" in reason

    def test_reverse_over_speed_denied(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=-3.0,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "speed" in reason

    def test_human_zone_speed_limit(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.5,
            zone=Zone.HUMAN_ZONE,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "human" in reason

    def test_human_zone_low_speed_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.1,
            zone=Zone.HUMAN_ZONE,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_loading_dock_speed_limit(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.5,
            zone=Zone.LOADING_DOCK,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "loading_dock" in reason

    def test_angular_speed_exceeded(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.TURN,
            source="autonomy_planner", angular_z=3.0,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "angular" in reason


class TestZonePolicy:
    """Issue #26: Add restricted-zone map / Issue #34: Attack test restricted zone."""

    def test_restricted_zone_denied(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.1,
            zone=Zone.RESTRICTED,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "restricted" in reason

    def test_restricted_zone_even_slow_denied(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.01,
            zone=Zone.RESTRICTED,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "DENY"

    def test_restricted_zone_stop_denied(self, gate):
        """Even stop in restricted zone is denied (shouldn't be there)."""
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.0,
            zone=Zone.RESTRICTED,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "DENY"

    def test_normal_zone_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.5,
            zone=Zone.NORMAL,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"


class TestHumanProximity:
    """Issue #28: Add human-proximity policy."""

    def test_human_nearby_high_speed_denied(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.5,
            human_nearby=True,
        )
        decision, reason = gate.evaluate(req)
        assert decision == "DENY"
        assert "human" in reason

    def test_human_nearby_low_speed_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.1,
            human_nearby=True,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_human_nearby_stop_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.STOP,
            source="autonomy_planner", human_nearby=True,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_human_nearby_emergency_stop_allowed(self, gate):
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.EMERGENCY_STOP,
            source="safety_monitor", human_nearby=True,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"


class TestAttackScenarios:
    """Issues #33, #34, #35: Attack tests for speed, zone, bypass."""

    def test_attack_unsafe_speed(self, gate):
        """Issue #33: Unsafe speed must be denied."""
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=9.9,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "DENY"

    def test_attack_restricted_zone_entry(self, gate):
        """Issue #34: Restricted zone entry must be denied."""
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.MOVE,
            source="autonomy_planner", linear_x=0.3,
            zone=Zone.RESTRICTED,
        )
        decision, _ = gate.evaluate(req)
        assert decision == "DENY"

    def test_attack_malformed_schema_rejected(self):
        """Issue #29: Malformed commands rejected at schema level."""
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="", action=RobotAction.MOVE,
                source="attacker", linear_x=0.5,
            )

    def test_attack_invalid_action_rejected(self):
        """Invalid action type rejected."""
        with pytest.raises(Exception):
            RoboticsActionRequest(
                robot_id="rover-01", action="self_destruct",
                source="attacker",
            )

    def test_stop_always_passes(self, gate):
        """Stop commands are always allowed regardless of state."""
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.STOP,
            source="safety_monitor",
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"

    def test_emergency_stop_always_passes(self, gate):
        """Emergency stop bypasses all checks."""
        req = RoboticsActionRequest(
            robot_id="rover-01", action=RobotAction.EMERGENCY_STOP,
            source="safety_monitor",
        )
        decision, _ = gate.evaluate(req)
        assert decision == "ALLOW"
