# display.launch.py
# Standard visualization template for ROS 2 Humble.

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    # 1. Resolve package installation directory
    package_name = 'robot_description'
    pkg_share = get_package_share_directory(package_name)

    # 2. Get target paths for the URDF and the saved RViz config
    urdf_path = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'urdf.rviz')

    # Expand macros at launch time, so RViz always sees the canonical model.
    # Command() builds one shell-style string and tokenizes it, so the path
    # is quoted here to survive spaces or other special characters in it
    # (e.g. a workspace directory like "ROS2 PROJECTS").
    robot_urdf_content = Command(['xacro ', '"', urdf_path, '"'])

    # Define Node 1: robot_state_publisher
    # Reads the URDF string and publishes to /robot_description and TF frames.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_urdf_content
        }]
    )

    # Define Node 2: joint_state_publisher_gui
    # Provides slider UI elements to rotate continuous joint frames.
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # Define Node 3: rviz2
    # Renders the actual 3D interface, pre-loaded with Fixed Frame=base_link
    # and the RobotModel/TF displays already added (rviz/urdf.rviz).
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
