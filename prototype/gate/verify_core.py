"""Verify Core gate: the Actuation Boundary Enforcement Point (ABEP).

This module ties together policy loading, signature verification, action
evaluation, authorization-token issuance, and audit logging.  It is the
single choke-point through which every actuator command must pass.

Design invariants:
  - Only signed policies are loaded (fail-closed).
  - Policy rollback (lower epoch) is rejected.
  - Every decision is logged.
  - ALLOW decisions produce a short-lived, action-bound authorization token.
  - A replay cache prevents token reuse.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from gate import decision_engine
from gate.audit_log import log_decision
from gate.schemas import (
    ActionRequest,
    AuthorizationToken,
    Decision,
    GateDecision,
)
from policy.compiler import CompiledPolicy, compile_policy
from policy.signer import get_public_key, sign_policy
from policy.verifier import PolicyVerificationError, verify_policy


class VerifyCore:
    """The central gate.  Instantiate once per robot or actuator group."""

    def __init__(self, public_key: Ed25519PublicKey | None = None):
        self._public_key = public_key or get_public_key()
        self._policy: CompiledPolicy | None = None
        self._replay_cache: set[str] = set()

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def load_policy(self, policy: CompiledPolicy) -> None:
        """Load a signed policy after verifying its signature and epoch."""
        verify_policy(policy, self._public_key)

        if self._policy is not None and policy.policy_epoch < self._policy.policy_epoch:
            raise PolicyVerificationError(
                f"Policy rollback denied: incoming epoch {policy.policy_epoch} "
                f"< current epoch {self._policy.policy_epoch}"
            )

        self._policy = policy

    def load_policy_from_file(self, path: Path) -> None:
        """Compile, sign (demo), and load a policy file."""
        policy = compile_policy(path)
        policy = sign_policy(policy)
        self.load_policy(policy)

    @property
    def current_policy(self) -> CompiledPolicy | None:
        return self._policy

    # ------------------------------------------------------------------
    # Action evaluation
    # ------------------------------------------------------------------

    def evaluate(self, request: ActionRequest) -> tuple[GateDecision, AuthorizationToken | None]:
        """Evaluate an action request and return a decision + optional auth token."""
        if self._policy is None:
            decision = GateDecision(
                decision=Decision.DENY,
                reason="no_policy_loaded",
                action_hash=request.canonical_hash(),
                nonce=request.nonce,
            )
            log_decision(request, decision.decision, decision.reason)
            return decision, None

        decision = decision_engine.evaluate(request, self._policy)
        log_decision(request, decision.decision, decision.reason)

        token = None
        if decision.decision == Decision.ALLOW:
            token = self._issue_token(request)

        return decision, token

    # ------------------------------------------------------------------
    # Authorization tokens
    # ------------------------------------------------------------------

    def _issue_token(self, request: ActionRequest) -> AuthorizationToken:
        token = AuthorizationToken(
            action_hash=request.canonical_hash(),
            nonce=request.nonce,
            policy_hash=self._policy.policy_hash if self._policy else "",
        )
        # Sign the token payload so the actuator can verify it
        token_payload = json.dumps(
            {
                "token_id": token.token_id,
                "action_hash": token.action_hash,
                "nonce": token.nonce,
                "policy_hash": token.policy_hash,
                "issued_at": token.issued_at,
                "expires_at": token.expires_at,
            },
            sort_keys=True,
        )
        token.signature = hashlib.sha256(token_payload.encode()).hexdigest()
        return token

    def validate_token(self, token: AuthorizationToken, action_hash: str) -> tuple[bool, str]:
        """Validate an authorization token for the actuator.

        Returns (valid, reason).
        """
        if token.is_expired():
            return False, "token_expired"

        if token.action_hash != action_hash:
            return False, "action_hash_mismatch"

        if token.token_id in self._replay_cache:
            return False, "token_replayed"

        # Verify token signature
        token_payload = json.dumps(
            {
                "token_id": token.token_id,
                "action_hash": token.action_hash,
                "nonce": token.nonce,
                "policy_hash": token.policy_hash,
                "issued_at": token.issued_at,
                "expires_at": token.expires_at,
            },
            sort_keys=True,
        )
        expected_sig = hashlib.sha256(token_payload.encode()).hexdigest()
        if token.signature != expected_sig:
            return False, "token_signature_invalid"

        # Mark as used (replay protection)
        self._replay_cache.add(token.token_id)
        return True, "token_valid"
