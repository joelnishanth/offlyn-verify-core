"""Shared test fixtures for Offlyn Verify Core tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from actuator_sim.robot_arm_sim import RobotArmActuator
from gate.audit_log import set_log_path
from gate.verify_core import VerifyCore

POLICY_DIR = Path(__file__).parent.parent / "policy" / "policies"
ROBOT_ARM_POLICY = POLICY_DIR / "robot_arm_policy.yaml"


@pytest.fixture(autouse=True)
def _silence_audit_log(tmp_path: Path) -> None:
    set_log_path(tmp_path / "test_audit.jsonl")


@pytest.fixture
def gate() -> VerifyCore:
    g = VerifyCore()
    g.load_policy_from_file(ROBOT_ARM_POLICY)
    return g


@pytest.fixture
def actuator(gate: VerifyCore) -> RobotArmActuator:
    return RobotArmActuator(gate)
