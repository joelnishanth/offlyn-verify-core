# SilicaFold Reference Strategy for VerifyCore

## Purpose

SilicaFold is a narrow hardware-backed reference artifact for VerifyCore. It demonstrates that part of the policy-at-actuation-boundary concept can be represented as deterministic hardware and tested through RTL/TinyTapeout workflows.

SilicaFold should be published first as a narrow, hardware-backed TinyTapeout / RTL / post-silicon data paper. VerifyCore should use SilicaFold as a supporting reference artifact, not as the full VerifyCore implementation. VerifyCore is the broader patent and publication target.

## Relationship Between Repositories

| Repository | Purpose | URL |
|------------|---------|-----|
| SilicaFold | Hardware primitive / evidence artifact | https://github.com/offlyn-ai/silicafold-offlyn.ai-chip |
| VerifyCore | Broader policy-at-actuation-boundary architecture | https://github.com/joelnishanth/offlyn-verify-core |

Key relationship:

- **SilicaFold** is the hardware primitive / evidence artifact
- **VerifyCore** is the broader policy-at-actuation-boundary architecture
- SilicaFold should be cited as supporting evidence, not as the full VerifyCore implementation
- SilicaFold provides narrow public evidence for a deterministic, hardware-reducible policy-at-actuation-boundary primitive
- Do not overclaim SilicaFold as production security, cryptographic enforcement, tamper resistance, or the complete VerifyCore stack

## What SilicaFold Can Support

| SilicaFold Evidence | VerifyCore Claim Theme | Safe Interpretation | Limitation |
|---------------------|------------------------|---------------------|------------|
| PolicyGate RTL decision tree | Hardware policy gate | A deterministic policy decision primitive can be represented in RTL | Does not prove full policy lifecycle, signing, or verification |
| HIGH risk requires human approval | Human-in-the-loop escalation | Escalation logic can be hardware-enforced at decision time | Does not prove authenticated notification channel or UI |
| EMERGENCY path scoped to safety-critical tools | Emergency override control | Emergency path can be scoped and hardware-gated | Does not prove secure boot, authentication, or tamper resistance |
| Offline medium-risk logging | Offline audit trail | Audit counter can increment on decision | Does not prove append-only digest, signed log, or tamper-evident storage |
| Audit counter persistence | Audit trail evidence | Hardware counter provides monotonic evidence | Does not prove log integrity, replay protection, or external verification |
| TensorTile context scoring | Context attestation | Context can inform gate decision | Does not prove authenticated context source or cryptographic binding |
| Compute/authority separation | Compute/authority boundary | Compute and authority can be separated at RTL level | Does not prove full isolation, authenticated channel, or secure boot |
| TinyTapeout hardware publication path | Hardware-backed evidence | A policy primitive can be fabricated in open silicon | Does not prove production-grade security, certification, or tamper resistance |

## What SilicaFold Does Not Prove

SilicaFold V0 does **not** demonstrate or provide evidence for:

- Production security
- Cryptographic policy verification
- Secure boot / measured boot
- Authenticated pins or command channels
- Replay protection (beyond counter increment)
- Append-only audit digests with cryptographic integrity
- Tamper resistance or physical security
- Full VerifyCore system behavior
- Regulatory or safety certification
- Protection against physical attacks, side-channel attacks, or fault injection
- Key management or policy signing authority

These capabilities are part of the broader VerifyCore architecture and should be addressed in separate patent filings, future papers, and production implementations.

## Patent-Safety Guidance

**Important**: Public repositories and documentation are not substitutes for patent protection.

1. **This repository is not a patent filing.** Public docs should not be treated as a substitute for provisional or non-provisional patent applications.

2. **File before broad disclosure.** File or coordinate patent materials before broad public disclosure of claims that go beyond the implemented SilicaFold V0 evidence.

3. **Keep broad claims in patent materials.** Broad system claims should remain in patent materials and carefully scoped VerifyCore papers. Public repos should contain only what is safe to disclose.

4. **Use SilicaFold as reduction-to-practice evidence only where accurate.** SilicaFold demonstrates a narrow hardware primitive. It does not demonstrate the full VerifyCore enforcement stack.

5. **Coordinate with patent counsel.** Before publishing claim language that goes beyond the implemented public evidence, coordinate with patent counsel to ensure IP protection.

6. **Do not disclose proprietary implementation details.** Keep proprietary VerifyCore implementation details out of public repositories.

## Citation Guidance

When citing SilicaFold in VerifyCore materials:

```
SilicaFold is a TinyTapeout-scale hardware prototype that demonstrates a narrow,
deterministic policy-gate primitive for structured agent actions. It is not the
full VerifyCore system. Instead, it provides hardware-backed evidence that a
policy-at-actuation-boundary decision primitive can be represented in RTL,
validated with reproducible tests, and prepared for open silicon workflows.
```

When citing in BibTeX:

```bibtex
@misc{silicafold2026,
  author = {Ponukumatla, Joel Nishanth and Natarajan, Rahul},
  title = {SilicaFold: A TinyTapeout Hardware Primitive for Policy-Gated Offline AI Actuation},
  year = {2026},
  note = {Draft / forthcoming hardware-backed data paper, Offlyn.ai},
  url = {https://github.com/offlyn-ai/silicafold-offlyn.ai-chip}
}
```
