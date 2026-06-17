"""Policy compiler: loads YAML policy files into structured Python objects.

The compiler validates policy structure and produces a canonical byte
representation used for signing and verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class PolicyRule:
    action: str
    target: str
    max_speed: float = 1.0
    min_angle_degrees: float = -180.0
    max_angle_degrees: float = 180.0
    max_altitude_meters: float = float("inf")
    min_altitude_meters: float = 0.0
    allowed_zones: list[str] = field(default_factory=list)
    deny_when_human_nearby: bool = False
    geofence: dict | None = None


@dataclass
class CompiledPolicy:
    policy_id: str
    policy_epoch: int
    actor: str
    rules: list[PolicyRule]
    raw_yaml: str
    canonical_bytes: bytes
    policy_hash: str
    signature: bytes = b""

    def find_rule(self, action: str, target: str) -> PolicyRule | None:
        for rule in self.rules:
            if rule.action == action and rule.target == target:
                return rule
        return None


def compile_policy(path: Path) -> CompiledPolicy:
    """Parse a YAML policy file and return a CompiledPolicy with a canonical hash."""
    raw = path.read_text()
    data = yaml.safe_load(raw)

    rules = []
    for r in data.get("rules", []):
        rules.append(
            PolicyRule(
                action=r["action"],
                target=r["target"],
                max_speed=r.get("max_speed", 1.0),
                min_angle_degrees=r.get("min_angle_degrees", -180.0),
                max_angle_degrees=r.get("max_angle_degrees", 180.0),
                max_altitude_meters=r.get("max_altitude_meters", float("inf")),
                min_altitude_meters=r.get("min_altitude_meters", 0.0),
                allowed_zones=r.get("allowed_zones", []),
                deny_when_human_nearby=r.get("deny_when_human_nearby", False),
                geofence=r.get("geofence"),
            )
        )

    canonical = json.dumps(
        {
            "policy_id": data["policy_id"],
            "policy_epoch": data["policy_epoch"],
            "actor": data["actor"],
            "rules": [
                {
                    "action": rl.action,
                    "target": rl.target,
                    "max_speed": rl.max_speed,
                    "allowed_zones": sorted(rl.allowed_zones),
                }
                for rl in rules
            ],
        },
        sort_keys=True,
    ).encode()

    policy_hash = hashlib.sha256(canonical).hexdigest()

    return CompiledPolicy(
        policy_id=data["policy_id"],
        policy_epoch=data["policy_epoch"],
        actor=data["actor"],
        rules=rules,
        raw_yaml=raw,
        canonical_bytes=canonical,
        policy_hash=policy_hash,
    )
