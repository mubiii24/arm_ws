import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')

        # ROS 2 parameter
        self.declare_parameter('arm_speed', 0.5)

        self.action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):

        self.get_logger().info(
            f'Received goal: {goal_handle.request.order}'
        )

        sequence = [0, 1]

        for i in range(1, goal_handle.request.order):

            sequence.append(
                sequence[-1] + sequence[-2]
            )

            feedback = Fibonacci.Feedback()

            feedback.sequence = sequence

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Feedback: {sequence}'
            )

            time.sleep(1)

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.sequence = sequence

        return result


def main(args=None):

    rclpy.init(args=args)

    node = FibonacciActionServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
