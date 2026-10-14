import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ArmHello(Node):

    def __init__(self):
        super().__init__('arm_hello')

        self.publisher = self.create_publisher(
            String,
            'arm_status',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_status
        )

    def publish_status(self):
        message = String()
        message.data = 'Robot arm is ready!'

        self.publisher.publish(message)

        self.get_logger().info(
            f'Publishing: {message.data}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ArmHello()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
