"""Append-only JSONL audit log for every gate decision.

Every ALLOW and DENY is written here.  In a hardware implementation this
log would be stored in tamper-evident storage (e.g. a signed hash chain).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from gate.schemas import ActionRequest, Decision

_LOG_PATH = Path("audit.jsonl")


def set_log_path(path: Path) -> None:
    global _LOG_PATH
    _LOG_PATH = path


def log_decision(
    request: ActionRequest,
    decision: Decision,
    reason: str,
) -> None:
    entry = {
        "timestamp": time.time(),
        "actor": request.actor,
        "action": request.action,
        "target": request.target,
        "nonce": request.nonce,
        "action_hash": request.canonical_hash(),
        "decision": decision.value,
        "reason": reason,
    }
    with open(_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
