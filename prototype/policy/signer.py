"""Policy signer: generates demo Ed25519 keys and signs compiled policies.

In a production deployment this signing step would happen on a secure
build/signing server.  The private key would never reside on the robot.
Here we use local demo keys for reproducibility.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from policy.compiler import CompiledPolicy

_KEYS_DIR = Path(__file__).parent
_PRIVATE_KEY_PATH = _KEYS_DIR / "demo_private.pem"
_PUBLIC_KEY_PATH = _KEYS_DIR / "demo_public.pem"


def _ensure_demo_keys() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a demo Ed25519 key pair if one does not exist yet."""
    if _PRIVATE_KEY_PATH.exists() and _PUBLIC_KEY_PATH.exists():
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        priv = load_pem_private_key(_PRIVATE_KEY_PATH.read_bytes(), password=None)
        assert isinstance(priv, Ed25519PrivateKey)
        pub = priv.public_key()
        return priv, pub

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    _PRIVATE_KEY_PATH.write_bytes(
        priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )
    _PUBLIC_KEY_PATH.write_bytes(
        pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    )
    return priv, pub


def get_public_key() -> Ed25519PublicKey:
    _, pub = _ensure_demo_keys()
    return pub


def sign_policy(policy: CompiledPolicy) -> CompiledPolicy:
    """Sign the canonical bytes of a compiled policy and attach the signature."""
    priv, _ = _ensure_demo_keys()
    policy.signature = priv.sign(policy.canonical_bytes)
    return policy
