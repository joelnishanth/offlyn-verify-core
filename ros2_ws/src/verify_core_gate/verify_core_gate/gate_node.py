"""Offlyn Verify Core Gate Node — the actuation boundary for ROS 2 robots.

Subscribes to /proposed_action, evaluates each action against active policy,
and publishes approved commands to /cmd_vel. Denied commands never reach
the actuator topic. Every decision is logged.
"""

import json
import time
import uuid
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "prototype"))

from gate.robotics_schemas import RoboticsActionRequest, Zone, RobotAction


class VerifyCoreGateNode(Node):
    def __init__(self):
        super().__init__("verify_core_gate")

        # Policy parameters
        self.declare_parameter("max_speed_normal", 1.0)
        self.declare_parameter("max_speed_human_zone", 0.2)
        self.declare_parameter("max_speed_loading_dock", 0.1)
        self.declare_parameter("max_angular_speed", 2.0)
        self.declare_parameter("policy_epoch", 1)
        self.declare_parameter("audit_log_path", "/tmp/verify_core_audit.jsonl")

        self.max_speed_normal = self.get_parameter("max_speed_normal").value
        self.max_speed_human = self.get_parameter("max_speed_human_zone").value
        self.max_speed_dock = self.get_parameter("max_speed_loading_dock").value
        self.max_angular = self.get_parameter("max_angular_speed").value
        self.policy_epoch = self.get_parameter("policy_epoch").value
        self.audit_log_path = self.get_parameter("audit_log_path").value

        # Subscribe to proposed actions from autonomy layer
        self.action_sub = self.create_subscription(
            String, "/proposed_action", self.on_proposed_action, 10
        )

        # Publish approved commands to actuator topic
        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # Publish gate decisions for monitoring
        self.decision_pub = self.create_publisher(String, "/gate_decision", 10)

        self.get_logger().info(
            "Verify Core Gate active — evaluating /proposed_action → /cmd_vel"
        )

    def on_proposed_action(self, msg: String):
        try:
            data = json.loads(msg.data)
            action_req = RoboticsActionRequest(**data)
        except Exception as e:
            self._log_decision("DENY", "schema_validation_failed", str(e), msg.data)
            return

        decision, reason = self._evaluate(action_req)

        if decision == "ALLOW":
            twist = Twist()
            twist.linear.x = action_req.linear_x or 0.0
            twist.angular.z = action_req.angular_z or 0.0
            self.cmd_vel_pub.publish(twist)
            self.get_logger().info(
                f"ALLOW: {action_req.action.value} "
                f"v={twist.linear.x:.2f} w={twist.angular.z:.2f}"
            )
        else:
            self.get_logger().warn(f"DENY: {action_req.action.value} — {reason}")

        self._log_decision(decision, reason, action_req.nonce, msg.data)
        self._publish_decision(decision, reason, action_req)

    def _evaluate(self, req: RoboticsActionRequest) -> tuple:
        """Evaluate action against active policy. Returns (decision, reason)."""

        # Emergency stop is always allowed
        if req.action == RobotAction.EMERGENCY_STOP:
            return ("ALLOW", "emergency_stop_always_permitted")

        # Stop is always allowed
        if req.action == RobotAction.STOP:
            return ("ALLOW", "stop_always_permitted")

        # Restricted zone — deny all movement
        if req.zone == Zone.RESTRICTED:
            return ("DENY", "zone_restricted_entry_forbidden")

        # Speed checks based on zone
        speed = abs(req.linear_x or 0.0)
        if req.zone == Zone.HUMAN_ZONE or req.human_nearby:
            if speed > self.max_speed_human:
                return ("DENY", f"speed_exceeds_human_zone_limit_{speed:.2f}>{self.max_speed_human}")
        elif req.zone == Zone.LOADING_DOCK:
            if speed > self.max_speed_dock:
                return ("DENY", f"speed_exceeds_loading_dock_limit_{speed:.2f}>{self.max_speed_dock}")
        else:
            if speed > self.max_speed_normal:
                return ("DENY", f"speed_exceeds_normal_limit_{speed:.2f}>{self.max_speed_normal}")

        # Angular speed check
        angular = abs(req.angular_z or 0.0)
        if angular > self.max_angular:
            return ("DENY", f"angular_speed_exceeds_limit_{angular:.2f}>{self.max_angular}")

        return ("ALLOW", "within_policy_bounds")

    def _log_decision(self, decision: str, reason: str, nonce: str, raw_data: str):
        entry = {
            "timestamp": time.time(),
            "decision": decision,
            "reason": reason,
            "nonce": nonce,
            "policy_epoch": self.policy_epoch,
        }
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            self.get_logger().error("Failed to write audit log")

        decision_msg = String()
        decision_msg.data = json.dumps(entry)
        self.decision_pub.publish(decision_msg)

    def _publish_decision(self, decision: str, reason: str, req: RoboticsActionRequest):
        entry = {
            "decision": decision,
            "reason": reason,
            "robot_id": req.robot_id,
            "action": req.action.value,
            "nonce": req.nonce,
        }
        msg = String()
        msg.data = json.dumps(entry)
        self.decision_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = VerifyCoreGateNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
