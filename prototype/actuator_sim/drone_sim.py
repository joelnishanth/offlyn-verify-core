"""Drone actuator simulator.

Same security invariant as the robot arm: the actuator only executes commands
that carry a valid gate-issued authorization token.
"""

from __future__ import annotations

from gate.schemas import ActuatorCommand
from gate.verify_core import VerifyCore


class DroneActuator:
    """Simulated drone that only accepts gate-authorized commands."""

    def __init__(self, verify_core: VerifyCore):
        self._verify_core = verify_core
        self.last_result: str = ""
        self.last_reason: str = ""

    def execute(self, command: ActuatorCommand) -> bool:
        if command.authorization_token is None:
            self.last_result = "rejected"
            self.last_reason = "no_authorization_token"
            return False

        valid, reason = self._verify_core.validate_token(
            command.authorization_token,
            command.action_request.canonical_hash(),
        )

        if not valid:
            self.last_result = "rejected"
            self.last_reason = reason
            return False

        self.last_result = "executed"
        self.last_reason = "authorized"
        return True
