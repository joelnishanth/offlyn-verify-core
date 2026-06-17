"""Tamper-evident append-only JSONL audit log with hash chaining.

Every ALLOW and DENY decision is recorded.  Each entry includes the SHA-256
hash of the previous entry, forming a chain that can be verified offline.
Modifying, inserting, or deleting any entry breaks the chain from that point
forward.

In a hardware implementation this log would be stored in tamper-evident
storage (e.g. a signed hash chain backed by a monotonic counter).
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from gate.schemas import ActionRequest, Decision

_LOG_PATH = Path("audit.jsonl")

GENESIS_HASH = "0" * 64


def set_log_path(path: Path) -> None:
    global _LOG_PATH
    _LOG_PATH = path


def _get_previous_hash() -> str:
    """Read the last entry's hash, or return the genesis hash if the log is empty."""
    if not _LOG_PATH.exists():
        return GENESIS_HASH
    try:
        with open(_LOG_PATH, "rb") as f:
            f.seek(0, 2)
            if f.tell() == 0:
                return GENESIS_HASH
            # Scan backward for the last newline-delimited entry
            f.seek(0)
            lines = f.read().decode().strip().split("\n")
            if not lines or not lines[-1].strip():
                return GENESIS_HASH
            last = json.loads(lines[-1])
            return last.get("entry_hash", GENESIS_HASH)
    except (json.JSONDecodeError, OSError):
        return GENESIS_HASH


def _compute_entry_hash(entry_content: dict, previous_hash: str) -> str:
    """Hash the canonical entry content concatenated with the previous hash."""
    canonical = json.dumps(entry_content, sort_keys=True) + previous_hash
    return hashlib.sha256(canonical.encode()).hexdigest()


def log_decision(
    request: ActionRequest,
    decision: Decision,
    reason: str,
) -> None:
    content = {
        "timestamp": time.time(),
        "actor": request.actor,
        "action": request.action,
        "target": request.target,
        "nonce": request.nonce,
        "action_hash": request.canonical_hash(),
        "decision": decision.value,
        "reason": reason,
    }

    previous_hash = _get_previous_hash()
    entry_hash = _compute_entry_hash(content, previous_hash)

    entry = {**content, "previous_entry_hash": previous_hash, "entry_hash": entry_hash}

    with open(_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
