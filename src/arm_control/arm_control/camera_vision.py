import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray

from cv_bridge import CvBridge

import cv2
import numpy as np


class CameraVision(Node):

    def __init__(self):
        super().__init__('camera_vision')

        self.bridge = CvBridge()

        self.image_subscription = self.create_subscription(
            Image,
            '/arm_camera/image_raw',
            self.image_callback,
            10
        )

        self.position_publisher = self.create_publisher(
            Int32MultiArray,
            '/red_object/position',
            10
        )

        self.get_logger().info(
            'Camera vision node started'
        )

    def image_callback(self, msg):

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            hsv = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2HSV
            )

            lower_red_1 = np.array([0, 100, 100])
            upper_red_1 = np.array([10, 255, 255])

            lower_red_2 = np.array([170, 100, 100])
            upper_red_2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(
                hsv,
                lower_red_1,
                upper_red_1
            )

            mask2 = cv2.inRange(
                hsv,
                lower_red_2,
                upper_red_2
            )

            mask = mask1 + mask2

            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            if contours:

                largest_contour = max(
                    contours,
                    key=cv2.contourArea
                )

                area = cv2.contourArea(
                    largest_contour
                )

                if area > 100:

                    x, y, w, h = cv2.boundingRect(
                        largest_contour
                    )

                    center_x = x + w // 2
                    center_y = y + h // 2

                    position = Int32MultiArray()
                    position.data = [
                        center_x,
                        center_y
                    ]

                    self.position_publisher.publish(
                        position
                    )

                    self.get_logger().info(
                        f'Red object: '
                        f'x={center_x}, y={center_y}'
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2
                    )

                    cv2.circle(
                        frame,
                        (center_x, center_y),
                        5,
                        (255, 0, 0),
                        -1
                    )

                    cv2.putText(
                        frame,
                        f'Object: ({center_x}, {center_y})',
                        (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

            cv2.imshow(
                'Robot Camera - Red Detection',
                frame
            )

            cv2.waitKey(1)

        except Exception as e:

            self.get_logger().error(
                f'Camera error: {e}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = CameraVision()

    rclpy.spin(node)

    node.destroy_node()

    cv2.destroyAllWindows()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
