"""Tests proving that replayed authorization tokens are rejected."""

import time

from gate.schemas import ActionRequest, ActuatorCommand, Decision
from gate.verify_core import VerifyCore
from actuator_sim.robot_arm_sim import RobotArmActuator


def test_replayed_token_rejected(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW

    # First use — should succeed
    cmd = ActuatorCommand(action_request=request, authorization_token=token)
    assert actuator.execute(cmd) is True

    # Replay — same token reused — must fail
    cmd_replay = ActuatorCommand(action_request=request, authorization_token=token)
    assert actuator.execute(cmd_replay) is False
    assert actuator.last_reason == "token_replayed"


def test_expired_token_rejected(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW

    # Force expiration
    token.expires_at = time.time() - 10

    cmd = ActuatorCommand(action_request=request, authorization_token=token)
    assert actuator.execute(cmd) is False
    assert actuator.last_reason == "token_expired"


def test_token_action_hash_mismatch(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    """Token issued for one action cannot be used for a different action."""
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    decision, token = gate.evaluate(request)
    assert decision.decision == Decision.ALLOW

    # Different action request
    different_request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 80, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )

    cmd = ActuatorCommand(action_request=different_request, authorization_token=token)
    assert actuator.execute(cmd) is False
    assert actuator.last_reason == "action_hash_mismatch"
