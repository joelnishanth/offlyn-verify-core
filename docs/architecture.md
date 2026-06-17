# Offlyn Verify Core — Architecture

## Overview

Offlyn Verify Core implements an **Actuation Boundary Enforcement Point (ABEP)** — a small, deterministic gate placed between an AI planner and robot actuators. The gate enforces signed policy capsules and issues short-lived authorization tokens for every allowed action. Actuators refuse commands that do not carry a valid token.

## Components

### AI Planner

The planner generates proposed actions (e.g., "move joint_2 to 45° at speed 0.4"). In the prototype, the planner is a deterministic simulator. In production, this would be an LLM-based or agentic planning system.

The planner **cannot talk directly to the actuator**. Every proposed action must pass through the Verify Core gate.

### Verify Core Gate

The central enforcement point. It:

1. **Loads only signed policies** — unsigned or tampered policies are rejected.
2. **Rejects policy rollback** — a policy with a lower epoch than the current one is denied.
3. **Evaluates every action request** against the loaded policy.
4. **Issues authorization tokens** for allowed actions — tokens are bound to the specific action hash, nonce, and policy hash.
5. **Maintains a replay cache** — tokens cannot be reused.
6. **Logs every decision** to an append-only audit log.

### Decision Engine

A pure, deterministic evaluator that checks:

1. **Actor identity** — is this planner authorized by the policy?
2. **Action/target match** — does the policy contain a rule for this action and target?
3. **Speed bounds** — is the requested speed within the limit?
4. **Angle bounds** — is the requested angle within the allowed range?
5. **Zone allowance** — is the robot in an allowed zone?
6. **Human proximity** — is movement denied when a human is nearby?

If any check fails, the request is denied immediately (**fail-closed**).

### Signed Policy Capsule

A YAML file compiled into a canonical byte representation, then signed with an Ed25519 key. The policy defines:

- Allowed actors
- Allowed actions and targets
- Physical bounds (speed, angle, altitude)
- Allowed zones
- Human-proximity constraints
- Policy epoch (monotonically increasing, prevents rollback)

### Authorization Token

A short-lived (5-second) token issued for each ALLOW decision. It contains:

- Token ID (unique)
- Action hash (binds to the specific action)
- Nonce (binds to the specific request)
- Policy hash (binds to the policy version)
- Expiration time
- HMAC signature

The actuator validates every field before executing.

### Actuator Simulator

The actuator is the final enforcement point. It:

- **Refuses commands without a token** (direct bypass rejected)
- **Validates token signature**
- **Checks expiration**
- **Checks action hash match** (token cannot be used for a different action)
- **Checks replay cache** (token cannot be reused)

### Audit Log

Every ALLOW and DENY decision is written to an append-only JSONL log. Each entry includes timestamp, actor, action, target, nonce, action hash, decision, and reason.

## Why Fail-Closed

The gate defaults to DENY. If:

- No policy is loaded → DENY
- Policy signature is invalid → policy not loaded
- No matching rule → DENY
- Any bound exceeded → DENY
- Token missing → actuator rejects
- Token invalid → actuator rejects

There is no path from the planner to the actuator that bypasses the gate.

## Mapping to Hardware

This software prototype models an architecture that maps to:

| Prototype Component | Hardware Target |
|---|---|
| Verify Core gate | TPM, secure enclave, FPGA, or ASIC |
| Policy capsule signing | HSM or secure boot chain |
| Replay cache | Hardware monotonic counter + bounded cache |
| Audit log | Tamper-evident storage (signed hash chain) |
| Actuator gate | Hardware I/O interlock (safety relay, FPGA I/O cell) |

The software simulation allows the architecture to be tested, evaluated, and refined before committing to silicon.
