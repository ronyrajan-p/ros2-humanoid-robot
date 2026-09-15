"""Launch the camera perception baseline."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Start the detector after gazebo.launch.py is running."""
    return LaunchDescription([
        Node(package='robot_description', executable='object_detector', output='screen'),
    ])
