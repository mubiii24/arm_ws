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

        self.step = 0

        self.timer = self.create_timer(
            3.0,
            self.move_robot
        )

        self.get_logger().info(
            'Robot pick-and-place sequence started'
        )

    def move_robot(self):

        message = Float64MultiArray()

        if self.step == 0:

            # HOME + GRIPPER OPEN
            message.data = [
                0.0,    # shoulder
                0.0,    # elbow
                0.0,    # wrist
                0.06,   # left finger OPEN
                -0.06   # right finger OPEN
            ]

            self.get_logger().info(
                'Step 1: HOME + Gripper OPEN'
            )

        elif self.step == 1:

            # MOVE TO PICK POSITION + GRIPPER OPEN
            message.data = [
                0.5,
                0.7,
                -0.4,
                0.06,
                -0.06
            ]

            self.get_logger().info(
                'Step 2: Moving to PICK position'
            )

        elif self.step == 2:

            # CLOSE GRIPPER
            message.data = [
                0.5,
                0.7,
                -0.4,
                0.0,
                0.0
            ]

            self.get_logger().info(
                'Step 3: Closing GRIPPER'
            )

        elif self.step == 3:

            # MOVE TO PLACE POSITION WHILE GRIPPER CLOSED
            message.data = [
                -0.5,
                0.8,
                0.5,
                0.0,
                0.0
            ]

            self.get_logger().info(
                'Step 4: Moving to PLACE position'
            )

        elif self.step == 4:

            # OPEN GRIPPER
            message.data = [
                -0.5,
                0.8,
                0.5,
                0.06,
                -0.06
            ]

            self.get_logger().info(
                'Step 5: Opening GRIPPER'
            )

        elif self.step == 5:

            # RETURN HOME + GRIPPER OPEN
            message.data = [
                0.0,
                0.0,
                0.0,
                0.06,
                -0.06
            ]

            self.get_logger().info(
                'Step 6: Returning HOME'
            )

        else:

            self.get_logger().info(
                'Pick-and-place sequence complete'
            )

            self.timer.cancel()
            return

        self.publisher.publish(message)

        self.step += 1


def main(args=None):

    rclpy.init(args=args)

    node = ArmMove()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
