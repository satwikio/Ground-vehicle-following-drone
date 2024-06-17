import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2 
from cv2 import aruco
import numpy as np



def calc_vel(corners_tl, cx, cy):
    tl, tr, br, bl = corners_tl[0], corners_tl[1], corners_tl[2], corners_tl[3]
    aurco_center = [tl[i]/4 + tr[i]/4 + br[i]/4 + bl[i]/4 for i in range(2)]
    tan_theta = (tr[1]-tl[1])/(tr[0] - tl[1])
    aurco_angle = np.arctan(tan_theta)

    kp, ki, kd = 0.001, 0.01, 0.01
    c_error = np.array([cx - aurco_center[0], cy - aurco_center[1]])
    v_linear = kp*c_error
    v_angular = kp*aurco_angle

    vel = Twist()
    vel.linear.x = v_linear[1]
    vel.linear.y = v_linear[0]
    vel.angular.z = v_angular
    return vel

    
def find_blue_box_corners(image):

    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define the lower and upper bounds for blue color
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Find contours in the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print(type(_))
    
    if _ is None:
        return -1
        #corners_tl = []
    
    else: 
    # Get the bounding box for each contour
        bounding_boxes = [cv2.boundingRect(contour) for contour in contours]

        #print(bounding_boxes)
        # Sort the bounding boxes based on area (assuming the largest one is the blue box)
        bounding_boxes.sort(key=lambda x: x[2] * x[3], reverse=True)
        
        # Extract the coordinates of the corners of the largest bounding box
        x, y, w, h = bounding_boxes[0]
        # top_left = (x, y)
        # top_right = (x + w, y)
        # bottom_right = (x + w, y + h)
        # bottom_left = (x, y + h)
        
        top_left = (x, y + h)
        top_right = (x + w, y + h)                # vel.linear.x = 0.0
                # vel.linear.y = 0.0
                # vel.angular.z = 0.0
                # self.vel_pub_.publish(vel)
    #return 'corners_tl'

# Draw bounding box around the blue box
def draw_bounding_box(image, corners):
    cv2.polylines(image, [np.array(corners)], True, (0, 0, 255), 2)
    return image





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

            #corners_tl = aurco_det(cv_image)
            corners_tl = find_blue_box_corners(cv_image)
            #print(corners_tl)

            if corners_tl == -1 :
                vel = Twist()
                vel.linear.x = 0.0
                vel.linear.y = 0.0
                vel.angular.z = 0.0
                self.vel_pub_.publish(vel)
            else :
                image_with_box = draw_bounding_box(cv_image, corners_tl)
                cv2.imshow("Blue Box", image_with_box)
                vel = calc_vel(corners_tl, cx, cy)
                #print(vel)
                # vel.linear.x = 0.0
                # vel.linear.y = 0.0
                # vel.angular.z = 0.0
                # self.vel_pub_.publish(vel)
                self.vel_pub_.publish(vel)
            
            

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