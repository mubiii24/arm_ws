arm control

One ROS 2 Python package, arm_control, with everything needed to simulate and drive the arm:

Part	Details
🦾 Robot	6 revolute joints (base yaw, shoulder, elbow, wrist roll, wrist pitch, wrist yaw) and a 2-finger gripper. Described in urdf/simple_arm.urdf.
📷 Camera	A 320x240 camera on the gripper, published at /gripper_camera/cam/image_raw.
🌍 World	A Gazebo world with a red T-shaped block and a green drop zone (worlds/pick_place.world).
🎛️ Control	Position controllers for the arm and the gripper, set up in config/controllers.yaml.
🧠 Software	Python nodes for moving the arm, red-object detection and an automatic pick and place.
🎬 Demo
<!-- Add your own screenshot or GIF of Gazebo here, for example: <p align="center"><img src="docs/demo.gif" width="80%"></p> -->

When you run the pick and place, the arm:

🔭 Moves to a scanning pose and sweeps left and right.
🔴 Spots the red block in the camera image and turns to centre it.
⬇️ Goes down and closes the gripper on the block.
🟩 Lifts it, swings to the green zone and sets it down.
🏠 Opens the gripper and returns home.
🏗️ How it fits together
/red_object(Point)
/arm_controller/commands/gripper_controller/commands
Gazeboarm + red block + greenzone
Gripper camera/gripper_camera/cam/image_raw
red_detector(OpenCV)
pick_placestate machine
arm_controller +gripper_controller
🧰 Requirements
Ubuntu 22.04 with ROS 2 Humble
Gazebo Classic, ros2_control, OpenCV and Tk:
bash
sudo apt install \
  ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-robot-state-publisher ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2 ros-humble-cv-bridge python3-opencv python3-tk
🔨 Build

Clone it into your home folder as ~/arm_ws (some files expect that location, see Known issues):

bash
cd ~
git clone https://github.com/mubiii24/arm_ws.git
cd arm_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
🚀 Usage
1. Start the simulation
bash
ros2 launch arm_control gazebo.launch.py

Gazebo opens with the arm, the red block and the green zone. The launch file starts Gazebo, waits 10 seconds, spawns the arm, then loads the joint state broadcaster, the arm controller and the gripper controller. Give it a moment before sending commands.

2. Run the pick and place

Open two more terminals (run source ~/arm_ws/install/setup.bash in each):

bash
# Terminal 2: finds the red block in the camera image
ros2 run arm_control red_detector

# Terminal 3: runs the pick and place
ros2 run arm_control pick_place

If the arm turns away from the block instead of towards it, flip the direction:

bash
ros2 run arm_control pick_place --ros-args -p centre_sign:=-1.0
3. Or move the arm yourself
bash
ros2 run arm_control joint_controller_gui

This opens a window with a slider for every joint and both fingers.

4. Just look at the model
bash
ros2 launch arm_control display.launch.py

Opens RViz with sliders (joint_state_publisher_gui) so you can inspect the arm without Gazebo.

🧩 Nodes
Command	What it does
ros2 run arm_control pick_place	⭐ Automatic pick and place: scan, centre on the red block, grasp, carry, release, go home.
ros2 run arm_control red_detector	Finds red pixels in the gripper camera image and publishes where the block is on /red_object. Shows a window with the detection.
ros2 run arm_control joint_controller_gui	Slider window for every joint and both fingers.
ros2 run arm_control arm_move	Plays a fixed sequence of arm poses.
ros2 run arm_control camera_vision	Older vision node. Reads /arm_camera/image_raw and publishes the block's pixel position on /red_object/position.
ros2 run arm_control visual_servo	Older node that steers the arm from /red_object/position.
ros2 run arm_control arm_hello	Learning example: publishes a status message on arm_status.
ros2 run arm_control arm_monitor	Learning example: prints the messages from arm_status.
ros2 run arm_control arm_service	Learning example: a SetBool service called arm_ready.
ros2 run arm_control fibonacci_action	Learning example: a Fibonacci action server.
📡 Topics
Topic	Type	Used for
/arm_controller/commands	Float64MultiArray	Joint positions for the 6 arm joints (radians).
/gripper_controller/commands	Float64MultiArray	Finger positions: 0.0 is open, about 0.026 closes on the block.
/joint_states	JointState	Current joint positions.
/gripper_camera/cam/image_raw	Image	Gripper camera image.
/red_object	Point	Block position: x and y are the offset from the image centre (-1 to 1), z is how much of the image is red.
📁 Project structure
arm_ws/
├── docs/
│   └── banner.svg
└── src/
    └── arm_control/
        ├── arm_control/        # Python nodes
        │   ├── pick_place.py
        │   ├── red_detector.py
        │   ├── joint_controller_gui.py
        │   ├── arm_move.py
        │   ├── camera_vision.py
        │   ├── visual_servo.py
        │   └── ...
        ├── config/controllers.yaml
        ├── launch/             # gazebo.launch.py, display.launch.py
        ├── urdf/simple_arm.urdf
        └── worlds/pick_place.world
🛠️ Known issues
Path to controllers.yaml: urdf/simple_arm.urdf points to /home/mubii/arm_ws/install/arm_control/share/arm_control/config/controllers.yaml. If your username is not mubii, replace /home/mubii in that line with your own home folder, then rebuild.
display.launch.py loads the URDF from ~/arm_ws/src/arm_control/urdf/simple_arm.urdf, so the workspace needs to live at ~/arm_ws.
Dependencies: package.xml does not list them yet, so rosdep will not install them. Use the apt command above.
📄 License

setup.py declares the MIT license. See the LICENSE file for details.

👤 Author

Made by mubii (@mubiii24).
