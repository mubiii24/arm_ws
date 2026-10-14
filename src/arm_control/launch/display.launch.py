import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    urdf_file = os.path.join(
        os.path.expanduser('~'),
        'arm_ws',
        'src',
        'arm_control',
        'urdf',
        'simple_arm.urdf'
    )

    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'robot_description': robot_description}
            ]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'
        ),

        Node(
            package='rviz2',
            executable='rviz2'
        )
    ])
