import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2 
from cv2 import aruco
import numpy as np

marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

param_markers = aruco.DetectorParameters_create()

def calc_vel(corners_tl, cx, cy):
    tl, tr, br, bl = corners_tl[0], corners_tl[1], corners_tl[2], corners_tl[3]
    aurco_center = [tl[i]/4 + tr[i]/4 + br[i]/4 + bl[i]/4 for i in range(2)]
    tan_theta = (tr[1]-tl[1])/(tr[0] - tl[1])
    aurco_angle = np.arctan(tan_theta)

    kp, ki, kd = 0.01, 0.01, 0.01
    c_error = np.array([cx - aurco_center[0], cy - aurco_center[1]])
    v_linear = kp*c_error
    v_angular = kp*aurco_angle

    vel = Twist()
    vel.linear.x = v_linear[0]
    vel.linear.y = v_linear[1]
    vel.angular.z = v_angular

    print(vel)
    return vel

def aurco_det(frame):
    #corners_tl = None
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            cv2.polylines(
                frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[1].ravel()
            top_left = corners[0].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()
            corners_tl = [top_left, top_right, bottom_right, bottom_left]
            
            #print(corners)
            cv2.putText(
                frame,
                f"id: {ids[0]}",
                top_right,
                cv2.FONT_HERSHEY_PLAIN,
                1.3,
                (200, 100, 0),
                2,
                cv2.LINE_AA,
            )
            return corners_tl
            # print(ids, "  ", corners)
    #cv2.imshow("frame", frame)

    else:
        return -1
    


class ImageSubscriber(Node):


    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(Image, '/drone/bottom/image_raw', self.image_callback, 10)
        self.vel_pub_ = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            h, w, c  = cv_image.shape
            cx, cy = w/2, h/2

            corners_tl = aurco_det(cv_image)

            if corners_tl != -1 :
                vel = calc_vel(corners_tl, cx, cy)
                self.vel_pub_.publish(vel)
            else:
                pass

            # Display the image
            cv2.imshow('Image from drone', cv_image)
            cv2.waitKey(1)  # Wait for a short time to process GUI events
        except Exception as e:
            self.get_logger().error('Error processing image: %s' % str(e))

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    try:
        rclpy.spin(image_subscriber)
    except KeyboardInterrupt:
        pass

    # Destroy OpenCV windows and shutdown ROS
    cv2.destroyAllWindows()
    image_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()