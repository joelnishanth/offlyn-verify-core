"""Tests proving that safe, policy-conforming actions are allowed."""

from gate.schemas import ActionRequest, ActuatorCommand, Decision
from gate.verify_core import VerifyCore
from actuator_sim.robot_arm_sim import RobotArmActuator


def test_safe_move_allowed(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW
    assert decision.reason == "within_policy_bounds"
    assert token is not None


def test_safe_move_actuator_executes(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 0, "speed": 0.3},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW

    cmd = ActuatorCommand(action_request=request, authorization_token=token)
    result = actuator.execute(cmd)
    assert result is True
    assert actuator.last_result == "executed"


def test_max_speed_boundary(gate: VerifyCore) -> None:
    """Speed exactly at the limit should be allowed."""
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.5},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, _ = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW


def test_angle_boundary(gate: VerifyCore) -> None:
    """Angle exactly at the limit should be allowed."""
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 90, "speed": 0.3},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, _ = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW


def test_gripper_action(gate: VerifyCore) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="gripper_open",
        target="gripper_1",
        parameters={"speed": 0.5},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, _ = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW
