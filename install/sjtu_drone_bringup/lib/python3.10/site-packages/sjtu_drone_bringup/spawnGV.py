#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Pose

class SpawnEntityNode(Node):
    def __init__(self):
        super().__init__('spawn_entity_node')
        self.client = self.create_client(SpawnEntity, 'spawn_entity')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = SpawnEntity.Request()

    def send_request(self):
        self.req.name = 'ground_vehicle'
        self.req.xml = open('ground_vehicle.urdf', 'r').read()
        self.req.robot_namespace = 'ground_vehicle'
        self.req.reference_frame = 'world'
        
        self.future = self.client.call_async(self.req)

def main(args=None):
    rclpy.init(args=args)
    node = SpawnEntityNode()
    node.send_request()

    while rclpy.ok():
        rclpy.spin_once(node)
        if node.future.done():
            try:
                response = node.future.result()
            except Exception as e:
                node.get_logger().info('Service call failed %r' % (e,))
            else:
                node.get_logger().info('Vehicle spawned: %s' % (response.success,))
            break

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

