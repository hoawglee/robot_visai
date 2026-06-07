#!/usr/bin/env python3

import rclpy

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


def make_pose(navigator, x, y, yaw):

    q = quaternion_from_euler(0.0, 0.0, yaw)

    pose = PoseStamped()

    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()

    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    pose.pose.orientation.x = q[0]
    pose.pose.orientation.y = q[1]
    pose.pose.orientation.z = q[2]
    pose.pose.orientation.w = q[3]

    return pose


def main():

    rclpy.init()

    navigator = BasicNavigator()

    print("Dang cho Nav2 khoi dong...")
    navigator.waitUntilNav2Active()

    print("Bat dau di theo cac diem...")

    waypoints = [

        make_pose(navigator,  0.0839,  2.7678, 0.0),  # P1
        make_pose(navigator,  2.8144,  2.7808, 0.0),  # P2
        make_pose(navigator,  7.9836,  4.8622, 0.0),  # P3
        make_pose(navigator, 14.1010,  1.0248, 0.0),  # P4
        make_pose(navigator,  5.2508,  0.4946, 0.0),  # P5
    ]

    for i, goal in enumerate(waypoints):

        print("\n========================")
        print(f"Dang di toi diem {i+1}/{len(waypoints)}")
        print("========================")

        navigator.goToPose(goal)

        while not navigator.isTaskComplete():
            rclpy.spin_once(navigator, timeout_sec=0.1)

        result = navigator.getResult()

        if result == TaskResult.SUCCEEDED:
            print(f"Da toi diem {i+1}")

        elif result == TaskResult.CANCELED:
            print("Nhiem vu bi huy!")
            break

        elif result == TaskResult.FAILED:
            print(f"Khong toi duoc diem {i+1}")
            break

    print("\nHoan thanh lo trinh!")

    rclpy.shutdown()


if __name__ == '__main__':
    main()