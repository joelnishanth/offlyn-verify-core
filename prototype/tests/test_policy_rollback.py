"""Tests proving that policy rollback attempts are rejected."""

import hashlib
import json
from pathlib import Path

import pytest

from gate.verify_core import VerifyCore
from policy.compiler import compile_policy
from policy.signer import sign_policy
from policy.verifier import PolicyVerificationError

ROBOT_ARM_POLICY = Path(__file__).parent.parent / "policy" / "policies" / "robot_arm_policy.yaml"


def test_rollback_to_lower_epoch_rejected(gate: VerifyCore) -> None:
    """A policy with a lower epoch than the currently loaded one must be rejected."""
    old_policy = compile_policy(ROBOT_ARM_POLICY)

    # Rebuild with epoch 0 (lower than the loaded epoch 1)
    old_policy.policy_epoch = 0
    canonical = json.dumps(
        {
            "policy_id": old_policy.policy_id,
            "policy_epoch": 0,
            "actor": old_policy.actor,
            "rules": [
                {
                    "action": r.action,
                    "target": r.target,
                    "max_speed": r.max_speed,
                    "allowed_zones": sorted(r.allowed_zones),
                }
                for r in old_policy.rules
            ],
        },
        sort_keys=True,
    ).encode()
    old_policy.canonical_bytes = canonical
    old_policy.policy_hash = hashlib.sha256(canonical).hexdigest()
    old_policy = sign_policy(old_policy)

    with pytest.raises(PolicyVerificationError, match="rollback denied"):
        gate.load_policy(old_policy)


def test_same_epoch_accepted(gate: VerifyCore) -> None:
    """Reloading the same epoch is allowed (idempotent policy refresh)."""
    policy = compile_policy(ROBOT_ARM_POLICY)
    policy = sign_policy(policy)
    gate.load_policy(policy)  # Should not raise


def test_higher_epoch_accepted(gate: VerifyCore) -> None:
    """Upgrading to a higher epoch must succeed."""
    new_policy = compile_policy(ROBOT_ARM_POLICY)
    new_policy.policy_epoch = 2
    canonical = json.dumps(
        {
            "policy_id": new_policy.policy_id,
            "policy_epoch": 2,
            "actor": new_policy.actor,
            "rules": [
                {
                    "action": r.action,
                    "target": r.target,
                    "max_speed": r.max_speed,
                    "allowed_zones": sorted(r.allowed_zones),
                }
                for r in new_policy.rules
            ],
        },
        sort_keys=True,
    ).encode()
    new_policy.canonical_bytes = canonical
    new_policy.policy_hash = hashlib.sha256(canonical).hexdigest()
    new_policy = sign_policy(new_policy)
    gate.load_policy(new_policy)  # Should not raise
    assert gate.current_policy.policy_epoch == 2
