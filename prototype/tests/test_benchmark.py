"""Lightweight tests for the benchmark module.

These verify the benchmark runs without errors and produces valid results,
not that the latency numbers meet any target (that depends on the machine).
"""

from gate.benchmark import run_benchmarks


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
