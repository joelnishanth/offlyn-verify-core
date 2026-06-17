"""Scenario runner: demonstrates all key Verify Core behaviors.

Usage:
    python -m planner.scenarios --scenario safe_move
    python -m planner.scenarios --scenario all
    python -m planner.scenarios --list
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from actuator_sim.robot_arm_sim import RobotArmActuator
from gate.audit_log import set_log_path
from gate.schemas import ActionRequest, ActuatorCommand, AuthorizationToken, Decision
from gate.verify_core import VerifyCore
from planner import planner
from policy.compiler import CompiledPolicy, compile_policy
from policy.signer import sign_policy
from policy.verifier import PolicyVerificationError

POLICY_PATH = Path(__file__).parent.parent / "policy" / "policies" / "robot_arm_policy.yaml"


def _print_header(name: str) -> None:
    print(f"\n{'='*60}")
    print(f"  SCENARIO: {name}")
    print(f"{'='*60}\n")


def _print_action(request: ActionRequest) -> None:
    params = " ".join(f"{k}={v}" for k, v in request.parameters.items())
    ctx = " ".join(f"{k}={v}" for k, v in request.context.items())
    print(f"[PLANNER]     Proposed action: {request.action} target={request.target} {params}")
    if ctx:
        print(f"[PLANNER]     Context: {ctx}")


def _print_decision(decision_val: str, reason: str) -> None:
    tag = "ALLOW" if decision_val == "allow" else "DENY"
    print(f"[VERIFY_CORE] Decision: {tag} reason={reason}")


def _print_actuator(result: str, reason: str) -> None:
    if result == "executed":
        print(f"[ACTUATOR]    Command executed ({reason})")
    else:
        print(f"[ACTUATOR]    Command rejected ({reason})")


def _setup() -> tuple[VerifyCore, RobotArmActuator]:
    set_log_path(Path("/dev/null"))
    gate = VerifyCore()
    gate.load_policy_from_file(POLICY_PATH)
    actuator = RobotArmActuator(gate)
    return gate, actuator


def _run_action(
    gate: VerifyCore,
    actuator: RobotArmActuator,
    request: ActionRequest,
) -> None:
    _print_action(request)
    decision, token = gate.evaluate(request)
    _print_decision(decision.decision.value, decision.reason)
    cmd = ActuatorCommand(action_request=request, authorization_token=token)
    actuator.execute(cmd)
    _print_actuator(actuator.last_result, actuator.last_reason)


# ------------------------------------------------------------------
# Individual scenarios
# ------------------------------------------------------------------

def scenario_safe_move() -> None:
    _print_header("safe_move")
    gate, actuator = _setup()
    _run_action(gate, actuator, planner.safe_move())


def scenario_speed_violation() -> None:
    _print_header("speed_violation")
    gate, actuator = _setup()
    _run_action(gate, actuator, planner.speed_violation())


def scenario_angle_violation() -> None:
    _print_header("angle_violation")
    gate, actuator = _setup()
    _run_action(gate, actuator, planner.angle_violation())


def scenario_geofence_violation() -> None:
    _print_header("geofence_violation")
    gate, actuator = _setup()
    _run_action(gate, actuator, planner.geofence_violation())


def scenario_human_nearby_violation() -> None:
    _print_header("human_nearby_violation")
    gate, actuator = _setup()
    _run_action(gate, actuator, planner.human_nearby_violation())


def scenario_unsigned_policy_update() -> None:
    _print_header("unsigned_policy_update")
    gate, _ = _setup()

    print("[ATTACKER]    Attempting to load unsigned policy...")
    unsigned = compile_policy(POLICY_PATH)
    try:
        gate.load_policy(unsigned)
        print("[VERIFY_CORE] ERROR: unsigned policy was accepted (should not happen)")
    except PolicyVerificationError as e:
        print(f"[VERIFY_CORE] Policy rejected: {e}")
        print("[GATE]        System remains on previous signed policy")


def scenario_policy_rollback() -> None:
    _print_header("policy_rollback")
    gate, _ = _setup()

    print("[ATTACKER]    Attempting to load policy with lower epoch...")
    old_policy = compile_policy(POLICY_PATH)
    old_policy.policy_epoch = 0  # Lower than current epoch of 1
    old_policy = sign_policy(old_policy)
    # Re-sign after modifying epoch — but the canonical bytes already include
    # the original epoch, so we need to rebuild canonical bytes.
    import hashlib
    import json
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

    try:
        gate.load_policy(old_policy)
        print("[VERIFY_CORE] ERROR: rollback was accepted (should not happen)")
    except PolicyVerificationError as e:
        print(f"[VERIFY_CORE] Policy rejected: {e}")
        print("[GATE]        Rollback attack blocked")


def scenario_replay_attack() -> None:
    _print_header("replay_attack")
    gate, actuator = _setup()

    request = planner.safe_move()
    _print_action(request)

    decision, token = gate.evaluate(request)
    _print_decision(decision.decision.value, decision.reason)

    cmd = ActuatorCommand(action_request=request, authorization_token=token)
    actuator.execute(cmd)
    _print_actuator(actuator.last_result, actuator.last_reason)

    print()
    print("[ATTACKER]    Replaying the same authorization token...")
    cmd_replay = ActuatorCommand(action_request=request, authorization_token=token)
    actuator.execute(cmd_replay)
    _print_actuator(actuator.last_result, actuator.last_reason)


def scenario_direct_actuator_bypass() -> None:
    _print_header("direct_actuator_bypass")
    gate, actuator = _setup()

    request = planner.safe_move()
    print(f"[ATTACKER]    Sending command directly to actuator (no gate)...")
    _print_action(request)

    cmd = ActuatorCommand(action_request=request, authorization_token=None)
    actuator.execute(cmd)
    _print_actuator(actuator.last_result, actuator.last_reason)


SCENARIOS = {
    "safe_move": scenario_safe_move,
    "speed_violation": scenario_speed_violation,
    "angle_violation": scenario_angle_violation,
    "geofence_violation": scenario_geofence_violation,
    "human_nearby_violation": scenario_human_nearby_violation,
    "unsigned_policy_update": scenario_unsigned_policy_update,
    "policy_rollback": scenario_policy_rollback,
    "replay_attack": scenario_replay_attack,
    "direct_actuator_bypass": scenario_direct_actuator_bypass,
}


def run_all() -> None:
    for fn in SCENARIOS.values():
        fn()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offlyn Verify Core — scenario runner"
    )
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS.keys()) + ["all"],
        help="Scenario to run",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios",
    )
    args = parser.parse_args()

    if args.list:
        print("Available scenarios:")
        for name in SCENARIOS:
            print(f"  {name}")
        return

    if args.scenario is None:
        parser.print_help()
        return

    if args.scenario == "all":
        run_all()
    else:
        SCENARIOS[args.scenario]()


if __name__ == "__main__":
    main()
