"""A dependency-light bright-region detector for the simulated RGB camera."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


class ObjectDetector(Node):
    """Emit one image-wide detection when a bright pixel is present."""

    def __init__(self):
        super().__init__('object_detector')
        self.subscription = self.create_subscription(
            Image, '/head_camera/image_raw', self.on_image, 10)
        self.publisher = self.create_publisher(Detection2DArray, '/detections', 10)

    def on_image(self, image):
        """Publish a coarse candidate without requiring OpenCV or a model download."""
        if image.encoding not in ('rgb8', 'bgr8') or not image.data:
            return
        # RGB/BGR image bytes: accepting any mostly bright pixel keeps this baseline
        # deterministic and makes it easy to replace with a trained detector later.
        if not any(value > 220 for value in image.data[::3]):
            return
        result = Detection2DArray()
        result.header = image.header
        detection = Detection2D()
        detection.bbox.center.position.x = image.width / 2.0
        detection.bbox.center.position.y = image.height / 2.0
        detection.bbox.size_x = float(image.width)
        detection.bbox.size_y = float(image.height)
        hypothesis = ObjectHypothesisWithPose()
        hypothesis.hypothesis.class_id = 'bright_object'
        hypothesis.hypothesis.score = 0.5
        detection.results.append(hypothesis)
        result.detections.append(detection)
        self.publisher.publish(result)


def main(args=None):
    """Run the camera perception baseline."""
    rclpy.init(args=args)
    node = ObjectDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
