#!/usr/bin/env bash
# Create Offlyn Verify Core - Robotics Roadmap issues
set -euo pipefail

REPO="joelnishanth/offlyn-verify-core"

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  gh label create "$name" --repo "$REPO" --color "$color" --description "$description" --force 2>/dev/null || true
}

echo "Creating roadmap labels..."
create_label "phase-1" "0E8A16" "Phase 1 - Robotics MVP"
create_label "phase-2" "1D76DB" "Phase 2 - Security & Hardening"
create_label "phase-3" "5319E7" "Phase 3 - Attestation Runtime"
create_label "phase-4" "FBCA04" "Phase 4 - Hardware Integration"
create_label "phase-5" "D93F0B" "Phase 5 - Fleet, Ecosystem & Silicon Path"
create_label "priority-p0" "B60205" "P0 Critical"
create_label "priority-p1" "D93F0B" "P1 High"
create_label "priority-p2" "FBCA04" "P2 Medium"
create_label "priority-p3" "0E8A16" "P3 Low"
create_label "epic" "7057FF" "Epic / parent work item"
create_label "roadmap" "C5DEF5" "Future roadmap item"
create_label "component-action-schema" "0075CA" "Action Schema"
create_label "component-simulator" "0075CA" "Simulator"
create_label "component-policy-gate" "0075CA" "Policy Gate"
create_label "component-opa-rego" "0075CA" "OPA / Rego"
create_label "component-ros2" "0075CA" "ROS 2"
create_label "component-audit-log" "0075CA" "Audit Log"
create_label "component-attack-tests" "0075CA" "Attack Tests"
create_label "component-dashboard" "0075CA" "Dashboard"
create_label "component-demo-video" "0075CA" "Demo Video"
create_label "component-documentation" "0075CA" "Documentation"
create_label "component-signed-policy" "0075CA" "Signed Policy"
create_label "component-tpm-attestation" "0075CA" "TPM / Attestation"
create_label "component-secure-boot" "0075CA" "Secure Boot"
create_label "component-edge-controller" "0075CA" "Edge Controller"
create_label "component-hardware-boundary" "0075CA" "Hardware Boundary"
create_label "component-fleet-management" "0075CA" "Fleet Management"
create_label "component-paper" "0075CA" "Paper"

create_issue() {
  local title="$1"
  local milestone="$2"
  local labels="$3"
  local body_file="$4"
  gh issue create --repo "$REPO" --title "$title" --milestone "$milestone" --label "$labels" --body-file "$body_file"
}

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

write_body() {
  local file="$1"
  shift
  cat > "$file" <<EOF
$@
EOF
}

echo "Creating Phase 1 issues..."

write_body "$TMPDIR/01-schema.md" '# Define Robotics Action Schema for Verify Core

## Phase
Phase 1 - Robotics MVP

## Component
Action Schema

## Priority
P0 Critical

## Status
Backlog

## Goal
Define the structured robot action format that the autonomy layer must submit before any command can be evaluated by Offlyn Verify Core.

## Why this matters
Verify Core should not evaluate vague free-form intent. It should evaluate structured, machine-checkable robot actions before they reach the actuator boundary.

## Example action

```json
{
  "robot_id": "rover-01",
  "mission_id": "mission-demo-001",
  "action": "move",
  "linear_x": 0.4,
  "angular_z": 0.0,
  "zone": "normal",
  "human_nearby": false,
  "source": "autonomy_planner"
}
```

## Acceptance criteria
- [ ] Action schema is documented
- [ ] Required fields are defined (robot_id, action, source)
- [ ] Optional fields are defined (zone, human_nearby, mission_id)
- [ ] Invalid or missing fields are rejected
- [ ] Schema supports: move, stop, turn, emergency_stop
- [ ] Example valid actions included
- [ ] Example invalid actions included
- [ ] Schema stored in `schemas/` or `docs/schemas/`

## Dependencies
None

## Expected output
A committed schema document and sample JSON files for valid and invalid robot actions.'

create_issue "Define Robotics Action Schema for Verify Core" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-action-schema,enhancement" "$TMPDIR/01-schema.md"

write_body "$TMPDIR/02-examples.md" '## Phase
Phase 1 - Robotics MVP

## Component
Action Schema

## Priority
P1 High

## Status
Backlog

## Goal
Document valid and invalid robot action examples for the Verify Core action schema.

## Why this matters
Developers and testers need concrete examples to validate schema enforcement and build integration tests.

## Acceptance criteria
- [ ] At least 5 valid action examples committed
- [ ] At least 5 invalid action examples committed
- [ ] Each invalid example documents the expected rejection reason
- [ ] Examples cover move, stop, turn, and emergency_stop actions

## Dependencies
- Define Robotics Action Schema for Verify Core

## Expected output
Sample JSON files under `schemas/examples/valid/` and `schemas/examples/invalid/`.'

create_issue "Document valid and invalid action examples" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-action-schema,enhancement" "$TMPDIR/02-examples.md"

write_body "$TMPDIR/03-ros2-env.md" '## Phase
Phase 1 - Robotics MVP

## Component
Simulator

## Priority
P0 Critical

## Status
Backlog

## Goal
Create a ROS 2 simulation workspace for the Verify Core robotics MVP demo.

## Why this matters
The MVP must prove policy enforcement in a realistic robotics middleware environment, not only in Python unit tests.

## Acceptance criteria
- [ ] ROS 2 workspace created under `ros2_ws/`
- [ ] Gazebo or compatible simulator launches successfully
- [ ] Workspace builds with `colcon build`
- [ ] Launch file starts simulation environment

## Dependencies
None

## Expected output
Working ROS 2 workspace with simulation launch files and build instructions in README.'

create_issue "Create ROS 2 simulation environment" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-simulator,enhancement" "$TMPDIR/03-ros2-env.md"

write_body "$TMPDIR/04-rover.md" '## Phase
Phase 1 - Robotics MVP

## Component
Simulator

## Priority
P1 High

## Status
Backlog

## Goal
Add a simple differential-drive rover model to the ROS 2 simulation.

## Why this matters
The demo needs a concrete robot that subscribes to `/cmd_vel` and moves in simulation.

## Acceptance criteria
- [ ] Rover URDF/SDF model added
- [ ] Rover spawns in simulation
- [ ] Rover responds to `/cmd_vel` commands
- [ ] Odometry or pose feedback available for zone checks

## Dependencies
- Create ROS 2 simulation environment

## Expected output
Rover model package with spawn and teleop test instructions.'

create_issue "Add simple rover model" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-simulator,enhancement" "$TMPDIR/04-rover.md"

write_body "$TMPDIR/05-gazebo-zones.md" '## Phase
Phase 1 - Robotics MVP

## Component
Simulator

## Priority
P1 High

## Status
Backlog

## Goal
Configure a Gazebo world with restricted zones for policy enforcement testing.

## Why this matters
Restricted-zone policy cannot be demonstrated without a map that defines allowed and forbidden areas.

## Acceptance criteria
- [ ] World file defines at least one restricted zone
- [ ] Zone boundaries are visible or documented
- [ ] Zone metadata is accessible to policy evaluation (map layer or config)
- [ ] Demo world launches with rover

## Dependencies
- Add simple rover model

## Expected output
Gazebo world with restricted zones and zone configuration file.'

create_issue "Configure Gazebo world with restricted zones" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-simulator,enhancement" "$TMPDIR/05-gazebo-zones.md"

write_body "$TMPDIR/06-gate-node.md" '## Phase
Phase 1 - Robotics MVP

## Component
Policy Gate

## Priority
P0 Critical

## Status
Backlog

## Goal
Build Verify Core as a ROS 2 node that evaluates proposed robot actions before actuation.

## Why this matters
This is the core actuation boundary — every command must pass through Verify Core before reaching `/cmd_vel`.

## Acceptance criteria
- [ ] ROS 2 node wraps existing `prototype/gate/verify_core.py` logic
- [ ] Node subscribes to proposed action topic
- [ ] Node evaluates actions against active policy
- [ ] Node fails closed on evaluation errors
- [ ] Node logs every decision

## Dependencies
- Define Robotics Action Schema for Verify Core

## Expected output
`verify_core_gate` ROS 2 package with gate node and launch file.'

create_issue "Build Verify Core gate as ROS 2 node" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-policy-gate,enhancement" "$TMPDIR/06-gate-node.md"

write_body "$TMPDIR/07-opa.md" '## Phase
Phase 1 - Robotics MVP

## Component
OPA / Rego

## Priority
P1 High

## Status
Backlog

## Goal
Add an OPA/Rego policy evaluator for robotics safety rules.

## Why this matters
Rego provides a declarative, auditable policy language for speed limits, zones, and proximity rules.

## Acceptance criteria
- [ ] OPA integration path defined (embedded or sidecar)
- [ ] Rego policies for speed, zone, and proximity rules
- [ ] Policy evaluation returns allow/deny with reason codes
- [ ] Unit tests cover Rego policy decisions

## Dependencies
- Build Verify Core gate as ROS 2 node

## Expected output
Rego policy files and integration with the Verify Core gate.'

create_issue "Add OPA/Rego policy evaluator" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-opa-rego,enhancement" "$TMPDIR/07-opa.md"

write_body "$TMPDIR/08-ros2-service.md" '## Phase
Phase 1 - Robotics MVP

## Component
ROS 2

## Priority
P1 High

## Status
Backlog

## Goal
Create a ROS 2 service interface for synchronous policy evaluation requests.

## Why this matters
Some autonomy components need request/response policy checks in addition to topic-based flow.

## Acceptance criteria
- [ ] Service definition for policy evaluation (`.srv` file)
- [ ] Gate node implements service handler
- [ ] Service returns allow/deny, reason, and token metadata
- [ ] Integration test calls service successfully

## Dependencies
- Build Verify Core gate as ROS 2 node

## Expected output
ROS 2 service interface and handler in the gate node.'

create_issue "Create ROS 2 service interface for policy evaluation" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-ros2,enhancement" "$TMPDIR/08-ros2-service.md"

write_body "$TMPDIR/09-route.md" '## Phase
Phase 1 - Robotics MVP

## Component
ROS 2

## Priority
P0 Critical

## Status
Backlog

## Goal
Route all autonomy commands through Verify Core before they can reach actuators.

## Why this matters
Direct routing to `/cmd_vel` would bypass the policy gate entirely.

## Acceptance criteria
- [ ] Autonomy planner publishes to `/proposed_action` (not `/cmd_vel`)
- [ ] Gate node is the only publisher to `/cmd_vel`
- [ ] Architecture diagram updated to show command flow
- [ ] Bypass attempt test fails as expected

## Dependencies
- Build Verify Core gate as ROS 2 node

## Expected output
End-to-end command routing through Verify Core with documented topic graph.'

create_issue "Route autonomy commands through Verify Core" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-ros2,enhancement" "$TMPDIR/09-route.md"

write_body "$TMPDIR/10-publish-cmdvel.md" '## Phase
Phase 1 - Robotics MVP

## Component
ROS 2

## Priority
P0 Critical

## Status
Backlog

## Goal
Publish approved commands from Verify Core to `/cmd_vel`.

## Why this matters
Allowed actions must reach the robot controller to demonstrate successful policy approval.

## Acceptance criteria
- [ ] Gate publishes `geometry_msgs/Twist` to `/cmd_vel` on ALLOW
- [ ] Published velocity matches approved action parameters
- [ ] Authorization token metadata attached or logged
- [ ] Rover moves when action is approved

## Dependencies
- Route autonomy commands through Verify Core

## Expected output
Working allow path from proposed action to rover movement.'

create_issue "Publish approved commands to /cmd_vel" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-ros2,enhancement" "$TMPDIR/10-publish-cmdvel.md"

write_body "$TMPDIR/11-block-deny.md" '## Phase
Phase 1 - Robotics MVP

## Component
Policy Gate

## Priority
P0 Critical

## Status
Backlog

## Goal
Ensure denied commands never reach `/cmd_vel`.

## Why this matters
Fail-closed enforcement is the central safety property of Verify Core.

## Acceptance criteria
- [ ] Denied actions produce no `/cmd_vel` publication
- [ ] Denial reason logged in audit trail
- [ ] Rover does not move on denied actions
- [ ] Test proves zero `/cmd_vel` messages on deny

## Dependencies
- Route autonomy commands through Verify Core

## Expected output
Verified fail-closed deny path with test coverage.'

create_issue "Block denied commands from reaching /cmd_vel" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-policy-gate,enhancement" "$TMPDIR/11-block-deny.md"

write_body "$TMPDIR/12-intercept.md" '## Phase
Phase 1 - Robotics MVP

## Component
ROS 2

## Priority
P1 High

## Status
Backlog

## Goal
Add a command interception node that prevents direct `/cmd_vel` bypass attempts.

## Why this matters
Autonomy stacks or attackers may attempt to publish directly to actuator topics.

## Acceptance criteria
- [ ] Interceptor detects unauthorized `/cmd_vel` publishers
- [ ] Direct bypass attempts are blocked or flagged
- [ ] Only gate-authorized commands reach actuators
- [ ] Attack test covers bypass scenario

## Dependencies
- Build Verify Core gate as ROS 2 node

## Expected output
Command interception node with bypass detection and blocking.'

create_issue "Add command interception node" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-ros2,enhancement" "$TMPDIR/12-intercept.md"

write_body "$TMPDIR/13-zone-map.md" '## Phase
Phase 1 - Robotics MVP

## Component
Policy Gate

## Priority
P1 High

## Status
Backlog

## Goal
Add restricted-zone map support to policy evaluation.

## Why this matters
Robots must not enter forbidden areas even if the autonomy planner requests it.

## Acceptance criteria
- [ ] Zone map format defined
- [ ] Gate evaluates robot position against zone boundaries
- [ ] Entering restricted zone triggers DENY
- [ ] Zone violation logged with coordinates

## Dependencies
- Configure Gazebo world with restricted zones
- Add OPA/Rego policy evaluator

## Expected output
Zone map configuration and restricted-zone policy enforcement.'

create_issue "Add restricted-zone map" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-policy-gate,enhancement" "$TMPDIR/13-zone-map.md"

write_body "$TMPDIR/14-speed.md" '## Phase
Phase 1 - Robotics MVP

## Component
OPA / Rego

## Priority
P1 High

## Status
Backlog

## Goal
Implement max-speed policy enforcement for rover actions.

## Why this matters
Unsafe velocity commands are a primary robotics safety concern and a core demo scenario.

## Acceptance criteria
- [ ] Policy defines maximum linear and angular velocity
- [ ] Actions exceeding limits are denied
- [ ] Actions within limits are allowed
- [ ] Speed violation reason code returned

## Dependencies
- Add OPA/Rego policy evaluator

## Expected output
Speed-limit Rego policy with passing unit and integration tests.'

create_issue "Add speed-limit policy" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-opa-rego,enhancement" "$TMPDIR/14-speed.md"

write_body "$TMPDIR/15-human.md" '## Phase
Phase 1 - Robotics MVP

## Component
OPA / Rego

## Priority
P1 High

## Status
Backlog

## Goal
Implement human-proximity policy that restricts robot speed or movement near humans.

## Why this matters
Human-robot interaction safety is a key robotics policy use case.

## Acceptance criteria
- [ ] Policy reads `human_nearby` field from action schema
- [ ] Speed capped or movement denied when human is nearby
- [ ] Policy configurable via policy file
- [ ] Demo scenario shows human-proximity enforcement

## Dependencies
- Add OPA/Rego policy evaluator

## Expected output
Human-proximity Rego policy and demo scenario.'

create_issue "Add human-proximity policy" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-opa-rego,enhancement" "$TMPDIR/15-human.md"

write_body "$TMPDIR/16-malformed.md" '## Phase
Phase 1 - Robotics MVP

## Component
Policy Gate

## Priority
P2 Medium

## Status
Backlog

## Goal
Reject malformed or incomplete action commands at the schema validation layer.

## Why this matters
Invalid input must fail closed before reaching policy evaluation or actuators.

## Acceptance criteria
- [ ] Missing required fields rejected
- [ ] Invalid action types rejected
- [ ] Out-of-range values rejected
- [ ] Rejection reason includes validation error details

## Dependencies
- Define Robotics Action Schema for Verify Core

## Expected output
Schema validation layer with malformed-command rejection tests.'

create_issue "Add malformed-command denial" "Phase 1 - Robotics MVP" "phase-1,priority-p2,component-policy-gate,enhancement" "$TMPDIR/16-malformed.md"

write_body "$TMPDIR/17-audit.md" '## Phase
Phase 1 - Robotics MVP

## Component
Audit Log

## Priority
P1 High

## Status
Backlog

## Goal
Add JSONL or SQLite audit logging for every Verify Core policy decision.

## Why this matters
Every allow/deny decision must be auditable for safety review and demo traceability.

## Acceptance criteria
- [ ] Audit log captures timestamp, action, decision, reason, policy hash
- [ ] Log format is JSONL or SQLite with query support
- [ ] Leverages existing `prototype/gate/audit_log.py` where possible
- [ ] Log entries append-only

## Dependencies
- Build Verify Core gate as ROS 2 node

## Expected output
Persistent audit log with sample query commands.'

create_issue "Add JSONL or SQLite audit log" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-audit-log,enhancement" "$TMPDIR/17-audit.md"

write_body "$TMPDIR/18-unit-tests.md" '## Phase
Phase 1 - Robotics MVP

## Component
Attack Tests

## Priority
P1 High

## Status
Backlog

## Goal
Add policy unit tests for robotics safety rules.

## Why this matters
Automated tests prevent regressions in allow/deny logic as policies evolve.

## Acceptance criteria
- [ ] Unit tests for speed-limit policy
- [ ] Unit tests for restricted-zone policy
- [ ] Unit tests for human-proximity policy
- [ ] Unit tests for schema validation
- [ ] All tests pass in CI

## Dependencies
- Add speed-limit policy
- Add restricted-zone map
- Add human-proximity policy

## Expected output
pytest (or equivalent) test suite for policy rules.'

create_issue "Add policy unit tests" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-attack-tests,enhancement" "$TMPDIR/18-unit-tests.md"

write_body "$TMPDIR/19-integration.md" '## Phase
Phase 1 - Robotics MVP

## Component
Attack Tests

## Priority
P1 High

## Status
Backlog

## Goal
Add ROS 2 integration tests for the full Verify Core command path.

## Why this matters
Unit tests alone cannot prove end-to-end middleware integration works correctly.

## Acceptance criteria
- [ ] Integration test launches gate node
- [ ] Test sends proposed action and verifies `/cmd_vel` output
- [ ] Test verifies deny path produces no actuator command
- [ ] Tests run in CI or documented local workflow

## Dependencies
- Build Verify Core gate as ROS 2 node
- Route autonomy commands through Verify Core

## Expected output
ROS 2 integration test suite with passing results.'

create_issue "Add ROS 2 integration tests" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-attack-tests,enhancement" "$TMPDIR/19-integration.md"

write_body "$TMPDIR/20-attack-speed.md" '## Phase
Phase 1 - Robotics MVP

## Component
Attack Tests

## Priority
P1 High

## Status
Backlog

## Goal
Add attack test: unsafe speed command must be denied.

## Why this matters
Demonstrates that Verify Core blocks dangerous velocity requests from reaching actuators.

## Acceptance criteria
- [ ] Test sends action with velocity above policy limit
- [ ] Verify Core returns DENY
- [ ] No `/cmd_vel` message published
- [ ] Denial logged in audit trail

## Dependencies
- Add speed-limit policy

## Expected output
Automated attack test for unsafe speed scenario.'

create_issue "Add attack test: unsafe speed" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-attack-tests,enhancement" "$TMPDIR/20-attack-speed.md"

write_body "$TMPDIR/21-attack-zone.md" '## Phase
Phase 1 - Robotics MVP

## Component
Attack Tests

## Priority
P1 High

## Status
Backlog

## Goal
Add attack test: restricted zone entry must be denied.

## Why this matters
Proves geofence-style policy enforcement blocks forbidden movement.

## Acceptance criteria
- [ ] Test sends action targeting restricted zone
- [ ] Verify Core returns DENY
- [ ] Rover does not enter restricted area
- [ ] Denial logged with zone violation reason

## Dependencies
- Add restricted-zone map

## Expected output
Automated attack test for restricted zone scenario.'

create_issue "Add attack test: restricted zone" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-attack-tests,enhancement" "$TMPDIR/21-attack-zone.md"

write_body "$TMPDIR/22-attack-bypass.md" '## Phase
Phase 1 - Robotics MVP

## Component
Attack Tests

## Priority
P0 Critical

## Status
Backlog

## Goal
Add attack test: direct actuator bypass attempt must be blocked.

## Why this matters
The actuation boundary is worthless if attackers can publish directly to `/cmd_vel`.

## Acceptance criteria
- [ ] Test publishes directly to `/cmd_vel` bypassing gate
- [ ] Interceptor or gate blocks unauthorized command
- [ ] Bypass attempt logged as security event
- [ ] Rover does not execute bypassed command

## Dependencies
- Add command interception node
- Build Verify Core gate as ROS 2 node

## Expected output
Automated attack test proving bypass prevention.'

create_issue "Add attack test: direct actuator bypass attempt" "Phase 1 - Robotics MVP" "phase-1,priority-p0,component-attack-tests,enhancement" "$TMPDIR/22-attack-bypass.md"

write_body "$TMPDIR/23-demo-script.md" '## Phase
Phase 1 - Robotics MVP

## Component
Demo Video

## Priority
P1 High

## Status
Backlog

## Goal
Create a scripted demo showing allow, deny, and bypass-block scenarios.

## Why this matters
The Phase 1 milestone requires a reproducible demo for stakeholders and video recording.

## Acceptance criteria
- [ ] Demo script covers: safe move (ALLOW), speed violation (DENY), zone violation (DENY), bypass attempt (BLOCK)
- [ ] Script is reproducible with single launch command
- [ ] Expected outputs documented step-by-step
- [ ] Script stored in `docs/phase1_demo.md`

## Dependencies
- All Phase 1 enforcement and test tasks

## Expected output
Documented demo script with launch commands and expected behavior.'

create_issue "Create demo script" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-demo-video,enhancement" "$TMPDIR/23-demo-script.md"

write_body "$TMPDIR/24-trace-view.md" '## Phase
Phase 1 - Robotics MVP

## Component
Dashboard

## Priority
P2 Medium

## Status
Backlog

## Goal
Build a demo trace view showing policy decisions in real time.

## Why this matters
Visualizing allow/deny decisions makes the demo compelling and aids debugging.

## Acceptance criteria
- [ ] Trace view reads from audit log
- [ ] Shows timestamp, action, decision, reason
- [ ] Updates during demo run (live or replay)
- [ ] Simple CLI or web view acceptable for MVP

## Dependencies
- Add JSONL or SQLite audit log

## Expected output
Demo trace viewer tool or dashboard page.'

create_issue "Build demo trace view" "Phase 1 - Robotics MVP" "phase-1,priority-p2,component-dashboard,enhancement" "$TMPDIR/24-trace-view.md"

write_body "$TMPDIR/25-demo-video.md" '## Phase
Phase 1 - Robotics MVP

## Component
Demo Video

## Priority
P1 High

## Status
Backlog

## Goal
Record the Phase 1 Robotics MVP demo video.

## Why this matters
Video proof is required for stakeholder communication and future grant/partner discussions.

## Acceptance criteria
- [ ] Video shows rover receiving proposed actions
- [ ] Video shows ALLOW path (rover moves)
- [ ] Video shows DENY path (rover stays still)
- [ ] Video shows bypass-block behavior
- [ ] Video linked from README

## Dependencies
- Create demo script

## Expected output
Recorded demo video committed or linked in repository documentation.'

create_issue "Record MVP demo video" "Phase 1 - Robotics MVP" "phase-1,priority-p1,component-demo-video,enhancement" "$TMPDIR/25-demo-video.md"

write_body "$TMPDIR/26-readme.md" '## Phase
Phase 1 - Robotics MVP

## Component
Documentation

## Priority
P2 Medium

## Status
Backlog

## Goal
Update README with Phase 1 Robotics MVP results and architecture.

## Why this matters
The repository must document what Phase 1 proves and how to reproduce the demo.

## Acceptance criteria
- [ ] README includes Phase 1 architecture diagram
- [ ] README includes quick start for ROS 2 demo
- [ ] README lists success criteria with checkmarks
- [ ] README links to demo script and video

## Dependencies
- Record MVP demo video

## Expected output
Updated README with Phase 1 results section.'

create_issue "Update README with Phase 1 results" "Phase 1 - Robotics MVP" "phase-1,priority-p2,component-documentation,enhancement" "$TMPDIR/26-readme.md"

echo "Phase 1 issues created."
