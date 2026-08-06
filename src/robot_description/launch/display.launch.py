# display.launch.py
# Standard visualization template for ROS 2 Humble.

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Resolve package installation directory
    package_name = 'robot_description'
    pkg_share = get_package_share_directory(package_name)

    # 2. Get target paths for the URDF
    urdf_path = os.path.join(pkg_share, 'urdf', 'robot.urdf')

    # 3. Read the XML content
    with open(urdf_path, 'r') as file:
        robot_urdf_content = file.read()

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
    # Renders the actual 3D interface.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
