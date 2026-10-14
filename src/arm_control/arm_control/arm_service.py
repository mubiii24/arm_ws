import rclpy
from rclpy.node import Node
from example_interfaces.srv import SetBool


class ArmService(Node):

    def __init__(self):
        super().__init__('arm_service')

        self.service = self.create_service(
            SetBool,
            'arm_ready',
            self.check_arm
        )

    def check_arm(self, request, response):

        if request.data:
            response.success = True
            response.message = 'Robot arm is ready!'
        else:
            response.success = False
            response.message = 'Robot arm is not ready.'

        return response


def main(args=None):
    rclpy.init(args=args)

    node = ArmService()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
