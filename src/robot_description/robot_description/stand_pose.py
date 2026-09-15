"""Publish a conservative bent-knee pose after the trajectory controller starts."""

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import rclpy
from rclpy.node import Node

# Keep this order in sync with config/controllers.yaml and
# moveit/moveit_controllers.yaml.
JOINT_NAMES = [
    'waist_joint', 'neck_joint',
    'left_shoulder_pitch', 'left_shoulder_roll', 'left_elbow',
    'right_shoulder_pitch', 'right_shoulder_roll', 'right_elbow',
    'left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee',
    'left_ankle_pitch', 'right_hip_yaw', 'right_hip_roll',
    'right_hip_pitch', 'right_knee', 'right_ankle_pitch',
]

# Used only if config/stand_pose.yaml is not passed to the node (e.g. running
# `ros2 run robot_description stand_pose` directly, with no parameters file).
# These match the values previously hardcoded here.
DEFAULT_POSITIONS = {
    'waist_joint': 0.0, 'neck_joint': 0.0,
    'left_shoulder_pitch': 0.2, 'left_shoulder_roll': 0.0, 'left_elbow': 0.4,
    'right_shoulder_pitch': 0.2, 'right_shoulder_roll': 0.0, 'right_elbow': 0.4,
    'left_hip_yaw': 0.0, 'left_hip_roll': 0.0, 'left_hip_pitch': -0.15,
    'left_knee': 0.30, 'left_ankle_pitch': -0.15,
    'right_hip_yaw': 0.0, 'right_hip_roll': 0.0, 'right_hip_pitch': -0.15,
    'right_knee': 0.30, 'right_ankle_pitch': -0.15,
}


class StandPosePublisher(Node):
    """Send one stable, symmetric standing trajectory."""

    def __init__(self):
        super().__init__('stand_pose_publisher')
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/humanoid_trajectory_controller/joint_trajectory',
            10,
        )

        # Declare each joint's target angle as its own parameter under the
        # 'stand_positions' namespace, seeded with DEFAULT_POSITIONS.
        # config/stand_pose.yaml (passed in by gazebo.launch.py) overrides
        # these, so retuning the pose is now a config edit, not a code edit.
        for name in JOINT_NAMES:
            self.declare_parameter(f'stand_positions.{name}', DEFAULT_POSITIONS[name])

        self.timer = self.create_timer(1.0, self.publish_once)
        self.sent = False

    def publish_once(self):
        """Publish only once; the trajectory controller holds its final targets."""
        if self.sent:
            return
        message = JointTrajectory()
        message.joint_names = list(JOINT_NAMES)
        point = JointTrajectoryPoint()
        point.positions = [
            self.get_parameter(f'stand_positions.{name}')
            .get_parameter_value().double_value
            for name in JOINT_NAMES
        ]
        point.time_from_start.sec = 3
        message.points = [point]
        self.publisher.publish(message)
        self.sent = True
        self.get_logger().info('Published standing pose.')


def main(args=None):
    """Run the standing pose publisher."""
    rclpy.init(args=args)
    node = StandPosePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
