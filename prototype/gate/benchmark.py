"""Benchmark module for Offlyn Verify Core gate operations.

Measures latency for policy loading, gate decisions, token validation,
and replay detection.  All measurements are software-simulation numbers —
hardware targets will differ.

Usage:
    python -m gate.benchmark --iterations 10000 --output ../results/benchmark_results.csv

    # Decision latency with varying policy complexity (issue #6)
    python -m gate.benchmark --mode decision --iterations 10000

    # Token validation with varying replay cache sizes (issue #7)
    python -m gate.benchmark --mode token --iterations 10000
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

from gate.audit_log import set_log_path
from gate.schemas import ActionRequest, AuthorizationToken, Decision
from gate.verify_core import VerifyCore
from policy.compiler import CompiledPolicy, PolicyRule, compile_policy
from policy.signer import sign_policy

POLICY_PATH = Path(__file__).parent.parent / "policy" / "policies" / "robot_arm_policy.yaml"

WARMUP_ITERATIONS = 100


# ------------------------------------------------------------------
# System information
# ------------------------------------------------------------------

def _system_info() -> dict[str, str]:
    """Collect CPU, RAM, OS, and Python version for reproducibility."""
    info: dict[str, str] = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
    }
    try:
        import psutil
        info["cpu_count"] = str(psutil.cpu_count(logical=True))
        info["ram_gb"] = f"{psutil.virtual_memory().total / (1024**3):.1f}"
    except ImportError:
        info["cpu_count"] = str(os.cpu_count() or "unknown")
        info["ram_gb"] = "unknown (install psutil for details)"
    return info


def _print_system_info() -> None:
    info = _system_info()
    print("System information:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    print()


# ------------------------------------------------------------------
# Request and policy generators
# ------------------------------------------------------------------

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


def _generate_policy(num_rules: int) -> CompiledPolicy:
    """Build a signed policy with *num_rules* synthetic rules.

    The first rule always matches the standard allowed request so
    evaluation exercises the full check path.
    """
    rules: list[PolicyRule] = []
    for i in range(num_rules):
        rules.append(PolicyRule(
            action="move_joint" if i == 0 else f"action_{i}",
            target="joint_2" if i == 0 else f"target_{i}",
            max_speed=0.5 + i * 0.1,
            min_angle_degrees=-90.0,
            max_angle_degrees=90.0,
            allowed_zones=["safe_area_a", "safe_area_b"],
            deny_when_human_nearby=True,
        ))

    canonical = json.dumps(
        {
            "policy_id": f"synthetic_{num_rules}_rules",
            "policy_epoch": 1,
            "actor": "robot_planner_01",
            "rules": [
                {
                    "action": r.action,
                    "target": r.target,
                    "max_speed": r.max_speed,
                    "allowed_zones": sorted(r.allowed_zones),
                }
                for r in rules
            ],
        },
        sort_keys=True,
    ).encode()

    policy = CompiledPolicy(
        policy_id=f"synthetic_{num_rules}_rules",
        policy_epoch=1,
        actor="robot_planner_01",
        rules=rules,
        raw_yaml="",
        canonical_bytes=canonical,
        policy_hash=hashlib.sha256(canonical).hexdigest(),
    )
    return sign_policy(policy)


# ------------------------------------------------------------------
# Measurement utilities
# ------------------------------------------------------------------

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


def _stats(timings: list[float], unit: str = "ms") -> dict[str, float]:
    """Compute p50, p95, p99, min, max, mean in the given unit."""
    sorted_t = sorted(timings)
    n = len(sorted_t)
    multiplier = 1_000 if unit == "ms" else 1_000_000  # ms or us
    suffix = f"_{unit}"
    return {
        f"p50{suffix}": sorted_t[n // 2] * multiplier,
        f"p95{suffix}": sorted_t[int(n * 0.95)] * multiplier,
        f"p99{suffix}": sorted_t[int(n * 0.99)] * multiplier,
        f"min{suffix}": sorted_t[0] * multiplier,
        f"max{suffix}": sorted_t[-1] * multiplier,
        f"mean{suffix}": statistics.mean(sorted_t) * multiplier,
    }


# ------------------------------------------------------------------
# Original combined benchmarks
# ------------------------------------------------------------------

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
    tokens_and_hashes = []
    for _ in range(WARMUP_ITERATIONS + iterations):
        req = _make_allowed_request()
        _, token = gate.evaluate(req)
        tokens_and_hashes.append((token, req.canonical_hash()))
    gate._replay_cache.clear()

    idx = WARMUP_ITERATIONS

    def bench_token_validate():
        nonlocal idx
        t, h = tokens_and_hashes[idx]
        gate.validate_token(t, h)
        idx += 1

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
    gate_replay = VerifyCore()
    gate_replay.load_policy_from_file(POLICY_PATH)
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


# ------------------------------------------------------------------
# Issue #6: Decision latency with varying policy complexity
# ------------------------------------------------------------------

def run_decision_latency_benchmarks(
    iterations: int,
    rule_counts: tuple[int, ...] = (1, 5, 20),
) -> list[dict]:
    """Measure gate decision latency across different policy complexities.

    For each rule count, measures allowed and denied action evaluation
    latency and reports p50/p95/p99/max in microseconds.
    """
    set_log_path(Path("/dev/null"))
    results: list[dict] = []

    for num_rules in rule_counts:
        policy = _generate_policy(num_rules)
        gate = VerifyCore()
        gate.load_policy(policy)

        # Allowed action (matches first rule)
        def bench_allow(g=gate):
            g.evaluate(_make_allowed_request())

        timings = _measure(bench_allow, iterations)
        s = _stats(timings, unit="us")
        results.append({
            "metric": f"decision_allow_{num_rules}_rules",
            "num_rules": num_rules,
            "decision": "allow",
            "iterations": iterations,
            **s,
        })

        # Denied action (speed exceeds limit — fails at speed check)
        def bench_deny(g=gate):
            g.evaluate(_make_denied_request())

        timings = _measure(bench_deny, iterations)
        s = _stats(timings, unit="us")
        results.append({
            "metric": f"decision_deny_{num_rules}_rules",
            "num_rules": num_rules,
            "decision": "deny",
            "iterations": iterations,
            **s,
        })

    return results


# ------------------------------------------------------------------
# Issue #7: Token validation with per-component breakdown and
#           varying replay cache sizes
# ------------------------------------------------------------------

def run_token_validation_benchmarks(
    iterations: int,
    cache_sizes: tuple[int, ...] = (100, 1_000, 10_000),
) -> list[dict]:
    """Measure token validation latency by component and cache size.

    Components measured independently:
      - expiry_check: token.is_expired()
      - action_hash_match: compare action hashes
      - replay_cache_lookup: token_id membership check in the replay set
      - signature_check: recompute SHA-256 and compare

    Full validation is also measured at each cache size.
    """
    set_log_path(Path("/dev/null"))
    results: list[dict] = []

    gate = VerifyCore()
    gate.load_policy_from_file(POLICY_PATH)

    # Pre-generate tokens for component benchmarks
    sample_tokens: list[tuple[AuthorizationToken, str]] = []
    for _ in range(WARMUP_ITERATIONS + iterations):
        req = _make_allowed_request()
        _, token = gate.evaluate(req)
        sample_tokens.append((token, req.canonical_hash()))
    gate._replay_cache.clear()

    # --- Per-component benchmarks (empty cache) ---

    # Expiry check
    def bench_expiry():
        t, _ = sample_tokens[WARMUP_ITERATIONS]
        t.is_expired()

    timings = _measure(bench_expiry, iterations)
    s = _stats(timings, unit="us")
    results.append({"metric": "component_expiry_check", "cache_size": 0,
                     "iterations": iterations, **s})

    # Action hash match
    def bench_hash_match():
        t, h = sample_tokens[WARMUP_ITERATIONS]
        _ = t.action_hash == h

    timings = _measure(bench_hash_match, iterations)
    s = _stats(timings, unit="us")
    results.append({"metric": "component_action_hash_match", "cache_size": 0,
                     "iterations": iterations, **s})

    # Signature check
    def bench_sig():
        t, _ = sample_tokens[WARMUP_ITERATIONS]
        payload = json.dumps(
            {
                "token_id": t.token_id,
                "action_hash": t.action_hash,
                "nonce": t.nonce,
                "policy_hash": t.policy_hash,
                "issued_at": t.issued_at,
                "expires_at": t.expires_at,
            },
            sort_keys=True,
        )
        _ = hashlib.sha256(payload.encode()).hexdigest() == t.signature

    timings = _measure(bench_sig, iterations)
    s = _stats(timings, unit="us")
    results.append({"metric": "component_signature_check", "cache_size": 0,
                     "iterations": iterations, **s})

    # --- Full validation at different replay cache sizes ---
    for cache_size in cache_sizes:
        gate_sized = VerifyCore()
        gate_sized.load_policy_from_file(POLICY_PATH)

        # Pre-populate the replay cache with *cache_size* dummy entries
        for i in range(cache_size):
            gate_sized._replay_cache.add(f"prefill_{i:08x}")

        # Generate fresh tokens for this run
        fresh_tokens: list[tuple[AuthorizationToken, str]] = []
        for _ in range(WARMUP_ITERATIONS + iterations):
            req = _make_allowed_request()
            _, tok = gate_sized.evaluate(req)
            fresh_tokens.append((tok, req.canonical_hash()))
        # Keep prefill entries, clear only the tokens we just added
        gate_sized._replay_cache = {
            tid for tid in gate_sized._replay_cache if tid.startswith("prefill_")
        }

        # Replay cache lookup only
        def bench_cache_lookup(g=gate_sized):
            t, _ = fresh_tokens[WARMUP_ITERATIONS]
            _ = t.token_id in g._replay_cache

        timings = _measure(bench_cache_lookup, iterations)
        s = _stats(timings, unit="us")
        results.append({"metric": f"component_replay_lookup_{cache_size}",
                         "cache_size": cache_size, "iterations": iterations, **s})

        # Full validate_token at this cache size
        validate_idx = WARMUP_ITERATIONS

        # Warmup
        for wi in range(WARMUP_ITERATIONS):
            t, h = fresh_tokens[wi]
            gate_sized.validate_token(t, h)
        gate_sized._replay_cache = {
            tid for tid in gate_sized._replay_cache if tid.startswith("prefill_")
        }
        validate_idx = WARMUP_ITERATIONS

        full_timings: list[float] = []
        for _ in range(iterations):
            t, h = fresh_tokens[validate_idx]
            start = time.perf_counter()
            gate_sized.validate_token(t, h)
            elapsed = time.perf_counter() - start
            full_timings.append(elapsed)
            validate_idx += 1

        s = _stats(full_timings, unit="us")
        results.append({"metric": f"full_token_validation_{cache_size}_cache",
                         "cache_size": cache_size, "iterations": iterations, **s})

    return results


# ------------------------------------------------------------------
# Output helpers
# ------------------------------------------------------------------

def print_results(results: list[dict]) -> None:
    if not results:
        return
    # Detect unit from the first result
    unit = "us" if "p50_us" in results[0] else "ms"
    label = "μs" if unit == "us" else "ms"
    p50_k, p95_k, p99_k = f"p50_{unit}", f"p95_{unit}", f"p99_{unit}"
    min_k, max_k, mean_k = f"min_{unit}", f"max_{unit}", f"mean_{unit}"

    print(f"\n{'Metric':<40} {'p50':>10} {'p95':>10} {'p99':>10} "
          f"{'min':>10} {'max':>10} {'mean':>10}")
    print("-" * 100)
    for r in results:
        print(
            f"{r['metric']:<40} "
            f"{r[p50_k]:>8.2f}{label} "
            f"{r[p95_k]:>8.2f}{label} "
            f"{r[p99_k]:>8.2f}{label} "
            f"{r[min_k]:>8.2f}{label} "
            f"{r[max_k]:>8.2f}{label} "
            f"{r[mean_k]:>8.2f}{label}"
        )
    print()


def write_csv(results: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return
    fields = list(results[0].keys())
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results written to {output}")


def _write_system_info_csv(output: Path) -> None:
    """Append system info as a separate CSV alongside benchmark results."""
    info_path = output.parent / (output.stem + "_system_info.csv")
    info = _system_info()
    with open(info_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        for k, v in info.items():
            writer.writerow([k, v])
    print(f"System info written to {info_path}")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description="Offlyn Verify Core — benchmark suite")
    parser.add_argument("--iterations", type=int, default=10000,
                        help="Number of iterations per benchmark")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output CSV path (overrides default per-mode paths)")
    parser.add_argument("--mode", choices=["all", "quick", "decision", "token"],
                        default="all",
                        help="Benchmark mode: 'all' (original), 'decision' (#6), "
                             "'token' (#7), 'quick' (original)")
    args = parser.parse_args()

    _print_system_info()
    print(f"Running benchmarks ({args.iterations} iterations each, "
          f"{WARMUP_ITERATIONS} warmup)...")
    print("NOTE: These are software-simulation measurements, not hardware "
          "measurements.\n")

    if args.mode in ("all", "quick"):
        results = run_benchmarks(args.iterations)
        print_results(results)
        out = args.output or RESULTS_DIR / "benchmark_results.csv"
        write_csv(results, out)
        _write_system_info_csv(out)

    if args.mode in ("all", "decision"):
        print("--- Decision latency with varying policy complexity ---")
        results = run_decision_latency_benchmarks(args.iterations)
        print_results(results)
        out = args.output if args.mode == "decision" else None
        out = out or RESULTS_DIR / "decision_latency_benchmark.csv"
        write_csv(results, out)
        _write_system_info_csv(out)

    if args.mode in ("all", "token"):
        print("--- Token validation with varying replay cache sizes ---")
        results = run_token_validation_benchmarks(args.iterations)
        print_results(results)
        out = args.output if args.mode == "token" else None
        out = out or RESULTS_DIR / "token_validation_benchmark.csv"
        write_csv(results, out)
        _write_system_info_csv(out)


if __name__ == "__main__":
    main()
