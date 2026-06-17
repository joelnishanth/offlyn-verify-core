"""Robot arm actuator simulator.

KEY INVARIANT: The actuator refuses any command that does not carry a valid
authorization token from the Verify Core gate.  This is the architectural
enforcement of the actuation boundary — the planner cannot talk directly
to the actuator.
"""

from __future__ import annotations

from gate.schemas import ActuatorCommand, Decision
from gate.verify_core import VerifyCore


class RobotArmActuator:
    """Simulated robot arm that only accepts gate-authorized commands."""

    def __init__(self, verify_core: VerifyCore):
        self._verify_core = verify_core
        self.last_result: str = ""
        self.last_reason: str = ""

    def execute(self, command: ActuatorCommand) -> bool:
        """Attempt to execute a command.  Returns True only on success."""

        # SECURITY BOUNDARY: no token means no execution
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
