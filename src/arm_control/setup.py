import os
from glob import glob
from setuptools import setup

package_name = 'arm_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mubii',
    maintainer_email='mubii@todo.todo',
    description='6-DOF pick and place arm with camera',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'arm_hello = arm_control.arm_hello:main',
            'arm_monitor = arm_control.arm_monitor:main',
            'arm_move = arm_control.arm_move:main',
            'arm_service = arm_control.arm_service:main',
            'camera_vision = arm_control.camera_vision:main',
            'fibonacci_action = arm_control.fibonacci_action:main',
            'joint_controller_gui = arm_control.joint_controller_gui:main',
            'visual_servo = arm_control.visual_servo:main',
            'red_detector = arm_control.red_detector:main',
            'pick_place = arm_control.pick_place:main',
        ],
    },
)
