"""Tests for tamper-evident audit log hash chaining."""

from __future__ import annotations

import json
from pathlib import Path

from gate.audit_log import GENESIS_HASH, log_decision, set_log_path
from gate.audit_verify import verify_chain
from gate.schemas import ActionRequest, Decision


def _make_request(action: str = "move_joint", speed: float = 0.4) -> ActionRequest:
    return ActionRequest(
        actor="robot_planner_01",
        action=action,
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": speed},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def test_entries_contain_hashes(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    set_log_path(log)

    log_decision(_make_request(), Decision.ALLOW, "within_policy_bounds")
    log_decision(_make_request(speed=1.2), Decision.DENY, "speed_exceeds_limit")

    lines = log.read_text().strip().split("\n")
    assert len(lines) == 2

    first = json.loads(lines[0])
    assert "previous_entry_hash" in first
    assert "entry_hash" in first
    assert first["previous_entry_hash"] == GENESIS_HASH
    assert len(first["entry_hash"]) == 64

    second = json.loads(lines[1])
    assert second["previous_entry_hash"] == first["entry_hash"]


def test_valid_chain_verifies(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    set_log_path(log)

    for i in range(5):
        log_decision(_make_request(speed=0.1 * (i + 1)), Decision.ALLOW, "ok")

    valid, count, message = verify_chain(log)
    assert valid is True
    assert count == 5
    assert "VALID" in message


def test_tampered_entry_breaks_chain(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    set_log_path(log)

    for i in range(5):
        log_decision(_make_request(speed=0.1 * (i + 1)), Decision.ALLOW, "ok")

    # Tamper with the second entry's reason field
    lines = log.read_text().strip().split("\n")
    entry = json.loads(lines[1])
    entry["reason"] = "TAMPERED"
    lines[1] = json.dumps(entry)
    log.write_text("\n".join(lines) + "\n")

    valid, line_num, message = verify_chain(log)
    assert valid is False
    assert line_num == 2
    assert "INVALID" in message


def test_deleted_entry_breaks_chain(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    set_log_path(log)

    for i in range(5):
        log_decision(_make_request(speed=0.1 * (i + 1)), Decision.ALLOW, "ok")

    # Delete the third entry
    lines = log.read_text().strip().split("\n")
    del lines[2]
    log.write_text("\n".join(lines) + "\n")

    valid, _, message = verify_chain(log)
    assert valid is False
    assert "INVALID" in message


def test_empty_log_is_valid(tmp_path: Path) -> None:
    log = tmp_path / "empty.jsonl"
    log.write_text("")

    valid, count, message = verify_chain(log)
    assert valid is True
    assert count == 0
