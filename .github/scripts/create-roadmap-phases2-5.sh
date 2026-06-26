#!/usr/bin/env bash
# Create Phase 2-5 roadmap issues for Offlyn Verify Core Robotics Roadmap
set -euo pipefail

REPO="joelnishanth/offlyn-verify-core"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

create_issue() {
  local title="$1"
  local milestone="$2"
  local labels="$3"
  local body_file="$4"
  gh issue create --repo "$REPO" --title "$title" --milestone "$milestone" --label "$labels" --body-file "$body_file"
}

write_body() {
  local file="$1"
  shift
  cat > "$file" <<EOF
$@
EOF
}

echo "Creating Phase 2 epics and tasks..."

# Phase 2 Epics
for epic in \
  "Epic: Signed policy updates|Define and implement signed policy update workflow with Ed25519 verification.|Signed Policy" \
  "Epic: Policy integrity protection|Protect policy files from tampering and unauthorized modification.|Signed Policy" \
  "Epic: Secure configuration loading|Validate and securely load gate configuration at startup.|Policy Gate" \
  "Epic: Audit log hardening|Strengthen audit log with tamper-evident hash chaining and metadata.|Audit Log" \
  "Epic: Expanded attack tests|Add security-focused attack tests for policy pipeline.|Attack Tests" \
  "Epic: CI security checks|Run security tests automatically in CI pipeline.|Attack Tests" \
  "Epic: Documentation and threat model|Document security architecture and threat model for Phase 2.|Documentation"; do
  IFS='|' read -r title goal component <<< "$epic"
  write_body "$TMPDIR/body.md" "## Phase
Phase 2 - Security & Hardening

## Component
$component

## Priority
P1 High

## Status
Backlog

## Type
Epic

## Goal
$goal

## Why this matters
Phase 2 makes the software policy gate secure, auditable, and resistant to unauthorized policy changes.

## Acceptance criteria
- [ ] Epic scope defined and broken into tasks
- [ ] All tasks linked to this epic
- [ ] Success criteria met for epic scope

## Dependencies
Phase 1 - Robotics MVP

## Expected output
Completed epic deliverables with tests and documentation."
  create_issue "$title" "Phase 2 - Security & Hardening" "phase-2,priority-p1,epic,roadmap,enhancement" "$TMPDIR/body.md"
done

# Phase 2 Tasks
declare -a P2_TASKS=(
  "Define policy signing process|Document the policy signing workflow from authoring to deployment.|Signed Policy|P1 High"
  "Generate signing and verification keys for demo|Create demo Ed25519 key pair for policy signing tests.|Signed Policy|P1 High"
  "Require signatures for policy updates|Gate rejects policy loads without valid signatures.|Signed Policy|P0 Critical"
  "Reject unsigned policy files|Add test proving unsigned policies are rejected at load time.|Signed Policy|P0 Critical"
  "Reject modified policy files|Detect and reject tampered policy content.|Signed Policy|P0 Critical"
  "Add policy hash to every audit event|Include active policy hash in all audit log entries.|Audit Log|P1 High"
  "Add gate binary version to every audit event|Include gate version in audit metadata for traceability.|Audit Log|P2 Medium"
  "Add config validation|Validate gate configuration schema at startup.|Policy Gate|P1 High"
  "Add policy rollback protection|Enforce monotonic policy epoch to prevent rollback attacks.|Signed Policy|P0 Critical"
  "Add tamper-evident audit log chain|Implement hash-chained audit log integrity verification.|Audit Log|P1 High"
  "Add test: unsigned policy update|Automated test for unsigned policy rejection.|Attack Tests|P1 High"
  "Add test: modified policy update|Automated test for tampered policy rejection.|Attack Tests|P1 High"
  "Add test: stale policy rollback|Automated test for epoch rollback rejection.|Attack Tests|P1 High"
  "Add test: malformed policy input|Automated test for invalid policy format rejection.|Attack Tests|P2 Medium"
  "Add CI checks for policy security tests|Run security tests in GitHub Actions CI.|Attack Tests|P1 High"
  "Add threat model document|Document Phase 2 threat model with attacker capabilities and mitigations.|Documentation|P1 High"
  "Add security architecture diagram|Visual diagram of secure policy pipeline.|Documentation|P2 Medium"
  "Update README with secure policy flow|Document signed policy workflow in README.|Documentation|P2 Medium"
)

for task in "${P2_TASKS[@]}"; do
  IFS='|' read -r title goal component priority <<< "$task"
  pri_label="priority-p1"
  [[ "$priority" == "P0 Critical" ]] && pri_label="priority-p0"
  [[ "$priority" == "P2 Medium" ]] && pri_label="priority-p2"
  comp_label="component-policy-gate"
  [[ "$component" == "Signed Policy" ]] && comp_label="component-signed-policy"
  [[ "$component" == "Audit Log" ]] && comp_label="component-audit-log"
  [[ "$component" == "Attack Tests" ]] && comp_label="component-attack-tests"
  [[ "$component" == "Documentation" ]] && comp_label="component-documentation"
  write_body "$TMPDIR/body.md" "## Phase
Phase 2 - Security & Hardening

## Component
$component

## Priority
$priority

## Status
Backlog

## Goal
$goal

## Why this matters
Secures the policy pipeline against unauthorized changes and provides auditable enforcement.

## Acceptance criteria
- [ ] Task goal implemented
- [ ] Tests pass
- [ ] Documentation updated if applicable

## Dependencies
Phase 1 - Robotics MVP

## Expected output
Working implementation with tests for: $title"
  create_issue "$title" "Phase 2 - Security & Hardening" "phase-2,$pri_label,$comp_label,roadmap,enhancement" "$TMPDIR/body.md"
done

echo "Creating Phase 3 epics and tasks..."

for epic in \
  "Epic: TPM or TEE-backed runtime identity|Establish hardware-backed runtime identity for the gate.|TPM / Attestation" \
  "Epic: Runtime measurement|Measure gate binary, policy, and config at runtime.|TPM / Attestation" \
  "Epic: Policy hash verification|Verify active policy hash matches attested measurement.|TPM / Attestation" \
  "Epic: Gate binary verification|Verify gate binary integrity via attestation.|TPM / Attestation" \
  "Epic: Attestation report API|Expose runtime attestation report for external verification.|TPM / Attestation" \
  "Epic: Fail-safe behavior|Block actuation when runtime attestation fails.|TPM / Attestation" \
  "Epic: Attested robotics demo|Record demo proving runtime trust before robot movement.|Demo Video"; do
  IFS='|' read -r title goal component <<< "$epic"
  write_body "$TMPDIR/body.md" "## Phase
Phase 3 - Attestation Runtime

## Component
$component

## Priority
P1 High

## Status
Backlog

## Type
Epic

## Goal
$goal

## Why this matters
Phase 3 proves the robot can verify policy gate and policy state before trusting commands.

## Acceptance criteria
- [ ] Epic scope defined and broken into tasks
- [ ] Attestation failure blocks actuation
- [ ] Demo proves runtime trust

## Dependencies
Phase 2 - Security & Hardening

## Expected output
Completed attestation runtime with demo."
  create_issue "$title" "Phase 3 - Attestation Runtime" "phase-3,priority-p1,epic,roadmap,enhancement,component-tpm-attestation" "$TMPDIR/body.md"
done

declare -a P3_TASKS=(
  "Choose TPM path for MVP|Select TPM 2.0 integration approach for attestation MVP.|TPM / Attestation|P0 Critical"
  "Define measured components|Document which components are measured (binary, policy, config).|TPM / Attestation|P1 High"
  "Measure Verify Core gate binary|Compute and store gate binary measurement.|TPM / Attestation|P1 High"
  "Measure active policy file|Compute and store policy file measurement.|TPM / Attestation|P1 High"
  "Measure config file|Compute and store config file measurement.|TPM / Attestation|P2 Medium"
  "Generate runtime attestation report|Produce attestation report with all measurements.|TPM / Attestation|P0 Critical"
  "Expose attestation report API|HTTP or ROS service for attestation report retrieval.|TPM / Attestation|P1 High"
  "Add policy hash to attestation report|Include policy hash in attestation output.|TPM / Attestation|P1 High"
  "Add gate binary hash to attestation report|Include gate binary hash in attestation output.|TPM / Attestation|P1 High"
  "Add boot or runtime trust status|Report trusted/untrusted runtime state.|TPM / Attestation|P1 High"
  "Add verification script|CLI script to verify attestation report externally.|TPM / Attestation|P2 Medium"
  "Add fail-safe mode when attestation fails|Enter safe mode blocking all actuation on attestation failure.|TPM / Attestation|P0 Critical"
  "Block actuator commands if runtime is untrusted|Fail-closed actuation when trust check fails.|TPM / Attestation|P0 Critical"
  "Add test: trusted runtime allows commands|Verify trusted state permits actuation.|Attack Tests|P1 High"
  "Add test: modified policy fails attestation|Verify tampered policy fails trust check.|Attack Tests|P1 High"
  "Add test: modified gate binary fails attestation|Verify tampered binary fails trust check.|Attack Tests|P1 High"
  "Add test: missing attestation blocks actuation|Verify missing attestation blocks commands.|Attack Tests|P0 Critical"
  "Update dashboard with attestation status|Show trust status in demo dashboard.|Dashboard|P2 Medium"
  "Record attested runtime demo|Record demo video for Phase 3 milestone.|Demo Video|P1 High"
)

for task in "${P3_TASKS[@]}"; do
  IFS='|' read -r title goal component priority <<< "$task"
  pri_label="priority-p1"
  [[ "$priority" == "P0 Critical" ]] && pri_label="priority-p0"
  [[ "$priority" == "P2 Medium" ]] && pri_label="priority-p2"
  comp_label="component-tpm-attestation"
  [[ "$component" == "Attack Tests" ]] && comp_label="component-attack-tests"
  [[ "$component" == "Dashboard" ]] && comp_label="component-dashboard"
  [[ "$component" == "Demo Video" ]] && comp_label="component-demo-video"
  write_body "$TMPDIR/body.md" "## Phase
Phase 3 - Attestation Runtime

## Component
$component

## Priority
$priority

## Status
Backlog

## Goal
$goal

## Why this matters
Runtime attestation ensures the robot trusts only verified gate and policy state.

## Acceptance criteria
- [ ] Task goal implemented
- [ ] Attestation tests pass
- [ ] Fail-safe behavior verified

## Dependencies
Phase 2 - Security & Hardening

## Expected output
Working attestation feature: $title"
  create_issue "$title" "Phase 3 - Attestation Runtime" "phase-3,$pri_label,$comp_label,roadmap,enhancement" "$TMPDIR/body.md"
done

echo "Creating Phase 4 epics and tasks..."

for epic in \
  "Epic: Edge controller integration|Move gate enforcement to edge controller hardware.|Edge Controller" \
  "Epic: Secure boot enforcement|Require trusted boot image for controller startup.|Secure Boot" \
  "Epic: Trusted command path|Establish hardware-trusted path from gate to actuators.|Hardware Boundary" \
  "Epic: Hardware-bound policy checks|Evaluate policy on controller near actuator boundary.|Hardware Boundary" \
  "Epic: Real-time command evaluation|Meet latency requirements for real-time robotics.|Policy Gate" \
  "Epic: Robotics middleware SDK|Provide SDK wrapper for ROS 2 command routing.|ROS 2" \
  "Epic: Hardware integration demo|Record demo of hardware-linked policy gate.|Demo Video"; do
  IFS='|' read -r title goal component <<< "$epic"
  comp_label="component-edge-controller"
  [[ "$component" == "Secure Boot" ]] && comp_label="component-secure-boot"
  [[ "$component" == "Hardware Boundary" ]] && comp_label="component-hardware-boundary"
  [[ "$component" == "Policy Gate" ]] && comp_label="component-policy-gate"
  [[ "$component" == "ROS 2" ]] && comp_label="component-ros2"
  [[ "$component" == "Demo Video" ]] && comp_label="component-demo-video"
  write_body "$TMPDIR/body.md" "## Phase
Phase 4 - Hardware Integration

## Component
$component

## Priority
P1 High

## Status
Backlog

## Type
Epic

## Goal
$goal

## Why this matters
Phase 4 moves enforcement closer to the robotics controller or actuator boundary.

## Acceptance criteria
- [ ] Epic scope defined and broken into tasks
- [ ] Hardware-linked enforcement demonstrated
- [ ] Fail-closed behavior on controller

## Dependencies
Phase 3 - Attestation Runtime

## Expected output
Hardware-integrated gate with demo."
  create_issue "$title" "Phase 4 - Hardware Integration" "phase-4,priority-p1,epic,roadmap,enhancement,$comp_label" "$TMPDIR/body.md"
done

declare -a P4_TASKS=(
  "Select edge controller target|Choose Raspberry Pi Pico, ESP32, or STM32 for gate prototype.|Edge Controller|P0 Critical"
  "Define controller-to-actuator command path|Document physical command path from controller to actuators.|Hardware Boundary|P1 High"
  "Move Verify Core gate onto edge controller|Port gate logic to run on dedicated controller.|Edge Controller|P0 Critical"
  "Add secure boot requirements|Define and implement secure boot for controller.|Secure Boot|P1 High"
  "Add controller identity check|Verify controller identity before accepting commands.|Edge Controller|P1 High"
  "Add trusted command channel|Establish authenticated channel between host and controller.|Hardware Boundary|P1 High"
  "Define hardware-bound policy interface|API for policy evaluation on controller hardware.|Hardware Boundary|P1 High"
  "Add latency measurement for policy decisions|Benchmark policy decision latency on controller.|Policy Gate|P2 Medium"
  "Add fail-closed behavior on controller|Block actuation when gate fails on controller.|Policy Gate|P0 Critical"
  "Add watchdog for gate failure|Hardware watchdog resets on gate hang or crash.|Edge Controller|P1 High"
  "Add emergency stop integration|Wire e-stop to bypass gate safely for safety override.|Hardware Boundary|P1 High"
  "Add real-time command constraints|Meet real-time deadlines for command evaluation.|Policy Gate|P2 Medium"
  "Add test: controller boots trusted image|Verify secure boot with trusted firmware.|Attack Tests|P1 High"
  "Add test: untrusted controller cannot send commands|Verify untrusted controller is blocked.|Attack Tests|P0 Critical"
  "Add test: policy gate failure stops actuation|Verify gate failure triggers fail-closed.|Attack Tests|P0 Critical"
  "Add SDK wrapper for ROS 2 command routing|SDK for routing ROS 2 commands through hardware gate.|ROS 2|P1 High"
  "Document hardware integration path|Document controller selection and integration steps.|Documentation|P2 Medium"
  "Record hardware-linked gate demo|Record Phase 4 milestone demo video.|Demo Video|P1 High"
)

for task in "${P4_TASKS[@]}"; do
  IFS='|' read -r title goal component priority <<< "$task"
  pri_label="priority-p1"
  [[ "$priority" == "P0 Critical" ]] && pri_label="priority-p0"
  [[ "$priority" == "P2 Medium" ]] && pri_label="priority-p2"
  comp_label="component-edge-controller"
  [[ "$component" == "Hardware Boundary" ]] && comp_label="component-hardware-boundary"
  [[ "$component" == "Secure Boot" ]] && comp_label="component-secure-boot"
  [[ "$component" == "Policy Gate" ]] && comp_label="component-policy-gate"
  [[ "$component" == "Attack Tests" ]] && comp_label="component-attack-tests"
  [[ "$component" == "ROS 2" ]] && comp_label="component-ros2"
  [[ "$component" == "Documentation" ]] && comp_label="component-documentation"
  [[ "$component" == "Demo Video" ]] && comp_label="component-demo-video"
  write_body "$TMPDIR/body.md" "## Phase
Phase 4 - Hardware Integration

## Component
$component

## Priority
$priority

## Status
Backlog

## Goal
$goal

## Why this matters
Hardware integration provides physical separation between autonomy stack and actuators.

## Acceptance criteria
- [ ] Task goal implemented on target hardware
- [ ] Tests pass on controller
- [ ] Fail-closed verified

## Dependencies
Phase 3 - Attestation Runtime

## Expected output
Hardware integration deliverable: $title"
  create_issue "$title" "Phase 4 - Hardware Integration" "phase-4,$pri_label,$comp_label,roadmap,enhancement" "$TMPDIR/body.md"
done

echo "Creating Phase 5 epics and tasks..."

for epic in \
  "Epic: Fleet policy management|Manage policies across multiple robots.|Fleet Management" \
  "Epic: Multi-robot coordination|Coordinate policy enforcement across robot fleet.|Fleet Management" \
  "Epic: Policy orchestration|Deploy and version policies across fleet.|Fleet Management" \
  "Epic: Industry-specific templates|Policy templates for warehouse, drone, arm, defense.|Policy Gate" \
  "Epic: Compliance and audit reporting|Generate compliance-style audit reports.|Audit Log" \
  "Epic: Silicon primitive definition|Define chip-level policy gate requirements.|Hardware Boundary" \
  "Epic: Partner and ecosystem readiness|Prepare materials for partners and investors.|Documentation"; do
  IFS='|' read -r title goal component <<< "$epic"
  comp_label="component-fleet-management"
  [[ "$component" == "Policy Gate" ]] && comp_label="component-policy-gate"
  [[ "$component" == "Audit Log" ]] && comp_label="component-audit-log"
  [[ "$component" == "Hardware Boundary" ]] && comp_label="component-hardware-boundary"
  [[ "$component" == "Documentation" ]] && comp_label="component-documentation"
  write_body "$TMPDIR/body.md" "## Phase
Phase 5 - Fleet, Ecosystem & Silicon Path

## Component
$component

## Priority
P1 High

## Status
Backlog

## Type
Epic

## Goal
$goal

## Why this matters
Phase 5 scales from one robot to fleets and defines the silicon enforcement path.

## Acceptance criteria
- [ ] Epic scope defined and broken into tasks
- [ ] Fleet-scale capabilities demonstrated
- [ ] Partner-ready documentation

## Dependencies
Phase 4 - Hardware Integration

## Expected output
Fleet and ecosystem deliverables."
  create_issue "$title" "Phase 5 - Fleet, Ecosystem & Silicon Path" "phase-5,priority-p1,epic,roadmap,enhancement,$comp_label" "$TMPDIR/body.md"
done

declare -a P5_TASKS=(
  "Define fleet policy model|Data model for fleet-wide policy management.|Fleet Management|P0 Critical"
  "Create policy groups by robot type|Group policies by rover, drone, arm, etc.|Fleet Management|P1 High"
  "Add fleet-level policy deployment flow|Workflow to deploy policies to robot fleet.|Fleet Management|P1 High"
  "Add policy version tracking across robots|Track which policy version each robot runs.|Fleet Management|P1 High"
  "Add robot trust status dashboard|Dashboard showing trust status of all robots.|Dashboard|P1 High"
  "Add multi-robot restricted-zone test|Test fleet coordination in shared restricted zones.|Attack Tests|P2 Medium"
  "Add policy template for warehouse rover|Industry template for warehouse automation.|Policy Gate|P2 Medium"
  "Add policy template for drone|Industry template for aerial robotics.|Policy Gate|P2 Medium"
  "Add policy template for robotic arm|Industry template for manipulator arms.|Policy Gate|P2 Medium"
  "Add policy template for defense/autonomy platform|Industry template for defense robotics.|Policy Gate|P3 Low"
  "Add compliance-style audit report export|Export audit logs in compliance report format.|Audit Log|P1 High"
  "Add fleet event timeline|Timeline view of fleet policy events.|Dashboard|P2 Medium"
  "Define hardware policy primitive requirements|Document requirements for silicon policy gate.|Hardware Boundary|P1 High"
  "Define chip-level policy gate concept|Concept design for ASIC/FPGA policy enforcement.|Hardware Boundary|P1 High"
  "Define actuator bus enforcement model|Model for enforcing policy on actuator bus.|Hardware Boundary|P1 High"
  "Define silicon integration assumptions|Document assumptions for silicon partner integration.|Hardware Boundary|P2 Medium"
  "Create investor/customer demo deck|Presentation deck for stakeholders.|Documentation|P1 High"
  "Create technical whitepaper update|Update paper with fleet and silicon roadmap.|Paper|P1 High"
  "Create partner outreach package|Materials for partner and ecosystem outreach.|Documentation|P2 Medium"
  "Record fleet-scale concept demo|Record Phase 5 milestone concept demo.|Demo Video|P1 High"
)

for task in "${P5_TASKS[@]}"; do
  IFS='|' read -r title goal component priority <<< "$task"
  pri_label="priority-p1"
  [[ "$priority" == "P0 Critical" ]] && pri_label="priority-p0"
  [[ "$priority" == "P2 Medium" ]] && pri_label="priority-p2"
  [[ "$priority" == "P3 Low" ]] && pri_label="priority-p3"
  comp_label="component-fleet-management"
  [[ "$component" == "Dashboard" ]] && comp_label="component-dashboard"
  [[ "$component" == "Attack Tests" ]] && comp_label="component-attack-tests"
  [[ "$component" == "Policy Gate" ]] && comp_label="component-policy-gate"
  [[ "$component" == "Audit Log" ]] && comp_label="component-audit-log"
  [[ "$component" == "Hardware Boundary" ]] && comp_label="component-hardware-boundary"
  [[ "$component" == "Documentation" ]] && comp_label="component-documentation"
  [[ "$component" == "Paper" ]] && comp_label="component-paper"
  [[ "$component" == "Demo Video" ]] && comp_label="component-demo-video"
  write_body "$TMPDIR/body.md" "## Phase
Phase 5 - Fleet, Ecosystem & Silicon Path

## Component
$component

## Priority
$priority

## Status
Backlog

## Goal
$goal

## Why this matters
Fleet scale and silicon path define the long-term product and ecosystem strategy.

## Acceptance criteria
- [ ] Task goal implemented or documented
- [ ] Stakeholder review completed
- [ ] Demo or documentation delivered

## Dependencies
Phase 4 - Hardware Integration

## Expected output
Fleet/ecosystem deliverable: $title"
  create_issue "$title" "Phase 5 - Fleet, Ecosystem & Silicon Path" "phase-5,$pri_label,$comp_label,roadmap,enhancement" "$TMPDIR/body.md"
done

echo "Phase 2-5 roadmap issues created."
