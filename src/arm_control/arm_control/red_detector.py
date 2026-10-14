#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point


class RedDetector(Node):
    def __init__(self):
        super().__init__('red_detector')
        self.create_subscription(
            Image, '/gripper_camera/cam/image_raw', self.cb, 10)
        # x, y = offset from image centre (-1..1); z = fraction of image that is red
        self.pub = self.create_publisher(Point, '/red_object', 10)

    def cb(self, msg):
        img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, 3)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255)) | \
            cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > 30:
                m = cv2.moments(c)
                cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
                p = Point()
                p.x = (cx - msg.width / 2) / (msg.width / 2)
                p.y = (cy - msg.height / 2) / (msg.height / 2)
                p.z = area / (msg.width * msg.height)
                self.pub.publish(p)
                cv2.circle(bgr, (int(cx), int(cy)), 8, (0, 255, 0), 2)
        cv2.imshow('gripper camera', bgr)
        cv2.waitKey(1)


def main():
    rclpy.init()
    rclpy.spin(RedDetector())


if __name__ == '__main__':
    main()
