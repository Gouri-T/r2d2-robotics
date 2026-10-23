# R2D2 Robotics 🤖

**A ROS 2 and Gazebo-based mobile robotics simulation featuring robot description, LiDAR sensing, obstacle detection services, custom actions, teleoperation, and a foundation for SLAM and autonomous navigation.**

![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20XML-blue)

## Contents
- [Setup](#setup)
- [Launch Simulation](#launch-simulation)
- [Keyboard Teleoperation](#keyboard-teleoperation)
- [Obstacle Detection Service](#obstacle-detection-service)
- [Robot Rotation Action](#robot-rotation-action)
- [RViz](#rviz)
- [Save a Map](#save-a-map)

## Setup

**Requirements:** Ubuntu, ROS 2 Humble, Gazebo Harmonic.

```bash
cd ~/r2d2-robotics
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Run `source install/setup.bash` in every new terminal before using the project.

## Launch Simulation

```bash
ros2 launch r2d2 spawn.launch.py
```

Launches the robot simulation and associated ROS 2 nodes.

## Keyboard Teleoperation

```bash
python3 ~/r2d2-robotics/src/r2d2/scripts/teleop_keyboard.py
```

Use the keyboard controls defined in the teleoperation script to move the robot.

## Obstacle Detection Service

**Terminal 1 — Start the service**
```bash
ros2 run robot_services obstacle_service
```

**Terminal 2 — Request obstacle detection**
```bash
ros2 service call /check_obstacle std_srvs/srv/Trigger "{}"
```

Returns whether an obstacle was detected in the configured LiDAR scan region.

## Robot Rotation Action

**Terminal 1 — Start the action server**
```bash
ros2 run robot_actions rotate_server
```

**Terminal 2 — Rotate the robot**

Example: rotate 90° at an angular speed of 0.5 rad/s.

```bash
ros2 action send_goal /rotate_robot robot_interfaces/action/RotateRobot "{angle_degrees: 90.0, angular_speed: 0.5}"
```

Change `angle_degrees` and `angular_speed` to adjust the rotation.

## RViz

Open RViz separately if it is not already launched:

```bash
rviz2
```

## Save a Map

With the mapping node running and the environment mapped:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/r2d2-robotics/map
```

This saves the map as `map.yaml` and `map.pgm` in the workspace root.

---
**Workspace:** `~/r2d2-robotics`  
**Packages:** `r2d2`, `robot_services`, `robot_actions`, `robot_interfaces`