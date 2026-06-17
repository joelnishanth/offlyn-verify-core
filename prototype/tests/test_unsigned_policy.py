"""Tests proving that unsigned or tampered policies are rejected."""

from pathlib import Path

import pytest

from gate.verify_core import VerifyCore
from policy.compiler import compile_policy
from policy.signer import sign_policy
from policy.verifier import PolicyVerificationError

ROBOT_ARM_POLICY = Path(__file__).parent.parent / "policy" / "policies" / "robot_arm_policy.yaml"


def test_unsigned_policy_rejected() -> None:
    gate = VerifyCore()
    unsigned = compile_policy(ROBOT_ARM_POLICY)

    with pytest.raises(PolicyVerificationError, match="unsigned"):
        gate.load_policy(unsigned)


def test_tampered_policy_rejected() -> None:
    gate = VerifyCore()
    policy = compile_policy(ROBOT_ARM_POLICY)
    policy = sign_policy(policy)

    # Tamper with canonical bytes after signing
    policy.canonical_bytes = policy.canonical_bytes + b"TAMPERED"

    with pytest.raises(PolicyVerificationError, match="invalid"):
        gate.load_policy(policy)


def test_signed_policy_accepted() -> None:
    gate = VerifyCore()
    policy = compile_policy(ROBOT_ARM_POLICY)
    policy = sign_policy(policy)
    gate.load_policy(policy)  # Should not raise
    assert gate.current_policy is not None
