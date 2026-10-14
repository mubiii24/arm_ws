import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Float64MultiArray


class VisualServo(Node):

    def __init__(self):
        super().__init__('visual_servo')

        self.position_subscription = self.create_subscription(
            Int32MultiArray,
            '/red_object/position',
            self.position_callback,
            10
        )

        self.command_publisher = self.create_publisher(
            Float64MultiArray,
            '/arm_controller/commands',
            10
        )

        self.current_shoulder = 0.0

        self.get_logger().info(
            'Visual servo node started'
        )

    def position_callback(self, msg):

        if len(msg.data) < 2:
            return

        x = msg.data[0]
        y = msg.data[1]

        image_center_x = 320

        error = x - image_center_x

        message = Float64MultiArray()

        if error < -30:

            self.current_shoulder += 0.02

            self.get_logger().info(
                f'Object LEFT: x={x}, '
                f'moving shoulder right'
            )

        elif error > 30:

            self.current_shoulder -= 0.02

            self.get_logger().info(
                f'Object RIGHT: x={x}, '
                f'moving shoulder left'
            )

        else:

            self.get_logger().info(
                f'Object CENTERED: x={x}'
            )

        self.current_shoulder = max(
            -1.57,
            min(1.57, self.current_shoulder)
        )

        message.data = [
            self.current_shoulder,
            0.6,
            -0.6,
            0.0,
            0.0
        ]

        self.command_publisher.publish(message)


def main(args=None):

    rclpy.init(args=args)

    node = VisualServo()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
