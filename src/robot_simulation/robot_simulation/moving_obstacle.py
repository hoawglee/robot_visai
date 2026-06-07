import math

import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState


class MovingObstacle(Node):
    def __init__(self):
        super().__init__('moving_obstacle')

        self.client = self.create_client(SetEntityState, '/set_entity_state')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /set_entity_state service...')

        self.t = 0.0
        self.timer = self.create_timer(0.05, self.update_obstacles)

    def set_model_pose(self, name, x, y, z):
        state = EntityState()
        state.name = name
        state.reference_frame = 'world'

        state.pose.position.x = x
        state.pose.position.y = y
        state.pose.position.z = z

        state.pose.orientation.w = 1.0

        req = SetEntityState.Request()
        req.state = state
        self.client.call_async(req)

    def update_obstacles(self):
        self.t += 0.05

        # moving_box_1: chạy dọc
        x1 = 0.2181692123413086
        y1 = 2.8494062423706055 + 0.8 * math.sin(self.t)

        # moving_box_2: chạy ngang
        x2 = 4.66617488861084 + 0.8 * math.sin(self.t)
        y2 = 2.5308852195739746

        # moving_box_3: chạy dọc
        x3 = -1.6642284393310547
        y3 = -2.076890707015991 + 0.8 * math.sin(self.t)

        self.set_model_pose('moving_box_1', x1, y1, 0.4)
        self.set_model_pose('moving_box_2', x2, y2, 0.4)
        self.set_model_pose('moving_box_3', x3, y3, 0.4)


def main(args=None):
    rclpy.init(args=args)
    node = MovingObstacle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()