import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import csv
import numpy as np
import pandas as pd

l_err_x  = []
l_err_y  = [] 
a_err = []
def calc_vel(corners_tl,wheels_l, wheels_r , cx, cy):
    tl, tr, br, bl = corners_tl[0], corners_tl[1], corners_tl[2], corners_tl[3]
    tl_r, tr_r, br_r, bl_r = wheels_r[0], wheels_r[1], wheels_r[2], wheels_r[3]
    tl_l, tr_l, br_l, bl_l = wheels_l[0], wheels_l[1], wheels_l[2], wheels_l[3]
    aurco_center = [tl[i] / 4 + tr[i] / 4 + br[i] / 4 + bl[i] / 4 for i in range(2)]
    wheel_l_center = [tl_l[i] / 4 + tr_l[i] / 4 + br_l[i] / 4 + bl_l[i] / 4 for i in range(2)]
    wheel_r_center = [tl_r[i] / 4 + tr_r[i] / 4 + br_r[i] / 4 + bl_r[i] / 4 for i in range(2)]
    #print('L', wheel_l_center)
    #print('R', wheel_r_center)
    tan_theta = (wheel_r_center[1]-wheel_l_center[1])/(wheel_r_center[0] - wheel_l_center[1])
    #print("tan_theta", tan_theta)
    aurco_angle = np.arctan(tan_theta)
    a_err.append(aurco_angle)
    print( a_err)

    kp, ki, kd = 0.003, 2, 0.01
    c_error = np.array([cx - aurco_center[0], cy - aurco_center[1]])
    l_err_x.append(c_error[0])
    l_err_y.append(c_error[1])
    v_linear = kp * c_error
    v_angular = ki * tan_theta
    #v_angular = ki *aurco_angle

    vel = Twist()
    vel.linear.x = (v_linear[1])
    vel.linear.y = (v_linear[0])
    vel.angular.z = v_angular
    return vel

def find_blue_box_corners(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return -1

    # Sort contours by area and get the largest one
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box coordinates
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)  # Convert to integer
    
    return box.tolist()

def find_green_box_corners(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# Define lower and upper threshold values for green color in HSV
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([70, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    #cv2.imshow(mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return -1

    # Sort contours by area and get the largest one
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box coordinates
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)  # Convert to integer

    return box.tolist()

def find_red_box_corners(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the lower range of red
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])

    # Define the lower and upper bounds for the upper range of red
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for both ranges of red
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine the masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Find contours in the combined mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return -1

    # Sort contours by area and get the largest one
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box coordinates
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)  # Convert to integer

    return box.tolist()


def draw_bounding_box(image, corners):
    points = np.array(corners, dtype=np.int32)
    cv_image_with_box = cv2.polylines(image, [points], True, (0, 0, 255), 2)
    return cv_image_with_box

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(Image, '/drone/bottom/image_raw', self.image_callback, 10)
        self.vel_pub_ = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            h, w, _ = cv_image.shape
            cx, cy = w / 2, h / 2

            corners_tl = find_blue_box_corners(cv_image)
            wheel_r = find_green_box_corners(cv_image)
            wheel_l = find_red_box_corners(cv_image)
            #print(corners_tl)

            if corners_tl == -1:
                vel = Twist()
                vel.linear.x = 0.0
                vel.linear.y = 0.0
                vel.angular.z = 0.0
                self.vel_pub_.publish(vel)
            else:
                image_with_box = draw_bounding_box(cv_image, corners_tl)
                image_with_box = draw_bounding_box(image_with_box, wheel_r)
                image_with_box = draw_bounding_box(image_with_box, wheel_l)
                cv2.imshow("Blue Box", image_with_box)
                vel = calc_vel(corners_tl,wheel_r, wheel_l, cx, cy)
                self.vel_pub_.publish(vel)

            cv2.imshow('Image from drone', cv_image)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error('Error processing image: %s' % str(e))

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    try:
        rclpy.spin(image_subscriber)
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    


    df = pd.DataFrame({
        'Array1': l_err_x,
        'Array2': l_err_y,
        'Array3': a_err
    })

# Write the DataFrame to a CSV file
    df.to_csv('arrays.csv', index=False)

    image_subscriber.destroy_node()
 

if __name__ == '__main__':
    main()
