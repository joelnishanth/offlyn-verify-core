# Offlyn Verify Core — Evaluation Plan

## Objective

Demonstrate that the Actuation Boundary Enforcement Point (ABEP) prototype correctly enforces safety policies, detects attacks, and operates within acceptable latency bounds.

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

**Method**: Measure wall-clock time for `verify_policy()` across 1000 iterations.

### 4. Gate Decision Latency

**Definition**: Time from action request receipt to ALLOW/DENY decision.

**Target**: < 1 ms (software), < 100 μs (hardware target)

**Method**: Measure wall-clock time for `evaluate()` across 10,000 action requests with varying policy complexity.

### 5. Authorization Token Validation Latency

**Definition**: Time for the actuator to validate an authorization token.

**Target**: < 1 ms (software), < 50 μs (hardware target)

**Method**: Measure wall-clock time for `validate_token()` across 10,000 tokens.

### 6. Replay Detection

**Definition**: Percentage of replayed authorization tokens correctly rejected.

**Target**: 100%

**Method**: Issue tokens for allowed actions, then replay each token and verify rejection.

### 7. Rollback Resistance

**Definition**: Percentage of policy rollback attempts correctly rejected.

**Target**: 100%

**Method**: Load a policy with epoch N, then attempt to load policies with epochs < N and verify rejection.

### 8. Audit Completeness

**Definition**: Percentage of gate decisions (both ALLOW and DENY) recorded in the audit log.

**Target**: 100%

**Method**: Submit a mixed workload of safe and unsafe actions, then verify every decision appears in the JSONL audit log.

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

## Benchmarking Protocol

1. Run each latency benchmark in an isolated Python process
2. Discard the first 100 iterations (warm-up)
3. Report p50, p95, p99, and max latency
4. Run on a consistent machine (document CPU, RAM, OS)
5. Store results in `results/` as CSV for reproducibility

## Future Hardware Evaluation

When the prototype is mapped to hardware (TPM, FPGA, ASIC):

- Re-run all latency benchmarks on the target platform
- Measure power consumption per decision
- Measure gate throughput (decisions per second)
- Stress-test replay cache under bounded memory
- Verify fail-closed behavior under hardware fault injection
