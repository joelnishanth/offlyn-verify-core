# Offlyn Verify Core — Robotics Roadmap

This repository tracks the **Offlyn Verify Core - Robotics Roadmap** via GitHub milestones and issues.

## Milestones

| Milestone | Goal | Issues |
|-----------|------|--------|
| [Phase 1 - Robotics MVP](https://github.com/joelnishanth/offlyn-verify-core/milestone/1) | Prove robot cannot actuate unless Verify Core allows | #14–#39 (+ legacy #1, #4, #6, #7, #9, #12) |
| [Phase 2 - Security & Hardening](https://github.com/joelnishanth/offlyn-verify-core/milestone/2) | Secure, auditable policy pipeline | #40–#64 (+ #8) |
| [Phase 3 - Attestation Runtime](https://github.com/joelnishanth/offlyn-verify-core/milestone/3) | Runtime trust before actuation | #65–#90 (+ #3, #11) |
| [Phase 4 - Hardware Integration](https://github.com/joelnishanth/offlyn-verify-core/milestone/4) | Enforcement at controller boundary | #91–#115 (+ #2, #10) |
| [Phase 5 - Fleet, Ecosystem & Silicon Path](https://github.com/joelnishanth/offlyn-verify-core/milestone/5) | Fleet scale and silicon path | #116–#142 (+ #5) |

## Start Here (Phase 1)

1. [#14 — Define Robotics Action Schema for Verify Core](https://github.com/joelnishanth/offlyn-verify-core/issues/14) (P0)
2. [#16 — Create ROS 2 simulation environment](https://github.com/joelnishanth/offlyn-verify-core/issues/16) (P0)
3. [#19 — Build Verify Core gate as ROS 2 node](https://github.com/joelnishanth/offlyn-verify-core/issues/19) (P0)

## Labels

Issues use labels that map to project custom fields:

- **Phase**: `phase-1` … `phase-5`
- **Priority**: `priority-p0` … `priority-p3`
- **Component**: `component-*` (e.g. `component-policy-gate`, `component-ros2`)
- **Type**: `epic`, `roadmap`

## GitHub Project Board

To create the project board with custom fields and add all issues:

```bash
gh auth refresh -h github.com -s project,read:project
.github/scripts/setup-github-project.sh
```

This creates **Offlyn Verify Core - Robotics Roadmap** with Phase, Priority, Component, Risk Level, Demo Impact, and Target Date fields. Configure the Status field in the GitHub UI:

`Backlog | Ready | In Progress | Blocked | Needs Review | Done`

## Recreate Issues (if needed)

```bash
.github/scripts/create-roadmap-issues.sh      # Phase 1 only
.github/scripts/create-roadmap-phases2-5.sh   # Phases 2–5
```

## Phase 1 Success Criteria

- Rover receives proposed actions
- Verify Core evaluates each action
- Allowed actions reach `/cmd_vel`
- Denied actions never reach `/cmd_vel`
- Restricted-zone and speed policies work
- Every decision is logged
- Demo shows allow, deny, and bypass-block behavior
