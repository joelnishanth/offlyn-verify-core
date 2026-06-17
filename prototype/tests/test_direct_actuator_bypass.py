"""Tests proving that the actuator rejects commands without gate authorization.

This is the core architectural claim of the paper: the planner cannot talk
directly to the actuator.
"""

from gate.schemas import ActionRequest, ActuatorCommand
from gate.verify_core import VerifyCore
from actuator_sim.robot_arm_sim import RobotArmActuator


def test_no_token_rejected(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    """Command with no authorization token is rejected."""
    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )
    cmd = ActuatorCommand(action_request=request, authorization_token=None)
    result = actuator.execute(cmd)
    assert result is False
    assert actuator.last_reason == "no_authorization_token"


def test_forged_token_rejected(gate: VerifyCore, actuator: RobotArmActuator) -> None:
    """Command with a forged (invalid signature) token is rejected."""
    from gate.schemas import AuthorizationToken

    request = ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )

    forged_token = AuthorizationToken(
        action_hash=request.canonical_hash(),
        nonce=request.nonce,
        policy_hash="fake_policy_hash",
        signature="forged_signature_value",
    )

    cmd = ActuatorCommand(action_request=request, authorization_token=forged_token)
    result = actuator.execute(cmd)
    assert result is False
    assert actuator.last_reason == "token_signature_invalid"
