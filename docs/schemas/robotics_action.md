# Robotics Action Schema

Structured format for robot actions proposed by the autonomy layer. Verify Core evaluates every action against policy **before** it can reach `/cmd_vel` or other actuator topics.

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `robot_id` | string | Robot identifier (e.g. `rover-01`) |
| `action` | enum | One of: `move`, `stop`, `turn`, `emergency_stop` |
| `source` | string | Origin of the proposal (e.g. `autonomy_planner`) |

## Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `mission_id` | string | Mission/task ID for audit correlation |
| `linear_x` | number | Forward velocity in m/s (−2.0 to 2.0); required for `move` |
| `angular_z` | number | Yaw rate in rad/s (−π to π); required for `move` and `turn` |
| `zone` | enum | `normal`, `restricted`, or `human_zone` |
| `human_nearby` | boolean | Human proximity flag for safety policy |

## Action types

| Action | Required params | Description |
|--------|-----------------|-------------|
| `move` | `linear_x`, `angular_z` | Drive with linear and angular velocity |
| `stop` | — | Halt all motion |
| `turn` | `angular_z` | Rotate in place |
| `emergency_stop` | — | Immediate safety stop (always allowed) |

## Example (valid move)

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

## Validation

- JSON Schema: [`schemas/robotics_action.json`](../../schemas/robotics_action.json)
- Valid examples: [`schemas/examples/valid/`](../../schemas/examples/valid/)
- Invalid examples: [`schemas/examples/invalid/`](../../schemas/examples/invalid/)

Invalid or missing required fields must be rejected at the gate (fail-closed).
