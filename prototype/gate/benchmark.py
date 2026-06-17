"""Benchmark module for Offlyn Verify Core gate operations.

Measures latency for policy loading, gate decisions, token validation,
and replay detection.  All measurements are software-simulation numbers —
hardware targets will differ.

Usage:
    python -m gate.benchmark --iterations 10000 --output ../results/benchmark_results.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

from gate.audit_log import set_log_path
from gate.schemas import ActionRequest, Decision
from gate.verify_core import VerifyCore
from policy.compiler import compile_policy
from policy.signer import sign_policy

POLICY_PATH = Path(__file__).parent.parent / "policy" / "policies" / "robot_arm_policy.yaml"

WARMUP_ITERATIONS = 100


def _make_allowed_request() -> ActionRequest:
    return ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def _make_denied_request() -> ActionRequest:
    return ActionRequest(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 30, "speed": 1.2},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def _measure(fn, iterations: int) -> list[float]:
    """Run fn for warmup + iterations, return timings in seconds."""
    for _ in range(WARMUP_ITERATIONS):
        fn()

    timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
    return timings


def _stats(timings: list[float]) -> dict[str, float]:
    """Compute p50, p95, p99, min, max, mean in milliseconds."""
    sorted_t = sorted(timings)
    n = len(sorted_t)
    return {
        "p50_ms": sorted_t[n // 2] * 1000,
        "p95_ms": sorted_t[int(n * 0.95)] * 1000,
        "p99_ms": sorted_t[int(n * 0.99)] * 1000,
        "min_ms": sorted_t[0] * 1000,
        "max_ms": sorted_t[-1] * 1000,
        "mean_ms": statistics.mean(sorted_t) * 1000,
    }


def run_benchmarks(iterations: int) -> list[dict]:
    """Run all benchmarks and return results as list of dicts."""
    set_log_path(Path("/dev/null"))

    results = []

    # --- Policy loading + verification ---
    def bench_policy_load():
        policy = compile_policy(POLICY_PATH)
        policy = sign_policy(policy)
        g = VerifyCore()
        g.load_policy(policy)

    timings = _measure(bench_policy_load, iterations)
    s = _stats(timings)
    results.append({"metric": "policy_load_and_verify", "iterations": iterations, **s})

    # --- Gate decision: allowed action ---
    gate = VerifyCore()
    gate.load_policy_from_file(POLICY_PATH)

    def bench_allow():
        gate.evaluate(_make_allowed_request())

    timings = _measure(bench_allow, iterations)
    s = _stats(timings)
    results.append({"metric": "gate_decision_allow", "iterations": iterations, **s})

    # --- Gate decision: denied action ---
    def bench_deny():
        gate.evaluate(_make_denied_request())

    timings = _measure(bench_deny, iterations)
    s = _stats(timings)
    results.append({"metric": "gate_decision_deny", "iterations": iterations, **s})

    # --- Token validation ---
    # Pre-generate tokens for validation
    tokens_and_hashes = []
    for _ in range(WARMUP_ITERATIONS + iterations):
        req = _make_allowed_request()
        _, token = gate.evaluate(req)
        tokens_and_hashes.append((token, req.canonical_hash()))
    # Reset replay cache for the benchmark
    gate._replay_cache.clear()

    idx = WARMUP_ITERATIONS

    def bench_token_validate():
        nonlocal idx
        t, h = tokens_and_hashes[idx]
        gate.validate_token(t, h)
        idx += 1

    # Warmup
    for _ in range(WARMUP_ITERATIONS):
        t, h = tokens_and_hashes[idx - WARMUP_ITERATIONS]
        gate.validate_token(t, h)
    gate._replay_cache.clear()
    idx = WARMUP_ITERATIONS

    token_timings: list[float] = []
    for _ in range(iterations):
        t, h = tokens_and_hashes[idx]
        start = time.perf_counter()
        gate.validate_token(t, h)
        elapsed = time.perf_counter() - start
        token_timings.append(elapsed)
        idx += 1

    s = _stats(token_timings)
    results.append({"metric": "token_validation", "iterations": iterations, **s})

    # --- Replay detection ---
    # All tokens are now in the cache; re-validating should hit replay
    gate_replay = VerifyCore()
    gate_replay.load_policy_from_file(POLICY_PATH)
    # Pre-use one token so it's in the cache
    req = _make_allowed_request()
    _, replay_token = gate_replay.evaluate(req)
    action_hash = req.canonical_hash()
    gate_replay.validate_token(replay_token, action_hash)

    def bench_replay_detect():
        gate_replay.validate_token(replay_token, action_hash)

    timings = _measure(bench_replay_detect, iterations)
    s = _stats(timings)
    results.append({"metric": "replay_detection", "iterations": iterations, **s})

    return results


def print_results(results: list[dict]) -> None:
    print(f"\n{'Metric':<30} {'p50':>10} {'p95':>10} {'p99':>10} {'min':>10} {'max':>10} {'mean':>10}")
    print("-" * 90)
    for r in results:
        print(
            f"{r['metric']:<30} "
            f"{r['p50_ms']:>9.4f}ms "
            f"{r['p95_ms']:>9.4f}ms "
            f"{r['p99_ms']:>9.4f}ms "
            f"{r['min_ms']:>9.4f}ms "
            f"{r['max_ms']:>9.4f}ms "
            f"{r['mean_ms']:>9.4f}ms"
        )
    print()


def write_csv(results: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["metric", "iterations", "p50_ms", "p95_ms", "p99_ms", "min_ms", "max_ms", "mean_ms"]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results written to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Offlyn Verify Core — benchmark suite")
    parser.add_argument("--iterations", type=int, default=10000, help="Number of iterations per benchmark")
    parser.add_argument("--output", type=Path, default=None, help="Output CSV path")
    args = parser.parse_args()

    print(f"Running benchmarks ({args.iterations} iterations each, {WARMUP_ITERATIONS} warmup)...")
    print("NOTE: These are software-simulation measurements, not hardware measurements.")

    results = run_benchmarks(args.iterations)
    print_results(results)

    if args.output:
        write_csv(results, args.output)


if __name__ == "__main__":
    main()
