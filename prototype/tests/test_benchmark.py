"""Lightweight tests for the benchmark module.

These verify the benchmark runs without errors and produces valid results,
not that the latency numbers meet any target (that depends on the machine).
"""

from gate.benchmark import (
    run_benchmarks,
    run_decision_latency_benchmarks,
    run_token_validation_benchmarks,
    _system_info,
)


def test_benchmark_runs_and_returns_results() -> None:
    results = run_benchmarks(iterations=50)
    assert len(results) == 5
    for r in results:
        assert "metric" in r
        assert r["iterations"] == 50
        assert r["p50_ms"] >= 0
        assert r["p99_ms"] >= r["p50_ms"]
        assert r["mean_ms"] > 0


def test_benchmark_metric_names() -> None:
    results = run_benchmarks(iterations=10)
    names = {r["metric"] for r in results}
    assert names == {
        "policy_load_and_verify",
        "gate_decision_allow",
        "gate_decision_deny",
        "token_validation",
        "replay_detection",
    }


def test_decision_latency_varying_complexity() -> None:
    rule_counts = (1, 5, 20)
    results = run_decision_latency_benchmarks(iterations=10, rule_counts=rule_counts)
    assert len(results) == len(rule_counts) * 2  # allow + deny per rule count
    for r in results:
        assert "num_rules" in r
        assert r["iterations"] == 10
        assert r["p50_us"] >= 0
        assert r["p99_us"] >= r["p50_us"]
        assert r["mean_us"] > 0


def test_decision_latency_metric_names() -> None:
    results = run_decision_latency_benchmarks(iterations=10, rule_counts=(1, 5))
    names = {r["metric"] for r in results}
    assert names == {
        "decision_allow_1_rules",
        "decision_deny_1_rules",
        "decision_allow_5_rules",
        "decision_deny_5_rules",
    }


def test_token_validation_varying_cache() -> None:
    results = run_token_validation_benchmarks(
        iterations=10, cache_sizes=(100, 1_000)
    )
    assert len(results) > 0
    for r in results:
        assert r["iterations"] == 10
        assert r["p50_us"] >= 0
        assert r["mean_us"] > 0


def test_token_validation_has_component_metrics() -> None:
    results = run_token_validation_benchmarks(
        iterations=10, cache_sizes=(100,)
    )
    names = {r["metric"] for r in results}
    assert "component_expiry_check" in names
    assert "component_action_hash_match" in names
    assert "component_signature_check" in names
    assert "component_replay_lookup_100" in names
    assert "full_token_validation_100_cache" in names


def test_system_info() -> None:
    info = _system_info()
    assert "python_version" in info
    assert "os" in info
    assert "machine" in info
