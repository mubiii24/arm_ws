import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class ArmMove(Node):

    def __init__(self):
        super().__init__('arm_move')

        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/arm_controller/commands',
            10
        )

        # Give Gazebo/controller time to start
        self.timer = self.create_timer(2.0, self.move_arm)

        self.sent = False

    def move_arm(self):

        if self.sent:
            return

        message = Float64MultiArray()

        # [shoulder, elbow, wrist] in radians
        message.data = [0.3, 0.5, -0.3]

        self.publisher.publish(message)

        self.get_logger().info(
            'Moving arm to: shoulder=0.3, elbow=0.5, wrist=-0.3'
        )

        self.sent = True


def main(args=None):

    rclpy.init(args=args)

    node = ArmMove()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
