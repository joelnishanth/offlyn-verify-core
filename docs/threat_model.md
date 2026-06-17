# Offlyn Verify Core — Threat Model

## Scope

This threat model covers the actuation boundary between an AI planner and robot actuators. The attacker's goal is to cause the robot to execute an unauthorized physical action.

## Attacker Capabilities

| Capability | Assumed? | Rationale |
|---|---|---|
| Control or confuse the AI planner | Yes | LLMs are susceptible to prompt injection, jailbreaking, and hallucination |
| Propose malformed or unsafe actions | Yes | A compromised planner can generate arbitrary action requests |
| Intercept action requests in transit | Yes | Software-level man-in-the-middle within the autonomy stack |
| Attempt to replay a valid authorization | Yes | Network replay or software-level token capture |
| Attempt policy rollback | Yes | Load an older, more permissive policy to widen the attack surface |
| Attempt unsigned policy update | Yes | Inject a policy without proper signing authority |
| Forge signing keys | No | Ed25519 keys are assumed to be generated and stored securely |
| Directly modify Verify Core runtime state | No | In hardware: the gate is in a separate trust domain (TPM/enclave/FPGA) |
| Physically tamper with the gate hardware | No | Out of scope for this prototype (addressed by physical security) |

## Threats and Mitigations

### T1: Compromised Planner Proposes Unsafe Action

**Attack**: The AI planner, influenced by adversarial input or hallucination, proposes an action that exceeds physical safety bounds (e.g., excessive speed, forbidden zone).

**Mitigation**: The Verify Core gate evaluates every action against the signed policy. Out-of-bounds actions are denied. The planner has no path to the actuator that bypasses the gate.

### T2: Planner Bypasses Gate (Direct Actuator Access)

**Attack**: The planner attempts to send commands directly to the actuator, circumventing the Verify Core gate.

**Mitigation**: The actuator simulator only accepts commands that include a valid, unexpired authorization token from the gate. Commands without tokens are rejected unconditionally.

### T3: Replay Attack

**Attack**: An attacker captures a valid authorization token and replays it to execute the same action again (or a different action).

**Mitigation**:
- Tokens are bound to a specific action hash — they cannot be used for a different action.
- The gate maintains a replay cache — used token IDs are rejected.
- Tokens have a short lifetime (5 seconds) — expired tokens are rejected.

### T4: Policy Rollback

**Attack**: An attacker loads an older, more permissive policy (with a lower epoch) to widen the allowed action space.

**Mitigation**: The gate tracks the current policy epoch and rejects any policy with a lower epoch. Policy epochs are monotonically increasing.

### T5: Unsigned Policy Update

**Attack**: An attacker injects a policy that was not signed by the authorized signing key.

**Mitigation**: The gate verifies the Ed25519 signature on every policy before loading. Unsigned policies are rejected. Policies with invalid signatures (tampered content) are rejected.

### T6: Modified Signed Policy

**Attack**: An attacker modifies the content of a signed policy (e.g., changing speed limits) without re-signing.

**Mitigation**: The signature covers the canonical byte representation of the policy. Any modification invalidates the signature. The gate rejects the modified policy.

### T7: Token Forgery

**Attack**: An attacker constructs a fake authorization token to bypass the gate.

**Mitigation**: Tokens include an HMAC signature computed by the gate. The actuator verifies the signature before accepting the token. Forged signatures do not match.

### T8: Nonce Collision

**Attack**: An attacker generates a request with the same nonce as a previous request to confuse the replay cache.

**Mitigation**: Nonces are UUIDv4 (128-bit random). Collision probability is negligible. The replay cache checks token_id, not just nonce.

## Trust Boundaries

```
┌─────────────────────────────────────────────┐
│  UNTRUSTED DOMAIN                           │
│  ┌───────────────────┐                      │
│  │   AI Planner      │  ← attacker can      │
│  │   (LLM/Agent)     │    control this       │
│  └────────┬──────────┘                      │
│           │ action request                   │
├───────────┼─────────────────────────────────┤
│  TRUST BOUNDARY (Actuation Boundary)        │
│           │                                  │
│  ┌────────▼──────────┐                      │
│  │   Verify Core     │  ← deterministic,    │
│  │   Gate (ABEP)     │    isolated,          │
│  └────────┬──────────┘    tamper-resistant   │
│           │ authorized command               │
│  ┌────────▼──────────┐                      │
│  │   Actuator        │  ← validates token   │
│  │                   │    before executing   │
│  └───────────────────┘                      │
│  TRUSTED DOMAIN                              │
└─────────────────────────────────────────────┘
```

## Residual Risks

1. **Side-channel attacks** on the gate hardware (out of scope for software prototype)
2. **Denial of service** — an attacker flooding the gate with requests could degrade throughput (mitigated by rate limiting in production)
3. **Policy correctness** — the gate enforces whatever the policy says; if the policy is too permissive, unsafe actions may be allowed
4. **Clock manipulation** — token expiry depends on system time; in hardware this would use a monotonic hardware clock
