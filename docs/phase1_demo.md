# Phase 1 Demo Script — Robotics MVP

This document describes how to run the Phase 1 demo showing Offlyn Verify Core
enforcing policy at the actuation boundary for a ROS 2 rover.

## What the Demo Proves

1. **ALLOW**: Safe commands within policy reach the robot actuators
2. **DENY**: Unsafe speed, restricted zone, and human-proximity violations are blocked
3. **BYPASS BLOCK**: Direct publication to /cmd_vel bypassing the gate is detected
4. **AUDIT**: Every decision is logged with timestamp, reason, and policy hash

## Quick Run (Docker)

```bash
cd ros2_ws
docker compose up --build
```

Watch the logs — you'll see alternating ALLOW and DENY decisions as the autonomy planner cycles through its demo sequence.

## Quick Run (Local ROS 2 Jazzy)

```bash
# Terminal 1: Start gate
source /opt/ros/jazzy/setup.bash
cd ros2_ws && colcon build --symlink-install && source install/setup.bash
ros2 launch verify_core_gate gate.launch.py

# Terminal 2: Start simulation (optional, for visual)
ros2 launch rover_sim simulation.launch.py

# Terminal 3: Start autonomy planner
ros2 run rover_sim autonomy_planner

# Terminal 4: Watch decisions
ros2 topic echo /gate_decision
```

## Demo Sequence

The autonomy planner publishes these actions in order:

| Step | Action | Speed | Zone | Human | Expected |
|------|--------|-------|------|-------|----------|
| 1 | move | 0.3 m/s | normal | no | ALLOW |
| 2 | move | 5.0 m/s | normal | no | DENY (speed) |
| 3 | move | 0.2 m/s | restricted | no | DENY (zone) |
| 4 | turn | 0.5 rad/s | normal | no | ALLOW |
| 5 | move | 0.8 m/s | human_zone | yes | DENY (human) |
| 6 | stop | — | normal | no | ALLOW |

## Bypass Attack Test

In a separate terminal, attempt direct /cmd_vel publication:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 2.0}, angular: {z: 0.0}}' --once
```

The interceptor node detects this and logs a security event.

## Viewing Audit Log

```bash
# Live tail
tail -f /tmp/verify_core_audit.jsonl

# Pretty print
cat /tmp/verify_core_audit.jsonl | python3 -m json.tool --no-ensure-ascii
```

## Running Policy Tests (No ROS 2 Required)

```bash
cd prototype
python -m pytest tests/test_rover_policy.py tests/test_robotics_schema.py -v
```

## Expected Output

```
tests/test_rover_policy.py::TestSpeedPolicy::test_normal_speed_allowed PASSED
tests/test_rover_policy.py::TestSpeedPolicy::test_over_speed_denied PASSED
tests/test_rover_policy.py::TestZonePolicy::test_restricted_zone_denied PASSED
tests/test_rover_policy.py::TestHumanProximity::test_human_nearby_high_speed_denied PASSED
tests/test_rover_policy.py::TestAttackScenarios::test_attack_unsafe_speed PASSED
tests/test_rover_policy.py::TestAttackScenarios::test_attack_restricted_zone_entry PASSED
...
81 passed
```

## Success Criteria Checklist

- [x] Rover receives proposed actions from autonomy layer
- [x] Verify Core evaluates each action against policy
- [x] Allowed actions reach /cmd_vel
- [x] Denied actions never reach /cmd_vel
- [x] Restricted-zone policy works
- [x] Speed-limit policy works
- [x] Human-proximity policy works
- [x] Every decision is logged
- [ ] Demo video recorded (pending)
