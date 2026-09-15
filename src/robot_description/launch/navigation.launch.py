"""Launch state estimation and Nav2 against the simulated IMU and lidar."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Provide localization and navigation configuration without spawning Gazebo."""
    share = get_package_share_directory('robot_description')
    nav2_share = get_package_share_directory('nav2_bringup')
    return LaunchDescription([
        Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node',
             output='screen', parameters=[os.path.join(share, 'config', 'ekf.yaml')]),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'navigation_launch.py')),
            launch_arguments={'use_sim_time': 'true', 'params_file': os.path.join(
                share, 'config', 'nav2_params.yaml')}.items()),
    ])
