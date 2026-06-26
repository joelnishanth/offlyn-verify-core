# ROS 2 Workspace — Offlyn Verify Core Robotics MVP

This workspace contains the ROS 2 packages for the Phase 1 robotics demo.

## Architecture

```
/proposed_action                    /cmd_vel
     │                                  │
     ▼                                  ▼
┌────────────┐    ┌──────────────┐    ┌────────────┐
│ Autonomy   │───▶│ Verify Core  │───▶│   Rover    │
│ Planner    │    │ Gate Node    │    │ Actuators  │
└────────────┘    └──────────────┘    └────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Audit Log   │
                  │  (JSONL)     │
                  └──────────────┘
```

**Key invariant**: The autonomy planner publishes to `/proposed_action`. Only the Verify Core gate publishes to `/cmd_vel`. Denied actions never reach the actuator topic.

## Packages

| Package | Purpose |
|---------|---------|
| `verify_core_gate` | Policy gate node, cmd_vel interceptor |
| `rover_sim` | Rover model, Gazebo world, autonomy planner |

## Quick Start (Docker)

```bash
cd ros2_ws
docker compose up --build
```

This launches:
1. The Verify Core gate node (evaluating policy)
2. The autonomy planner (proposing actions)
3. Audit logging to `/tmp/verify_core_audit.jsonl`

## Quick Start (Local ROS 2 Jazzy)

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash

# Terminal 1: Launch gate
ros2 launch verify_core_gate gate.launch.py

# Terminal 2: Launch simulation
ros2 launch rover_sim simulation.launch.py

# Terminal 3: Start autonomy planner
ros2 run rover_sim autonomy_planner
```

## Topics

| Topic | Type | Publisher | Purpose |
|-------|------|-----------|---------|
| `/proposed_action` | `std_msgs/String` | autonomy_planner | JSON robot action proposals |
| `/cmd_vel` | `geometry_msgs/Twist` | gate_node | Approved velocity commands |
| `/gate_decision` | `std_msgs/String` | gate_node | Allow/deny decisions (JSON) |
| `/security_events` | `std_msgs/String` | interceptor | Bypass attempt alerts |

## Demo Sequence

The autonomy planner cycles through:
1. **Normal move** (0.3 m/s, normal zone) → ALLOW
2. **Unsafe speed** (5.0 m/s, normal zone) → DENY
3. **Restricted zone entry** (0.2 m/s, restricted) → DENY
4. **Normal turn** (0.5 rad/s) → ALLOW
5. **Human zone too fast** (0.8 m/s, human nearby) → DENY
6. **Stop command** → ALLOW

## Audit Log

Decisions are logged to `/tmp/verify_core_audit.jsonl`:

```json
{"timestamp": 1719360000.0, "decision": "ALLOW", "reason": "within_policy_bounds", "nonce": "abc123", "policy_epoch": 1}
{"timestamp": 1719360002.0, "decision": "DENY", "reason": "speed_exceeds_normal_limit_5.00>1.0", "nonce": "def456", "policy_epoch": 1}
```

## Zone Map

| Zone | Location (x, y) | Color | Speed Limit |
|------|-----------------|-------|-------------|
| Restricted | (2–4, 2–4) | Red | 0 (entry denied) |
| Human Zone | (-4 to -2, -1 to 1) | Yellow | 0.2 m/s |
| Loading Dock | (-1 to 1, -4 to -2) | Green | 0.1 m/s |
| Normal | Everywhere else | — | 1.0 m/s |
