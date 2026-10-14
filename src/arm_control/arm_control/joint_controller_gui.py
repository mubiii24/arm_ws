#!/usr/bin/env python3
import threading
import tkinter as tk

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState

# name, min, max, step
JOINTS = [
    ('base_yaw_joint',     -3.14, 3.14, 0.01),
    ('shoulder_joint',     -2.0,  2.0,  0.01),
    ('elbow_joint',        -2.4,  2.4,  0.01),
    ('wrist_roll_joint',   -3.14, 3.14, 0.01),
    ('wrist_pitch_joint',  -1.9,  1.9,  0.01),
    ('wrist_yaw_joint',    -1.9,  1.9,  0.01),
    ('left_finger_joint',   0.0, 0.04, 0.001),
    ('right_finger_joint',  0.0, 0.04, 0.001),
]


class GuiNode(Node):
    def __init__(self):
        super().__init__('joint_controller_gui')
        self.pub_arm = self.create_publisher(
            Float64MultiArray, '/arm_controller/commands', 10)
        self.pub_grip = self.create_publisher(
            Float64MultiArray, '/gripper_controller/commands', 10)
        self.positions = {}
        self.create_subscription(JointState, '/joint_states', self.on_state, 10)

    def on_state(self, msg):
        for n, p in zip(msg.name, msg.position):
            self.positions[n] = p


def main():
    rclpy.init()
    node = GuiNode()
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()

    root = tk.Tk()
    root.title('Arm Joint Controller')
    sliders = []
    state = {'synced': False}

    def send(_=None):
        v = [float(s.get()) for s in sliders]
        a = Float64MultiArray()
        a.data = v[:6]
        node.pub_arm.publish(a)
        g = Float64MultiArray()
        g.data = v[6:]
        node.pub_grip.publish(g)

    for name, lo, hi, step in JOINTS:
        tk.Label(root, text=name).pack(anchor='w', padx=10, pady=(6, 0))
        s = tk.Scale(root, from_=lo, to=hi, resolution=step,
                     orient='horizontal', length=400, command=send)
        s.pack(padx=10)
        sliders.append(s)

    def home():
        for s in sliders:
            s.set(0.0)

    def open_gripper():
        sliders[6].set(0.0)
        sliders[7].set(0.0)

    def close_gripper():
        sliders[6].set(0.026)
        sliders[7].set(0.026)

    def print_pose():
        vals = [round(float(s.get()), 3) for s in sliders]
        print('POSE:', vals, flush=True)

    bar = tk.Frame(root)
    bar.pack(pady=10)
    tk.Button(bar, text='Home', command=home).pack(side='left', padx=4)
    tk.Button(bar, text='Open gripper', command=open_gripper).pack(side='left', padx=4)
    tk.Button(bar, text='Close gripper', command=close_gripper).pack(side='left', padx=4)
    tk.Button(bar, text='Print pose', command=print_pose).pack(side='left', padx=4)

    def sync_from_robot():
        # copy real joint positions into the sliders once, so nothing jumps
        if not state['synced'] and all(j[0] in node.positions for j in JOINTS):
            for s, j in zip(sliders, JOINTS):
                s.set(node.positions[j[0]])
            state['synced'] = True
        if not state['synced']:
            root.after(200, sync_from_robot)

    root.after(200, sync_from_robot)
    root.mainloop()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
