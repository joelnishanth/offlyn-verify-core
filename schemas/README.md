# Robotics Action Schema

This directory defines the **structured robot action format** used by Offlyn Verify Core for the ROS 2 robotics integration.

## Schema

- [`robotics_action.schema.json`](robotics_action.schema.json) — JSON Schema (2020-12) defining the action request format.

## Design Principles

1. **Machine-checkable**: Every field has a defined type, range, and purpose.
2. **Fail-closed**: Missing required fields or out-of-range values cause rejection before policy evaluation.
3. **Action-bound**: Each request is tied to a specific robot, action type, and policy epoch.
4. **Replay-protected**: The `nonce` field prevents request reuse.
5. **Position-aware**: Optional position data enables geofence and zone boundary enforcement.

## Required Fields

| Field | Type | Purpose |
|-------|------|---------|
| `robot_id` | string | Identifies which robot is proposing the action |
| `action` | enum | One of: `move`, `stop`, `turn`, `emergency_stop` |
| `source` | string | Which component proposed the action |

## Conditional Requirements

| Action | Additional Required Fields |
|--------|---------------------------|
| `move` | `linear_x` |
| `turn` | `angular_z` |
| `stop` | (none) |
| `emergency_stop` | (none) |

## Optional Fields

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `linear_x` | number | — | Forward velocity (m/s) |
| `angular_z` | number | — | Rotational velocity (rad/s) |
| `zone` | enum | `"normal"` | Current/target zone |
| `human_nearby` | boolean | `false` | Human detection flag |
| `mission_id` | string | — | Traceability reference |
| `position` | object | — | Robot pose for zone checks |
| `timestamp` | number | — | When the action was proposed |
| `nonce` | string | — | Replay protection |
| `policy_epoch` | integer | — | Expected policy version |

## Zone Values

| Zone | Meaning |
|------|---------|
| `normal` | Standard operating area, full speed allowed |
| `restricted` | Entry forbidden — action will be denied |
| `human_zone` | Human-occupied area — reduced speed enforced |
| `loading_dock` | Low-speed zone near infrastructure |

## Relationship to Existing Prototype

This schema extends the existing `ActionRequest` model in `prototype/gate/schemas.py`. The mapping:

| Robotics Schema | Prototype `ActionRequest` |
|-----------------|--------------------------|
| `robot_id` | `actor` |
| `action` | `action` |
| `source` | (new — identifies proposing component) |
| `linear_x`, `angular_z` | `parameters.speed`, `parameters.angle_degrees` |
| `zone` | `context.zone` |
| `human_nearby` | `context.human_nearby` |
| `nonce` | `nonce` |
| `policy_epoch` | `policy_epoch` |

## Validation

```bash
# Validate an action against the schema (requires jsonschema or check-jsonschema)
check-jsonschema --schemafile schemas/robotics_action.schema.json schemas/examples/valid/move_forward.json
```

## Examples

- [`examples/valid/`](examples/valid/) — Actions that pass schema validation
- [`examples/invalid/`](examples/invalid/) — Actions that fail validation (with documented reasons)
