# r2d2 — ROS 2 Humble + Gazebo Harmonic

## Prerequisites
Humble's default `ros-humble-ros-gz` targets Gazebo Fortress. For Harmonic install the OSRF-built packages:

    sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
    sudo apt update
    sudo apt install ros-humble-ros-gzharmonic

(Don't run `rosdep install` for this package; it would pull the Fortress `ros_gz` build.)

## Build & run
    mkdir -p ~/ws/src && cp -r r2d2 ~/ws/src/
    cd ~/ws && source /opt/ros/humble/setup.bash
    colcon build --packages-select r2d2
    source install/setup.bash
    ros2 launch r2d2 spawn.launch.py

Launch args: `rviz:=true world:=<path to .sdf> x:=0.0 y:=0.0 z:=0.52`

The default world (`worlds/r2d2_world.sdf`) loads Gazebo's Sensors system (needed by the
camera and lidar) and has a few 2 m-tall obstacles for the lidar to hit. If you pass your own
world, it must include `gz-sim-sensors-system`. If ogre2 rendering fails (VM / no GPU), change
`<render_engine>` in the world file to `ogre`.

## Sensors (all bridged to ROS 2)
| Topic | Type | Frame |
|---|---|---|
| `/scan` | sensor_msgs/LaserScan (360°, 720 samples, 0.12-15 m, 10 Hz) | `lidar_link` (on a mast above the head) |
| `/camera/image_raw` | sensor_msgs/Image (640x480, 30 Hz) | `camera_link` (on the head "eye" box, turns with `head_swivel`) |
| `/camera/camera_info` | sensor_msgs/CameraInfo | `camera_link` |
| `/odom`, `/tf` | Odometry, `odom` -> `base_link` | |

The robot's front is +y of `base_link` (the gripper side); both sensors face that way.

RViz opens with RobotModel, TF, LaserScan and Camera displays; fixed frame is `odom`.

## Teleop
In a second terminal (workspace sourced):

    ros2 run r2d2 teleop_keyboard.py

| Key | Action |
|---|---|
| w / s | forward / backward (latched) |
| a / d | rotate left / right |
| q / e | forward-left / forward-right arc |
| SPACE | stop |
| z / c | speeds -10% / +10% (start: 0.5 m/s, 1.0 rad/s) |
| j / l | head swivel left / right |
| i / k | gripper pole extend / retract |
| u / o | finger angle + / - (0 .. 0.548 rad) |
| r | reset head and gripper to 0 |

Or `ros2 launch r2d2 spawn.launch.py teleop:=true` to open it in an xterm window.
Any other tool that publishes `geometry_msgs/Twist` on `/cmd_vel` also works, e.g.
`ros2 run teleop_twist_keyboard teleop_twist_keyboard` or `teleop_twist_joy`.

Driving uses Gazebo's DiffDrive plugin on the four wheels (track 0.44 m, wheel radius 0.035 m).
The wheel joint axes in the URDF were flipped (`0 0 -1`) so positive `linear.x` drives toward the
robot's front (+y). It is a skid-steer layout, so in-place turns scrub the wheels; if turning is
sluggish, raise the angular speed with `c`, or lower wheel friction.

## Control the joints
    ros2 topic pub --once /head_swivel/cmd       std_msgs/msg/Float64 "{data: 1.0}"
    ros2 topic pub --once /gripper_extension/cmd std_msgs/msg/Float64 "{data: -0.2}"   # -0.38 .. 0 m
    ros2 topic pub --once /left_gripper/cmd      std_msgs/msg/Float64 "{data: 0.4}"    # 0 .. 0.548 rad
    ros2 topic pub --once /right_gripper/cmd     std_msgs/msg/Float64 "{data: 0.4}"
    ros2 topic echo /joint_states

## Drive with the keyboard
    sudo apt install ros-humble-teleop-twist-keyboard
    ros2 run teleop_twist_keyboard teleop_twist_keyboard

`/cmd_vel` is bridged to a Gazebo skid-steer DiffDrive plugin on the four wheels. "Forward"
(`i`) is the robot's +y (gripper/camera side). Accelerations are limited (1 m/s², 2 rad/s²)
because the robot is tall with a short wheelbase and tips over under hard acceleration.
Keep teleop speeds modest (press `z` a few times to lower them); the default 0.5 m/s is fine.
In-place turning is a skid-steer scrub, so wheel friction is set to 0.4.
