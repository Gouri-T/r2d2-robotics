# R2D2 Robotics 🤖

**A ROS 2 and Gazebo-based mobile robotics simulation featuring robot description, LiDAR sensing, obstacle detection services, custom actions, teleoperation, and a foundation for SLAM and autonomous navigation.**

![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20XML-blue)


## 📑 Contents

1. [Requirements](#1-requirements)
2. [Verify Installations](#2-verify-installations)
3. [Configure ROS 2](#3-configure-ros-2)
4. [Clone the Repository](#4-clone-the-repository)
5. [Install Dependencies and Build](#5-install-dependencies-and-build)
6. [Launch Simulation](#6-launch-simulation)
7. [Keyboard Teleoperation](#7-keyboard-teleoperation)
8. [Obstacle Detection Service](#8-obstacle-detection-service)
9. [Robot Rotation Action](#9-robot-rotation-action)
10. [RViz](#10-rviz)

---

## 1. Requirements

Install the following on Ubuntu:

- ROS 2 Humble
- Gazebo Harmonic
- Git

The commands below assume ROS 2 Humble and Gazebo Harmonic are already installed.

## 2. Verify Installations

**Check the Ubuntu version:**
```bash
lsb_release -a
```

**Check the ROS 2 distribution:**
```bash
echo $ROS_DISTRO
```

Expected output:
```text
humble
```

If the output is empty, source ROS 2 first:

```bash
source /opt/ros/humble/setup.bash
echo $ROS_DISTRO
```

**Check the Gazebo version:**
```bash
gz sim --version
```

Confirm that the installed version corresponds to Gazebo Harmonic (Gazebo 8).

## 3. Configure ROS 2

Add ROS 2 to your Bash configuration so it is available in new terminals.

```bash
nano ~/.bashrc
```

Add this line at the end of the file:

```bash
source /opt/ros/humble/setup.bash
```

Save and exit Nano:
- `Ctrl + O`, then `Enter` to save.
- `Ctrl + X` to exit.

Reload the configuration:

```bash
source ~/.bashrc
```

Check the distribution:

```bash
echo $ROS_DISTRO
```

## 4. Clone the Repository

Install Git:

```bash
sudo apt update
sudo apt install git -y
```

Create the workspace and clone the repository:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/Gouri-T/r2d2-robotics.git
```

## 5. Install Dependencies and Build

Install the required tools:

```bash
sudo apt install python3-rosdep2 python3-colcon-common-extensions -y
```

Update rosdep:

```bash
sudo rosdep init
rosdep update
```

> If `sudo rosdep init` reports that rosdep is already initialized, continue to `rosdep update`.

Install package dependencies:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

Build the workspace:

```bash
colcon build
```

Source the workspace:

```bash
source install/setup.bash
```

For every new terminal, source the workspace after sourcing ROS 2:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 6. Launch Simulation

```bash
ros2 launch r2d2 spawn.launch.py
```

## 7. Keyboard Teleoperation

Open a new terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
python3 ~/ros2_ws/src/r2d2-robotics/r2d2/scripts/teleop_keyboard.py
```

Use the keyboard controls defined in the script to move the robot.

## 8. Obstacle Detection Service

**Terminal 1 — Start the service:**

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run robot_services obstacle_service
```

**Terminal 2 — Call the service:**

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 service call /check_obstacle std_srvs/srv/Trigger "{}"
```

## 9. Robot Rotation Action

**Terminal 1 — Start the action server:**

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run robot_actions rotate_server
```

**Terminal 2 — Send a rotation goal:**

Example: rotate 90 degrees at an angular speed of 0.5 rad/s.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 action send_goal /rotate_robot robot_interfaces/action/RotateRobot "{angle_degrees: 90.0, angular_speed: 0.5}"
```

Change `angle_degrees` and `angular_speed` to adjust the rotation.

## 10. RViz

If RViz is not launched automatically with the simulation:

```bash
rviz2
```


---

## 📦 Packages

| Package | Purpose |
|---|---|
| `r2d2` | Robot description, simulation, launch files, and teleoperation script |
| `robot_services` | LiDAR-based obstacle detection service |
| `robot_actions` | Robot rotation action server |
| `robot_interfaces` | Custom action interface definitions |

**Repository:** [Gouri-T/r2d2-robotics](https://github.com/Gouri-T/r2d2-robotics)
**Packages:** `r2d2`, `robot_services`, `robot_actions`, `robot_interfaces`
