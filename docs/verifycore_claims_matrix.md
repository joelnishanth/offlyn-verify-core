# VerifyCore Claims Matrix

This document maps VerifyCore claim themes to available evidence, safe public claims, and areas requiring patent or future work protection.

## Claims Matrix

| VerifyCore Claim Theme | SilicaFold Supporting Evidence | What Can Be Publicly Claimed Now | What Should Remain Patent/Future Work | Risk of Overclaiming |
|------------------------|-------------------------------|----------------------------------|--------------------------------------|---------------------|
| **Policy at actuation boundary** | PolicyGate RTL implements decision tree between planner and actuator | A deterministic policy gate can mediate action requests at the actuation boundary; software prototype demonstrates fail-closed semantics | Full hardware enforcement stack, production deployment architecture, integration with industrial robot buses | Medium — public claim is well-supported by prototype |
| **Structured action normalization** | PolicyGate accepts structured action requests with defined fields | Actions can be canonicalized into structured requests for policy evaluation | Normalization engine implementation, schema evolution, integration with ROS/middleware | Low — demonstrated in prototype |
| **Hardware policy gate** | SilicaFold TinyTapeout RTL demonstrates policy decision primitive | A policy decision primitive can be represented in RTL and prepared for open silicon | Full ASIC implementation, production-grade timing, power, area targets | High — SilicaFold is narrow evidence; do not claim full hardware VerifyCore |
| **Human-in-the-loop escalation** | HIGH risk tier requires human approval in SilicaFold | Escalation logic can be hardware-gated | Authenticated notification channel, UI implementation, escalation policy management | Medium — logic is demonstrated; channel security is not |
| **Emergency override control** | EMERGENCY path scoped to safety-critical tools in SilicaFold | Emergency paths can be scoped and hardware-gated | Secure boot for emergency policy, authenticated override channels, tamper resistance | High — do not claim secure emergency override without further evidence |
| **Offline audit trail** | Audit counter increments on SilicaFold decisions | Hardware counter provides monotonic decision evidence | Append-only digest with cryptographic integrity, tamper-evident storage, external verification | High — counter is not a secure audit log |
| **Signed policy lifecycle** | Ed25519 signing demonstrated in software prototype | Policies can be signed and verified before loading | HSM key management, TPM attestation path, secure policy provisioning | Medium — signing is demonstrated; key management is not |
| **Context attestation** | TensorTile context scoring in SilicaFold | Context can inform policy gate decisions | Authenticated context source, cryptographic binding of context to decision, trusted sensor path | High — context source authentication is not demonstrated |
| **Authenticated hardware command channel** | Compute/authority separation in SilicaFold RTL | Compute and authority can be separated at hardware level | Full authenticated channel implementation, bus-level authentication, secure boot | High — separation is demonstrated; authentication is not |
| **Replay protection** | Nonce and replay cache in software prototype; counter in SilicaFold | Replay detection is possible via nonce checking and monotonic counters | Hardware monotonic counter with tamper resistance, bounded replay cache with guaranteed eviction | Medium — mechanism is demonstrated; hardware guarantees are not |
| **Secure boot / measured boot** | Not implemented | — | Full measured boot chain, TPM attestation, firmware integrity verification | Critical — do not claim without implementation |
| **Append-only audit digest** | Not implemented | Audit logging with hash chaining demonstrated in software prototype | Cryptographic append-only log with external verification, tamper-evident hardware storage | Critical — hash chaining is not append-only hardware |
| **Offline/edge AI agent enforcement** | SilicaFold demonstrates offline-capable gate | A policy gate can operate without network connectivity | Secure offline policy updates, offline attestation, sync-on-reconnect protocols | Medium — offline capability is demonstrated; secure update is not |

## Claim Discipline Guidelines

### Safe Public Claims

The following claims are well-supported by current evidence and can be made publicly:

1. VerifyCore defines an Actuation Boundary Enforcement Point (ABEP) abstraction
2. A software prototype demonstrates fail-closed policy enforcement
3. Signed policy capsules can be verified before loading
4. Replay and rollback attacks can be detected and blocked
5. The architecture reduces the trusted computing base for action authorization
6. SilicaFold demonstrates that a narrow policy primitive can be represented in RTL

### Claims Requiring Caution

The following claims require careful framing and should reference limitations:

1. "Hardware-rooted" — clarify that current implementation is software simulation with hardware path planned
2. "Tamper-resistant" — applies to hardware targets, not current prototype
3. "Audit integrity" — hash chaining is demonstrated, but not hardware-enforced append-only storage
4. "Context attestation" — context influences decisions, but authenticated context binding is future work

### Claims to Avoid

The following claims should not be made without additional evidence or patent protection:

1. "Tamper-proof" — no implementation is tamper-proof
2. "Cryptographically secure" — without specifying what is secured and against what threat
3. "Production ready" — current artifact is a research prototype
4. "Certified" or "compliant" — no safety certification has been obtained
5. "Guarantees safety" — no system can guarantee safety without defining scope and assumptions
6. "Prevents malicious agents" — the system prevents unauthorized actions, not all malicious behavior
7. "Full hardware VerifyCore" — SilicaFold is a narrow primitive, not the full stack
8. "Patented" — do not claim patent protection unless a patent has been granted

## Review Checklist

Before publishing any VerifyCore or SilicaFold material, verify:

- [ ] Claims are supported by implemented and tested evidence
- [ ] Hardware claims distinguish between software prototype and hardware targets
- [ ] SilicaFold is cited as narrow evidence, not full implementation
- [ ] Limitations section clearly states what is not implemented
- [ ] Patent-sensitive claims are not publicly disclosed before filing
- [ ] Terminology uses "prototype," "evidence," "demonstration" rather than "production," "secure," "guaranteed"
