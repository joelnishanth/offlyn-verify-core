"""Policy verifier: validates signatures on compiled policies.

The Verify Core gate calls this before loading any policy.  A policy that
fails verification is never loaded — this is a hard security boundary.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from policy.compiler import CompiledPolicy


class PolicyVerificationError(Exception):
    """Raised when a policy fails signature or integrity verification."""


def verify_policy(policy: CompiledPolicy, public_key: Ed25519PublicKey) -> bool:
    """Return True if the policy signature is valid, raise on failure."""
    if not policy.signature:
        raise PolicyVerificationError("Policy is unsigned — no signature present")

    try:
        public_key.verify(policy.signature, policy.canonical_bytes)
    except InvalidSignature:
        raise PolicyVerificationError(
            "Policy signature invalid — content may have been tampered with"
        )

    return True
