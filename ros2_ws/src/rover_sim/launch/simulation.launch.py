"""Launch file for Offlyn Verify Core rover simulation.

Launches Gazebo with the demo world and spawns the rover model.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("rover_sim")
    world_file = os.path.join(pkg_share, "worlds", "verify_core_demo.world")
    urdf_file = os.path.join(pkg_share, "urdf", "rover.urdf")

    with open(urdf_file, "r") as f:
        robot_description = f.read()

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation clock",
        ),

        # Gazebo server
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(
                    get_package_share_directory("gazebo_ros"),
                    "launch",
                    "gazebo.launch.py",
                )
            ]),
            launch_arguments={"world": world_file}.items(),
        ),

        # Robot state publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": robot_description,
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }],
        ),

        # Spawn rover in Gazebo
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-topic", "robot_description",
                "-entity", "verify_core_rover",
                "-x", "0.0",
                "-y", "0.0",
                "-z", "0.1",
            ],
            output="screen",
        ),
    ])
