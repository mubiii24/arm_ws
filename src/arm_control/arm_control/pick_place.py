#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point

ARM_JOINTS = ['base_yaw_joint', 'shoulder_joint', 'elbow_joint',
              'wrist_roll_joint', 'wrist_pitch_joint', 'wrist_yaw_joint']
GRIP_JOINTS = ['left_finger_joint', 'right_finger_joint']

# arm pose = [base_yaw, shoulder, elbow, roll, pitch, yaw]  (radians)
HOME = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
HOVER = [0.0, 0.108, 1.879, 0.0, 1.156, 0.0]   # gripper pointing down, 20 cm high
GRASP = [0.0, 0.387, 2.060, 0.0, 0.695, 0.0]   # gripper pointing down, at the cube

OPEN = [0.0, 0.0]
CLOSE = [0.026, 0.026]

DROP_YAW = 1.5708     # green zone is on the left side
SCAN_MIN, SCAN_MAX = -1.5, 1.2


def with_yaw(pose, yaw):
    p = list(pose)
    p[0] = yaw
    return p


class PickPlace(Node):
    def __init__(self):
        super().__init__('pick_place')
        self.declare_parameter('centre_sign', 1.0)   # set to -1.0 if it turns the wrong way
        self.sign = self.get_parameter('centre_sign').value

        self.arm_pub = self.create_publisher(
            Float64MultiArray, '/arm_controller/commands', 10)
        self.grip_pub = self.create_publisher(
            Float64MultiArray, '/gripper_controller/commands', 10)
        self.create_subscription(Point, '/red_object', self.on_red, 10)
        self.create_subscription(JointState, '/joint_states', self.on_js, 10)

        self.js = {}
        self.arm = None
        self.grip = list(OPEN)
        self.red = None
        self.red_t = 0.0
        self.state = 'WAIT'
        self.motion = None
        self.queue = []
        self.yaw = SCAN_MIN
        self.scan_dir = 1.0
        self.centered = 0
        self.lost = 0
        self.create_timer(0.05, self.tick)   # 20 times per second
        self.get_logger().info('Waiting for the robot joint states...')

    # ---------- callbacks ----------
    def on_js(self, msg):
        for n, p in zip(msg.name, msg.position):
            self.js[n] = p

    def on_red(self, msg):
        self.red = msg
        self.red_t = time.time()

    def seen(self):
        return self.red is not None and (time.time() - self.red_t) < 0.4

    # ---------- helpers ----------
    def publish(self):
        a = Float64MultiArray()
        a.data = [float(v) for v in self.arm]
        self.arm_pub.publish(a)
        g = Float64MultiArray()
        g.data = [float(v) for v in self.grip]
        self.grip_pub.publish(g)

    def start_motion(self, arm_goal, grip_goal, secs):
        self.motion = {'a0': list(self.arm), 'a1': list(arm_goal),
                       'g0': list(self.grip), 'g1': list(grip_goal),
                       't0': time.time(), 'T': secs}

    def step_motion(self):
        m = self.motion
        f = min(1.0, (time.time() - m['t0']) / m['T'])
        s = f * f * (3 - 2 * f)   # smooth start and stop
        self.arm = [a + (b - a) * s for a, b in zip(m['a0'], m['a1'])]
        self.grip = [a + (b - a) * s for a, b in zip(m['g0'], m['g1'])]
        self.publish()
        if f >= 1.0:
            self.motion = None

    # ---------- main loop ----------
    def tick(self):
        if self.motion:
            self.step_motion()
            return

        if self.queue:
            arm_goal, grip_goal, secs, text = self.queue.pop(0)
            self.get_logger().info(text)
            self.start_motion(arm_goal, grip_goal, secs)
            return

        if self.state == 'WAIT':
            if all(n in self.js for n in ARM_JOINTS + GRIP_JOINTS):
                self.arm = [self.js[n] for n in ARM_JOINTS]
                self.grip = [self.js[n] for n in GRIP_JOINTS]
                self.get_logger().info('Moving to scan pose')
                self.start_motion(with_yaw(HOVER, self.yaw), OPEN, 5.0)
                self.state = 'SCAN'

        elif self.state == 'SCAN':
            if self.seen():
                self.get_logger().info('Red object found, centring...')
                self.state = 'CENTER'
                self.centered = 0
                self.lost = 0
                return
            self.yaw += self.scan_dir * 0.006       # about 0.12 rad/s
            if self.yaw > SCAN_MAX:
                self.scan_dir = -1.0
            if self.yaw < SCAN_MIN:
                self.scan_dir = 1.0
            self.arm[0] = self.yaw
            self.publish()

        elif self.state == 'CENTER':
            if not self.seen():
                self.lost += 1
                if self.lost > 20:
                    self.get_logger().info('Lost the object, scanning again')
                    self.state = 'SCAN'
                return
            self.lost = 0
            self.yaw -= self.sign * 0.04 * self.red.x
            self.arm[0] = self.yaw
            self.publish()
            if abs(self.red.x) < 0.05:
                self.centered += 1
            else:
                self.centered = 0
            if self.centered >= 15:
                y = self.yaw
                self.queue = [
                    (with_yaw(GRASP, y), OPEN, 3.0, 'Going down'),
                    (with_yaw(GRASP, y), CLOSE, 1.5, 'Closing gripper'),
                    (with_yaw(HOVER, y), CLOSE, 3.0, 'Lifting'),
                    (with_yaw(HOVER, DROP_YAW), CLOSE, 4.0, 'Moving to drop zone'),
                    (with_yaw(GRASP, DROP_YAW), CLOSE, 3.0, 'Lowering'),
                    (with_yaw(GRASP, DROP_YAW), OPEN, 1.5, 'Releasing'),
                    (with_yaw(HOVER, DROP_YAW), OPEN, 3.0, 'Moving up'),
                    (HOME, OPEN, 4.0, 'Going home'),
                ]
                self.state = 'RUN'

        elif self.state == 'RUN':
            self.get_logger().info('PICK AND PLACE DONE')
            self.state = 'DONE'


def main():
    rclpy.init()
    rclpy.spin(PickPlace())


if __name__ == '__main__':
    main()
