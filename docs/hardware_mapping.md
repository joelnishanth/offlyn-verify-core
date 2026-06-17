# Offlyn Verify Core — Hardware Mapping

## Overview

This document describes the staged path from software prototype to hardware enforcement. The current implementation is **Stage 0** and should not be represented as completed silicon or a shipping hardware product.

## Stages

### Stage 0: Software Simulation (current)

The prototype in `prototype/` is a pure-Python simulation of the Verify Core gate architecture. It demonstrates:

- Signed policy capsule loading and verification (Ed25519)
- Deterministic action evaluation against policy rules
- Short-lived, action-bound authorization token issuance
- Replay cache for token reuse prevention
- Monotonic policy epoch enforcement (rollback defense)
- Tamper-evident audit log with hash chaining
- Actuator simulator that refuses commands without valid gate tokens

**What this stage proves**: The architecture, interfaces, fail-closed semantics, and defense properties are correct and testable. All threat model scenarios pass in software.

**What this stage does not prove**: Latency under real-time constraints, tamper resistance under physical attack, or behavior on resource-constrained hardware.

### Stage 1: TPM-backed Signing and Attestation

Replace the demo Ed25519 key pair with TPM 2.0-backed key storage:

- Policy signing keys generated and stored inside a TPM
- Remote attestation of the signing environment
- Policy verification on the robot uses the TPM-attested public key
- Key provisioning workflow documented and reproducible
- Signing authority is separated from the robot runtime

**Target hardware**: Any platform with a TPM 2.0 module (most modern x86 and ARM SBCs).

**What this stage adds**: Hardware-rooted trust for the policy signing chain. The signing key cannot be extracted from the TPM, so even a compromised host cannot forge new policies without physical access to the signing machine.

### Stage 2: Microcontroller-mediated Actuator Release

Move the Verify Core gate logic onto a dedicated microcontroller that sits between the host and the actuator bus:

- Raspberry Pi Pico (RP2040), ESP32, or STM32 as the gate processor
- Serial/UART or SPI interface to the host for receiving action requests
- GPIO or relay output to the actuator bus — the host cannot drive actuators directly
- Policy evaluation in C or MicroPython on the microcontroller
- Hardware monotonic counter for replay protection (flash wear-leveled counter or EEPROM)
- LED or GPIO status indicator for ALLOW/DENY

**What this stage adds**: Physical separation of the gate from the host OS and autonomy stack. The host cannot bypass the gate by writing directly to the actuator bus — the microcontroller controls the physical connection.

**Limitations**: Microcontroller flash is writable via JTAG/SWD. Physical tamper resistance requires additional measures (epoxy, secure boot, fuse bits).

### Stage 3: FPGA Implementation of Deterministic Policy Checks

Implement the gate decision logic in RTL on an FPGA:

- Lattice iCE40, Xilinx Artix-7, or similar low-cost FPGA
- Policy rules compiled into lookup tables or content-addressable memory
- Sub-microsecond decision latency for bounded rule sets
- Hardware replay counter (monotonic, non-volatile)
- Physical I/O gating: actuator control signals pass through FPGA fabric
- Bitstream signed and authenticated at boot

**What this stage adds**: Deterministic, constant-time policy evaluation. The gate logic is not software — it cannot be modified by the host at runtime. Attack surface is reduced to the bitstream provisioning chain.

**Limitations**: FPGA bitstream can be reflashed if the attacker has physical access and the bitstream authentication fuse is not burned.

### Stage 4: ASIC / Tiny Tapeout-style Primitive

Map the gate logic to fixed-function silicon:

- Tiny Tapeout or a small ASIC shuttle for the core decision comparators
- Hardwired policy-rule slots (e.g., 8–16 configurable rules loaded at provisioning)
- Monotonic hardware counter in OTP or NV fuse
- Power budget suitable for battery-powered robots or drones
- The gate logic is immutable after fabrication — no firmware to compromise

**What this stage adds**: The strongest tamper resistance. The gate behavior is defined by the physical layout of transistors. There is no software layer to exploit, no firmware to reflash, no OS to compromise.

**Limitations**: Fixed-function silicon is inflexible. Policy rule format and count must be defined at design time. Updates require reprovisioning or a new chip revision. This is appropriate only for the narrowest, most safety-critical enforcement checks.

## Current Status

| Stage | Status | Tracked In |
|---|---|---|
| Stage 0: Software simulation | **Complete** | This repository |
| Stage 1: TPM-backed signing | Planned | [Issue #3](https://github.com/joelnishanth/offlyn-verify-core/issues/3), [Issue #11](https://github.com/joelnishanth/offlyn-verify-core/issues/11) |
| Stage 2: Microcontroller gate | Planned | [Issue #2](https://github.com/joelnishanth/offlyn-verify-core/issues/2), [Issue #10](https://github.com/joelnishanth/offlyn-verify-core/issues/10) |
| Stage 3: FPGA implementation | Future | — |
| Stage 4: ASIC primitive | Future | — |

## Important Disclaimer

The current implementation is a **software simulation** (Stage 0). It demonstrates the architecture, interfaces, and defense properties but does not yet run on dedicated hardware. Claims about tamper resistance, real-time latency, and physical bypass prevention apply to the target hardware stages, not to the current Python prototype.

Any publication, presentation, or discussion of this work should clearly distinguish between the software prototype and the hardware enforcement targets.
