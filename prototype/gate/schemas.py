"""Canonical Pydantic schemas for action requests, decisions, and authorization tokens.

These schemas define the wire format between every component in the Offlyn Verify
Core architecture.  Strict validation here is intentional — the gate must never
operate on ambiguous or partially-specified inputs.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class ActionRequest(BaseModel):
    """A proposed robot action submitted by the AI planner."""

    actor: str
    action: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    nonce: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: float = Field(default_factory=time.time)
    policy_epoch: int = 1

    def canonical_hash(self) -> str:
        """Deterministic hash of the action content (excludes nonce/timestamp)."""
        payload = json.dumps(
            {
                "actor": self.actor,
                "action": self.action,
                "target": self.target,
                "parameters": self.parameters,
                "context": self.context,
                "policy_epoch": self.policy_epoch,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()


class GateDecision(BaseModel):
    """The Verify Core gate's response to an action request."""

    decision: Decision
    reason: str
    action_hash: str = ""
    nonce: str = ""


class AuthorizationToken(BaseModel):
    """Short-lived token issued for ALLOW decisions.

    The actuator must validate this token before executing any command.  Tokens
    are bound to the specific action hash, nonce, and policy hash so they cannot
    be reused for a different action.
    """

    token_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    action_hash: str
    nonce: str
    policy_hash: str
    issued_at: float = Field(default_factory=time.time)
    expires_at: float = 0.0
    signature: str = ""

    # Default token lifetime: 5 seconds (intentionally short)
    TOKEN_LIFETIME_SECONDS: float = 5.0

    def model_post_init(self, __context: Any) -> None:
        if self.expires_at == 0.0:
            self.expires_at = self.issued_at + self.TOKEN_LIFETIME_SECONDS

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class ActuatorCommand(BaseModel):
    """A command sent to the actuator, bundling the original request and auth token."""

    action_request: ActionRequest
    authorization_token: AuthorizationToken | None = None
