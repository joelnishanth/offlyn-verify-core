# Offlyn Verify Core — Evaluation Plan

## Objective

Demonstrate that the Actuation Boundary Enforcement Point (ABEP) prototype correctly enforces safety policies, detects attacks, operates within acceptable latency bounds, and maintains audit integrity.

## Metrics

### 1. Unsafe Command Block Rate

**Definition**: Percentage of policy-violating actions correctly denied by the gate.

**Target**: 100% (fail-closed design)

**Method**: Submit a test suite of known-unsafe actions (speed violations, angle violations, zone violations, human-proximity violations) and verify all are denied.

### 2. False Positive Rate

**Definition**: Percentage of safe, policy-conforming actions incorrectly denied.

**Target**: 0%

**Method**: Submit a test suite of known-safe actions and verify all are allowed.

### 3. Policy Verification Latency

**Definition**: Time to verify a signed policy's Ed25519 signature and load it.

**Target**: < 10 ms (software), < 1 ms (hardware target)

**Method**: Measure wall-clock time for `load_policy()` across configurable iterations using `gate.benchmark`.

### 4. Gate Decision Latency

**Definition**: Time from action request receipt to ALLOW/DENY decision.

**Target**: < 1 ms (software), < 100 μs (hardware target)

**Method**: Measure wall-clock time for `evaluate()` across configurable iterations, separately for allowed and denied actions.

### 5. Authorization Token Validation Latency

**Definition**: Time for the actuator to validate an authorization token.

**Target**: < 1 ms (software), < 50 μs (hardware target)

**Method**: Measure wall-clock time for `validate_token()` across configurable iterations.

### 6. Replay Detection Latency

**Definition**: Time to detect and reject a replayed authorization token.

**Target**: < 1 ms (software)

**Method**: Replay a previously used token and measure rejection time across configurable iterations.

### 7. Rollback Resistance

**Definition**: Percentage of policy rollback attempts correctly rejected.

**Target**: 100%

**Method**: Load a policy with epoch N, then attempt to load policies with epochs < N and verify rejection.

### 8. Audit Completeness

**Definition**: Percentage of gate decisions (both ALLOW and DENY) recorded in the audit log.

**Target**: 100%

**Method**: Submit a mixed workload of safe and unsafe actions, then verify every decision appears in the JSONL audit log.

### 9. Audit Chain Integrity

**Definition**: Ability to detect tampering with the audit log via hash chain verification.

**Target**: 100% detection of modified, inserted, or deleted entries

**Method**: Generate an audit log, tamper with individual entries, and verify that `audit_verify.py` detects the break point. The hash chain uses SHA-256 with each entry hashing the canonical content concatenated with the previous entry's hash, starting from a known genesis hash.

## Test Scenarios

| # | Scenario | Expected | Metric |
|---|---|---|---|
| 1 | Safe movement within bounds | ALLOW | False positive rate |
| 2 | Speed exceeds limit | DENY | Block rate |
| 3 | Angle out of range | DENY | Block rate |
| 4 | Forbidden zone | DENY | Block rate |
| 5 | Human nearby + movement | DENY | Block rate |
| 6 | Unsigned policy load | REJECT | Policy integrity |
| 7 | Tampered signed policy | REJECT | Policy integrity |
| 8 | Policy rollback (lower epoch) | REJECT | Rollback resistance |
| 9 | Replay authorization token | REJECT | Replay detection |
| 10 | Direct actuator bypass | REJECT | Architectural enforcement |
| 11 | Forged authorization token | REJECT | Token integrity |
| 12 | Expired authorization token | REJECT | Token freshness |
| 13 | Tampered audit log entry | DETECTED | Audit chain integrity |
| 14 | Deleted audit log entry | DETECTED | Audit chain integrity |

## Benchmarking Protocol

1. Run benchmarks using `python -m gate.benchmark --iterations N`
2. The first 100 iterations are discarded as warmup
3. Report p50, p95, p99, min, max, and mean latency in milliseconds
4. Run on a consistent machine (document CPU, RAM, OS, Python version)
5. Store results in `results/benchmark_results.csv`

## Software Simulation vs. Hardware Measurements

All latency numbers produced by `gate.benchmark` are **software-simulation measurements** on a general-purpose CPU running Python. They reflect the algorithmic cost of each operation but do not represent the performance of a hardware implementation.

Hardware targets (see [hardware_mapping.md](hardware_mapping.md)):

| Operation | Software (Python) | MCU target | FPGA target | ASIC target |
|---|---|---|---|---|
| Policy verification | ~1 ms | ~10 ms | < 1 ms | < 100 μs |
| Gate decision | ~0.05 ms | ~1 ms | < 10 μs | < 1 μs |
| Token validation | ~0.03 ms | ~0.5 ms | < 5 μs | < 1 μs |
| Replay detection | ~0.01 ms | ~0.1 ms | < 1 μs | < 0.1 μs |

These hardware targets are estimates based on comparable operations in TPM, FPGA, and ASIC literature. Actual measurements will be reported when hardware prototypes are available.

## Future Hardware Evaluation

When the prototype is mapped to hardware (TPM, FPGA, ASIC):

- Re-run all latency benchmarks on the target platform
- Measure power consumption per decision
- Measure gate throughput (decisions per second)
- Stress-test replay cache under bounded memory
- Verify fail-closed behavior under hardware fault injection
- Verify audit chain integrity under power-loss scenarios
