"""Launch MoveIt 2 planning for the humanoid upper body."""

import os

import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    """Start move_group using the package-owned semantic and controller config."""
    share = get_package_share_directory('robot_description')
    xacro = os.path.join(share, 'urdf', 'robot.urdf.xacro')
    moveit = os.path.join(share, 'moveit')
    with open(os.path.join(moveit, 'humanoid.srdf'), encoding='utf-8') as stream:
        semantic = stream.read()
    with open(os.path.join(moveit, 'kinematics.yaml'), encoding='utf-8') as stream:
        kinematics = yaml.safe_load(stream)
    with open(os.path.join(moveit, 'joint_limits.yaml'), encoding='utf-8') as stream:
        joint_limits = yaml.safe_load(stream)
    with open(os.path.join(moveit, 'moveit_controllers.yaml'), encoding='utf-8') as stream:
        controllers = yaml.safe_load(stream)
    return LaunchDescription([
        Node(
            package='moveit_ros_move_group', executable='move_group', output='screen',
            parameters=[{
                # Quoted so the path survives spaces (Command() tokenizes the
                # built string like a shell would).
                'robot_description': Command(['xacro ', '"', xacro, '"']),
                'robot_description_semantic': semantic,
                'robot_description_kinematics': kinematics,
                'robot_description_planning': joint_limits,
                'moveit_controller_manager': (
                    'moveit_simple_controller_manager/'
                    'MoveItSimpleControllerManager'
                ),
                'moveit_simple_controller_manager': controllers,
                'planning_pipelines': ['ompl'],
                'default_planning_pipeline': 'ompl',
            }],
        ),
    ])
