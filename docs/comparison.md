# Offlyn Verify Core — Comparison with Related Approaches

This document provides a structured comparison of Offlyn Verify Core against adjacent approaches in LLM robot safety, runtime assurance, and hardware-rooted enforcement. The goal is to position the Actuation Boundary Enforcement Point (ABEP) architecture relative to the closest related work.

## Approaches Compared

| Abbreviation | Full Name | Reference |
|---|---|---|
| **RoboGuard** | Safety Guardrails for LLM-Enabled Robots | Ravichandran et al., arXiv:2503.07885, 2025 |
| **SafeGate** | Pre-Execution Safety Gate and Task Safety Contracts | Obi et al., arXiv:2604.05427, 2026 |
| **ROSClaw** | An OpenClaw ROS 2 Framework for Agentic Robot Control | Cardenas et al., arXiv:2603.26997, 2026 |
| **ZTPM** | Zero Trust Policy Model for Agentic Cyber-Physical Systems | Ranathunga et al., arXiv:2605.25653, 2026 |
| **EHV** | Hardware-Rooted Zero-Trust Runtime Enforcement for Agentic AI | Sharma, arXiv:2605.17909, 2026 |
| **Simplex/RTA** | Runtime Assurance / Black-Box Simplex Architecture | Mehmood et al.; NASA NTRS 20240007986 |
| **CBF/Shielding** | Control Barrier Functions and Safe RL Shielding | Ames et al., 2019; Alshiekh et al., 2018 |
| **Offlyn VC** | Offlyn Verify Core | This project |

## Comparison Table: Trust Boundary and Enforcement

| Dimension | RoboGuard | SafeGate | ROSClaw | ZTPM | EHV | Simplex/RTA | CBF/Shielding | **Offlyn VC** |
|---|---|---|---|---|---|---|---|---|
| **Trust boundary location** | Planner level | Pre-execution | ROS middleware | Policy boundary | TEE runtime | Controller switch | Control input filter | **Actuation boundary** |
| **Policy format** | Temporal logic constraints | Task safety contracts | Action validators | Typed zero-trust primitives | Machine-readable policies | Safety controller specs | Mathematical safe sets | **Signed YAML capsules (Ed25519)** |
| **Hardware dependency** | None | None | None | None | TEE / secure enclave | Varies (some HW) | None | **Simulated → TPM/FPGA/ASIC path** |
| **Fail mode** | Planner constraint | Pre-execution reject | Middleware reject | Policy deny | TEE enforcement | Controller fallback | Modified control input | **Fail-closed (deny by default)** |
| **Replay protection** | — | — | — | — | — | — | — | **Yes (token ID cache + expiry)** |
| **Rollback defense** | — | — | — | — | — | — | — | **Yes (monotonic policy epoch)** |
| **Audit model** | — | — | Structured logs | — | Machine-readable logs | — | — | **Tamper-evident hash chain (SHA-256)** |
| **Actuator binding** | None | None | Middleware level | Policy boundary | Not robot-specific | Controller authority | None | **Token-gated (actuator rejects without gate token)** |

## Comparison Table: Feature Coverage

| Feature | RoboGuard | SafeGate | ROSClaw | ZTPM | EHV | Simplex/RTA | CBF/Shielding | **Offlyn VC** |
|---|---|---|---|---|---|---|---|---|
| **Robot-focused** | Yes | Yes | Yes | Yes | General agents | Varies | Varies | **Yes** |
| **LLM-aware** | Yes | Yes | Yes | Yes | Yes | No | No | **Yes** |
| **Enforcement placement** | Planner | Pre-execution | Middleware | Policy model | TEE | Controller | Control input | **Actuation boundary** |
| **Hardware-rooted boundary** | No | No | No | No | Yes | Varies | No | **Simulated / hardware path** |
| **Signed policy capsules** | — | — | — | — | Yes | — | — | **Yes (Ed25519)** |
| **Replay defense** | — | — | — | — | — | — | — | **Yes** |
| **Rollback defense** | — | — | — | — | — | — | — | **Yes** |
| **Open artifact** | No | No | Partial | No | No | Varies | Varies | **Yes (MIT)** |

## Key Distinctions

### Where Offlyn Verify Core differs

1. **Enforcement at the actuation boundary, not the planner or middleware.** Most approaches enforce safety constraints upstream — at the LLM prompt level, planning level, or ROS middleware level. Offlyn Verify Core places the final mandatory authorization point between the software stack and the physical actuator, so that even a compromised host cannot release unauthorized commands.

2. **Explicit replay and rollback defenses.** Token-based replay protection (short-lived tokens with unique IDs and a replay cache) and monotonic policy epochs for rollback defense are not present in the compared approaches. These defenses matter when the attacker has access to the host software.

3. **Tamper-evident audit log.** The hash-chained JSONL audit log detects insertion, deletion, or modification of any entry. Most compared approaches either lack audit logging or use append-only logs without tamper-evidence chaining.

4. **Hardware implementation path.** While the current artifact is a software simulation, the architecture is designed for staged progression to TPM-backed signing, microcontroller gate, FPGA, and ASIC implementations. EHV also targets hardware, but is not robot-specific.

5. **Actuator-side token validation.** The actuator itself rejects commands that lack a valid gate token. This is a second enforcement point that prevents direct bypass.

### Where other approaches are stronger

1. **RoboGuard and SafeGate** reason about task-level semantics, temporal constraints, and safety contracts that a small deterministic gate cannot evaluate. They are better suited for catching semantically unsafe plans before they reach the actuation layer.

2. **CBF/Shielding** provides mathematically grounded safety guarantees over continuous state spaces and dynamics. Offlyn Verify Core checks bounded predicates, not dynamical invariants.

3. **Simplex/RTA** can switch to a verified safe controller at runtime, providing active recovery rather than just deny/allow decisions.

4. **ROSClaw** provides deep ROS 2 integration with dynamic capability discovery, observation normalization, and structured middleware hooks that Offlyn Verify Core does not attempt.

5. **ZTPM** provides a richer typed policy model with physical impact tiers and capability attestation for general agentic cyber-physical systems.

### Complementarity

These approaches are **not mutually exclusive**. The intended deployment is a layered safety stack:

```
LLM / Agent Planner
    ↓  (RoboGuard / SafeGate: semantic safety checks)
Executive / Middleware
    ↓  (ROSClaw: ROS 2 validation + audit)
    ↓  (CBF/Shielding: control input filtering)
Actuation Boundary
    ↓  (Offlyn Verify Core: hardware-rooted final authorization)
Physical Actuator
```

Each layer addresses threats that the others cannot. Offlyn Verify Core is the last line of defense, not a replacement for upstream safety reasoning.

## Comparison Dimensions Explained

| Dimension | Definition |
|---|---|
| **Trust boundary location** | Where the enforcement point sits in the robot software/hardware stack |
| **Policy format** | How safety rules are expressed and consumed by the enforcement point |
| **Hardware dependency** | Whether the approach requires or targets hardware-rooted enforcement |
| **Fail mode** | What happens when the enforcement point cannot reach a decision or encounters an error |
| **Replay protection** | Whether the system detects and rejects replayed commands or tokens |
| **Rollback defense** | Whether the system prevents loading older, more permissive policies |
| **Audit model** | How decisions are recorded and whether the records are tamper-evident |
| **Actuator binding** | Whether the actuator independently validates authorization before executing |
