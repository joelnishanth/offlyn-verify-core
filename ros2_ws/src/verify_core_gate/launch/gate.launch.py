"""Launch file for the Verify Core gate node and command interceptor."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "max_speed_normal", default_value="1.0",
            description="Maximum speed in normal zones (m/s)",
        ),
        DeclareLaunchArgument(
            "max_speed_human_zone", default_value="0.2",
            description="Maximum speed in human zones (m/s)",
        ),
        DeclareLaunchArgument(
            "max_speed_loading_dock", default_value="0.1",
            description="Maximum speed in loading dock (m/s)",
        ),
        DeclareLaunchArgument(
            "audit_log_path", default_value="/tmp/verify_core_audit.jsonl",
            description="Path to JSONL audit log file",
        ),

        # Verify Core Gate Node
        Node(
            package="verify_core_gate",
            executable="gate_node",
            name="verify_core_gate",
            output="screen",
            parameters=[{
                "max_speed_normal": LaunchConfiguration("max_speed_normal"),
                "max_speed_human_zone": LaunchConfiguration("max_speed_human_zone"),
                "max_speed_loading_dock": LaunchConfiguration("max_speed_loading_dock"),
                "audit_log_path": LaunchConfiguration("audit_log_path"),
            }],
        ),

        # Command interceptor (bypass detection)
        Node(
            package="verify_core_gate",
            executable="cmd_vel_interceptor",
            name="cmd_vel_interceptor",
            output="screen",
            parameters=[{
                "audit_log_path": LaunchConfiguration("audit_log_path"),
            }],
        ),
    ])
