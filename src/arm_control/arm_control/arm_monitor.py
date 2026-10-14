import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ArmMonitor(Node):

    def __init__(self):
        super().__init__('arm_monitor')

        self.subscription = self.create_subscription(
            String,
            'arm_status',
            self.status_callback,
            10
        )

    def status_callback(self, message):
        self.get_logger().info(
            f'Received: {message.data}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ArmMonitor()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
