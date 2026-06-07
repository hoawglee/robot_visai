#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math
import time


class NavResultRecorder(Node):
    def __init__(self):
        super().__init__('nav_result_recorder')

        self.last_time = None
        self.last_x = None
        self.last_y = None

        self.final_x = None
        self.final_y = None

        self.total_distance = 0.0
        self.moving_time = 0.0

        self.has_started = False
        self.result_printed = False

        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.get_logger().info("Dang ghi du lieu /odom...")
        self.get_logger().info("Bam Nav2 Goal cho robot chay.")
        self.get_logger().info("Khi robot bao Goal succeeded thi bam Ctrl+C.")

    def odom_callback(self, msg):
        now = time.time()

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        wz = msg.twist.twist.angular.z

        speed = math.sqrt(vx * vx + vy * vy)

        is_moving = speed > 0.02 or abs(wz) > 0.05

        if self.last_time is None:
            self.last_time = now
            self.last_x = x
            self.last_y = y
            return

        dt = now - self.last_time

        dx = x - self.last_x
        dy = y - self.last_y
        step_distance = math.sqrt(dx * dx + dy * dy)

        if is_moving:
            if not self.has_started:
                self.has_started = True
                self.get_logger().info("Robot bat dau di chuyen -> bat dau tinh.")

            self.moving_time += dt

            if step_distance > 0.001:
                self.total_distance += step_distance

            self.final_x = x
            self.final_y = y

        self.last_time = now
        self.last_x = x
        self.last_y = y

    def show_result(self):
        if self.result_printed:
            return

        self.result_printed = True

        if not self.has_started:
            print("\nRobot chua di chuyen nen khong co ket qua.\n")
            return

        avg_speed = self.total_distance / self.moving_time if self.moving_time > 0 else 0.0

        print("\n")
        print("====================================")
        print("        KET QUA THU NGHIEM")
        print("====================================")
        print(f"Thoi gian robot di chuyen: {self.moving_time:.3f} s")
        print(f"Quang duong di chuyen    : {self.total_distance:.3f} m")
        print(f"Van toc trung binh       : {avg_speed:.3f} m/s")

        if self.final_x is not None:
            print(f"Vi tri cuoi              : ({self.final_x:.3f}, {self.final_y:.3f})")

        print("====================================")
        print("\n")


def main(args=None):
    rclpy.init(args=args)
    node = NavResultRecorder()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.show_result()
        node.destroy_node()

        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()