#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


class PathPublisher(Node):

    def __init__(self):
        super().__init__('path_publisher')

        self.publisher = self.create_publisher(Path, '/reference_path', 10)

        self.timer = self.create_timer(1.0, self.publish_path)

        self.points = [
            (0.0839,  2.7678, 0.0),
            (2.8144,  2.7808, 0.0),
            (7.9836,  4.8622, 0.0),
            (14.1010, 1.0248, 0.0),
            (5.2508,  0.4946, 0.0),
        ]

    def make_pose(self, x, y, yaw):
        q = quaternion_from_euler(0.0, 0.0, yaw)

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]

        return pose

    def publish_path(self):
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()

        for x, y, yaw in self.points:
            path.poses.append(self.make_pose(x, y, yaw))

        self.publisher.publish(path)
        self.get_logger().info('Published reference path')


def main():
    rclpy.init()
    node = PathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()