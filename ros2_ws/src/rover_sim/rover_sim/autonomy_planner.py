"""Simple autonomy planner that publishes proposed actions to the Verify Core gate.

This node simulates an AI planner proposing robot actions. In the full system,
proposed actions go to the Verify Core gate (not directly to /cmd_vel).
"""

import json
import time
import uuid

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AutonomyPlanner(Node):
    def __init__(self):
        super().__init__("autonomy_planner")
        self.publisher_ = self.create_publisher(String, "/proposed_action", 10)
        self.timer = self.create_timer(2.0, self.publish_action)
        self.action_index = 0
        self.get_logger().info("Autonomy planner started - publishing to /proposed_action")

    def publish_action(self):
        actions = self._demo_sequence()
        if self.action_index >= len(actions):
            self.action_index = 0

        action = actions[self.action_index]
        action["timestamp"] = time.time()
        action["nonce"] = uuid.uuid4().hex

        msg = String()
        msg.data = json.dumps(action)
        self.publisher_.publish(msg)
        self.get_logger().info(
            f"Proposed: {action['action']} linear_x={action.get('linear_x', 0)}"
        )
        self.action_index += 1

    def _demo_sequence(self):
        """Sequence of actions demonstrating allow/deny/block scenarios."""
        return [
            {
                "robot_id": "rover-01",
                "action": "move",
                "source": "autonomy_planner",
                "linear_x": 0.3,
                "angular_z": 0.0,
                "zone": "normal",
                "human_nearby": False,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
            {
                "robot_id": "rover-01",
                "action": "move",
                "source": "autonomy_planner",
                "linear_x": 5.0,
                "angular_z": 0.0,
                "zone": "normal",
                "human_nearby": False,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
            {
                "robot_id": "rover-01",
                "action": "move",
                "source": "autonomy_planner",
                "linear_x": 0.2,
                "angular_z": 0.0,
                "zone": "restricted",
                "human_nearby": False,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
            {
                "robot_id": "rover-01",
                "action": "turn",
                "source": "autonomy_planner",
                "linear_x": 0.0,
                "angular_z": 0.5,
                "zone": "normal",
                "human_nearby": False,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
            {
                "robot_id": "rover-01",
                "action": "move",
                "source": "autonomy_planner",
                "linear_x": 0.8,
                "angular_z": 0.0,
                "zone": "human_zone",
                "human_nearby": True,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
            {
                "robot_id": "rover-01",
                "action": "stop",
                "source": "autonomy_planner",
                "linear_x": 0.0,
                "angular_z": 0.0,
                "zone": "normal",
                "human_nearby": False,
                "mission_id": "demo-001",
                "policy_epoch": 1,
            },
        ]


def main(args=None):
    rclpy.init(args=args)
    node = AutonomyPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
