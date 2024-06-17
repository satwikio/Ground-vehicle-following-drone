import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Pose
import matplotlib.pyplot as plt

tf_x = []
tf_y = []
gt_x = []
gt_y = []

class PoseSubscriber(Node):
    def __init__(self):
        super().__init__('pose_subscriber')
        
        # Arrays to store x and y values
        # self.tf_x = []
        # self.tf_y = []
        # self.gt_x = []
        # self.gt_y = []

        # Create subscriptions
        self.tf_subscription = self.create_subscription(
            TFMessage,
            '/tf',
            self.tf_callback,
            10
        )
        self.gt_subscription = self.create_subscription(
            Pose,
            '/drone/gt_pose',
            self.gt_pose_callback,
            10
        )

    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id == "base_footprint":
                tf_x.append(transform.transform.translation.x)
                tf_y.append(transform.transform.translation.y)
                #self.get_logger().info(f'TF x: {transform.transform.translation.x}, y: {transform.transform.translation.y}')

    def gt_pose_callback(self, msg):
        gt_x.append(msg.position.x)
        gt_y.append(msg.position.y)
        #self.get_logger().info(f'GT Pose x: {msg.position.x}, y: {msg.position.y}')
        #print(tf_x)
        #print(gt_x)

def main(args=None):
    rclpy.init(args=args)
    pose_subscriber = PoseSubscriber()

    try:
        rclpy.spin(pose_subscriber)
    except KeyboardInterrupt:
        pass

    pose_subscriber.destroy_node()
    plt.figure()
    plt.plot(tf_x, tf_y, label='TF Data')
    plt.plot(gt_x, gt_y, label='GT Pose Data')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.title('TF and GT Pose Data')
    plt.show()
    rclpy.shutdown()

    # Plot the data
    
    

if __name__ == '__main__':
    main()
