import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher = self.create_publisher(Image, '/drone/bottom/image_ra', 10)
        self.timer = self.create_timer(0.1, self.publish_image)
        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(0)  # Use the default camera (index 0)

    def publish_image(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imshow('frame', frame)
            # Convert OpenCV image to ROS Image message
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            # Publish the ROS Image message
            self.publisher.publish(ros_image)
        else:
            self.get_logger().error("Failed to capture image from camera")

def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraPublisher()
    try:
        rclpy.spin(camera_publisher)
    except KeyboardInterrupt:
        pass

    # Release the camera and shutdown ROS
    camera_publisher.cap.release()
    camera_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
