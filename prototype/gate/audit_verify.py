"""Audit log chain verifier.

Reads a JSONL audit log and verifies the hash chain from genesis to the
last entry.  Any modification, insertion, or deletion of an entry will
cause the chain to break at the tampered position.

Usage:
    python -m gate.audit_verify --log audit.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from gate.audit_log import GENESIS_HASH


def _compute_entry_hash(content: dict, previous_hash: str) -> str:
    canonical = json.dumps(content, sort_keys=True) + previous_hash
    return hashlib.sha256(canonical.encode()).hexdigest()


def verify_chain(log_path: Path) -> tuple[bool, int, str]:
    """Verify the audit log hash chain.

    Returns (valid, line_count, message).
    """
    if not log_path.exists():
        return False, 0, "Log file does not exist"

    lines = log_path.read_text().strip().split("\n")
    if not lines or not lines[0].strip():
        return True, 0, "Empty log — trivially valid"

    expected_previous = GENESIS_HASH

    for i, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False, i, f"INVALID chain at line {i}: malformed JSON"

        stored_previous = entry.get("previous_entry_hash", "")
        stored_hash = entry.get("entry_hash", "")

        if stored_previous != expected_previous:
            return False, i, (
                f"INVALID chain at line {i}: previous_entry_hash mismatch "
                f"(expected {expected_previous[:16]}..., got {stored_previous[:16]}...)"
            )

        content = {
            k: v
            for k, v in entry.items()
            if k not in ("previous_entry_hash", "entry_hash")
        }
        recomputed = _compute_entry_hash(content, stored_previous)

        if recomputed != stored_hash:
            return False, i, (
                f"INVALID chain at line {i}: entry_hash mismatch "
                f"(expected {recomputed[:16]}..., got {stored_hash[:16]}...)"
            )

        expected_previous = stored_hash

    return True, len(lines), f"VALID chain — {len(lines)} entries verified"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Offlyn Verify Core audit log chain")
    parser.add_argument("--log", type=Path, required=True, help="Path to JSONL audit log")
    args = parser.parse_args()

    valid, count, message = verify_chain(args.log)
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
