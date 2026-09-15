import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command


def generate_launch_description():

    pkg_share = get_package_share_directory('robot_description')
    urdf = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    controllers = os.path.join(pkg_share, 'config', 'controllers.yaml')
    stand_pose_params = os.path.join(pkg_share, 'config', 'stand_pose.yaml')

    # Start the world paused ("--pause") so the robot never free-falls while
    # its controllers are still loading. With 18 unactuated joints, letting
    # physics run from t=0 means the robot collapses under gravity during the
    # several seconds it takes joint_state_broadcaster and
    # humanoid_trajectory_controller to activate; the controller then has to
    # snap every joint from a fallen heap into the standing pose almost
    # instantly, which is exactly the kind of large, sudden correction that
    # makes Gazebo Classic's physics solver diverge and fling the model far
    # outside the camera view. Staying paused until a stand-pose command is
    # already queued avoids that fall-then-snap sequence entirely.
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        ),
        launch_arguments={'extra_gazebo_args': '--pause'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            # Both paths are quoted so Command()'s shell-style tokenizing
            # survives spaces in the path (e.g. a workspace directory like
            # "ROS2 PROJECTS").
            'robot_description': Command([
                'xacro ', '"', urdf, '"',
                ' controllers_file:=', '"', controllers, '"',
            ]),
            # Gazebo is the clock source here (it publishes /clock); without
            # this, robot_state_publisher runs on the wall clock instead and
            # its TF stamps drift out of sync with sim time, which shows up
            # as TF extrapolation warnings once Nav2/MoveIt are also running.
            'use_sim_time': True,
        }],
        output='screen'
    )

    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'my_robot',
            '-topic', 'robot_description'
        ],
        output='screen'
    )

    joint_state_broadcaster = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )
    trajectory_controller = Node(
        package='controller_manager', executable='spawner',
        arguments=[
            'humanoid_trajectory_controller', '--controller-manager',
            '/controller_manager',
        ],
        output='screen'
    )
    stand_pose = Node(
        package='robot_description', executable='stand_pose', output='screen',
        parameters=[stand_pose_params],
    )

    # Physics is still paused at this point (see the `gazebo` comment above).
    # stand_pose publishes its one trajectory message ~1s after it starts
    # (its internal timer), so it has already queued the standing-pose
    # command on humanoid_trajectory_controller by the time this fires.
    unpause_physics = ExecuteProcess(
        cmd=['ros2', 'service', 'call', '/unpause_physics', 'std_srvs/srv/Empty', '{}'],
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn,
        TimerAction(period=3.0, actions=[joint_state_broadcaster]),
        TimerAction(period=5.0, actions=[trajectory_controller]),
        TimerAction(period=6.0, actions=[stand_pose]),
        TimerAction(period=8.0, actions=[unpause_physics]),
    ])
