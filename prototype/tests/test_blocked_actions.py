"""Tests proving that unsafe actions are denied by the Verify Core gate."""

from gate.schemas import ActionRequest, Decision
from gate.verify_core import VerifyCore


def test_speed_violation_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 30, "speed": 1.2},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "speed_exceeds_limit"
    assert token is None


def test_angle_out_of_range_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 120, "speed": 0.3},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "angle_out_of_range"
    assert token is None


def test_negative_angle_out_of_range_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": -100, "speed": 0.3},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "angle_out_of_range"


def test_forbidden_zone_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.2},
        context={"zone": "restricted_zone_x", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "zone_not_allowed"
    assert token is None


def test_human_nearby_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.2},
        context={"zone": "safe_area_a", "human_nearby": True},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "human_nearby_movement_denied"
    assert token is None


def test_unknown_actor_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="rogue_planner_99",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.2},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, _ = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "actor_not_authorized"


def test_unknown_action_denied(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="self_destruct",
        target="joint_2",
        parameters={},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, _ = gate.evaluate(request)
    assert decision.decision == Decision.DENY
    assert decision.reason == "no_matching_rule"
