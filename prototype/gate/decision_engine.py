"""Deterministic decision engine: evaluates an action request against a compiled policy.

This is the core safety logic.  It checks — in order — actor identity, action/target
match, speed bounds, angle bounds, zone allowance, and human-proximity constraints.
If any check fails the request is denied immediately (fail-closed).
"""

from __future__ import annotations

from gate.schemas import ActionRequest, Decision, GateDecision
from policy.compiler import CompiledPolicy


def evaluate(request: ActionRequest, policy: CompiledPolicy) -> GateDecision:
    """Evaluate *request* against *policy* and return an ALLOW or DENY decision."""

    # --- Actor identity ---
    if request.actor != policy.actor:
        return _deny(request, "actor_not_authorized")

    # --- Policy epoch ---
    if request.policy_epoch != policy.policy_epoch:
        return _deny(request, "policy_epoch_mismatch")

    # --- Find matching rule ---
    rule = policy.find_rule(request.action, request.target)
    if rule is None:
        return _deny(request, "no_matching_rule")

    # --- Speed check ---
    speed = request.parameters.get("speed")
    if speed is not None and speed > rule.max_speed:
        return _deny(request, "speed_exceeds_limit")

    # --- Angle check ---
    angle = request.parameters.get("angle_degrees")
    if angle is not None:
        if angle < rule.min_angle_degrees or angle > rule.max_angle_degrees:
            return _deny(request, "angle_out_of_range")

    # --- Zone check ---
    zone = request.context.get("zone")
    if zone is not None and rule.allowed_zones and zone not in rule.allowed_zones:
        return _deny(request, "zone_not_allowed")

    # --- Human proximity ---
    human_nearby = request.context.get("human_nearby", False)
    if human_nearby and rule.deny_when_human_nearby:
        return _deny(request, "human_nearby_movement_denied")

    # --- All checks passed ---
    return GateDecision(
        decision=Decision.ALLOW,
        reason="within_policy_bounds",
        action_hash=request.canonical_hash(),
        nonce=request.nonce,
    )


def _deny(request: ActionRequest, reason: str) -> GateDecision:
    return GateDecision(
        decision=Decision.DENY,
        reason=reason,
        action_hash=request.canonical_hash(),
        nonce=request.nonce,
    )
