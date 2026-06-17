"""AI planner simulator.

In production this would be an LLM or agentic planner.  For the prototype
it generates deterministic ActionRequest objects for testing.
"""

from __future__ import annotations

from gate.schemas import ActionRequest


def propose_action(
    actor: str,
    action: str,
    target: str,
    parameters: dict | None = None,
    context: dict | None = None,
    policy_epoch: int = 1,
) -> ActionRequest:
    """Create a proposed action request from the planner."""
    return ActionRequest(
        actor=actor,
        action=action,
        target=target,
        parameters=parameters or {},
        context=context or {},
        policy_epoch=policy_epoch,
    )


def safe_move() -> ActionRequest:
    return propose_action(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 45, "speed": 0.4},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def speed_violation() -> ActionRequest:
    return propose_action(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 30, "speed": 1.2},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def angle_violation() -> ActionRequest:
    return propose_action(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 120, "speed": 0.3},
        context={"zone": "safe_area_a", "human_nearby": False},
    )


def geofence_violation() -> ActionRequest:
    return propose_action(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.2},
        context={"zone": "restricted_zone_x", "human_nearby": False},
    )


def human_nearby_violation() -> ActionRequest:
    return propose_action(
        actor="robot_planner_01",
        action="move_joint",
        target="joint_2",
        parameters={"angle_degrees": 10, "speed": 0.2},
        context={"zone": "safe_area_a", "human_nearby": True},
    )
