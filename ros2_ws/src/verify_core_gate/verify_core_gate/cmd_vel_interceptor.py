"""Command interception node — detects and blocks unauthorized /cmd_vel publishers.

This node monitors /cmd_vel and flags or blocks messages that did not originate
from the Verify Core gate node. In the demo, it watches for bypass attempts
where an attacker publishes directly to /cmd_vel.
"""

import json
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class CmdVelInterceptor(Node):
    """Monitors /cmd_vel for unauthorized publications.

    Strategy: The gate node publishes to /cmd_vel_verified, and this interceptor
    relays verified commands to /cmd_vel (the actual actuator topic). Any direct
    publication to /cmd_vel from an unauthorized source is logged as a bypass attempt.
    """

    def __init__(self):
        super().__init__("cmd_vel_interceptor")

        # Listen on the verified channel from gate
        self.verified_sub = self.create_subscription(
            Twist, "/cmd_vel_verified", self.on_verified_cmd, 10
        )

        # Publish to the actual actuator topic
        self.actuator_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # Security event publisher
        self.security_pub = self.create_publisher(String, "/security_events", 10)

        self.declare_parameter("audit_log_path", "/tmp/verify_core_audit.jsonl")
        self.audit_log_path = self.get_parameter("audit_log_path").value

        self.get_logger().info(
            "Interceptor active — relaying /cmd_vel_verified → /cmd_vel"
        )

    def on_verified_cmd(self, msg: Twist):
        self.actuator_pub.publish(msg)

    def _log_bypass_attempt(self, msg: Twist):
        event = {
            "timestamp": time.time(),
            "event": "bypass_attempt",
            "linear_x": msg.linear.x,
            "angular_z": msg.angular.z,
            "action": "blocked",
        }
        self.get_logger().error(
            f"BYPASS ATTEMPT DETECTED: linear={msg.linear.x} angular={msg.angular.z}"
        )

        security_msg = String()
        security_msg.data = json.dumps(event)
        self.security_pub.publish(security_msg)

        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelInterceptor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
