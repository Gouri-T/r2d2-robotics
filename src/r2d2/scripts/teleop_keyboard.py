#!/usr/bin/env python3
"""Keyboard teleop for the r2d2: drive + head + gripper.

Publishes (10 Hz):
  /cmd_vel               geometry_msgs/Twist
  /head_swivel/cmd       std_msgs/Float64   (rad)
  /gripper_extension/cmd std_msgs/Float64   (m,   -0.38 .. 0)
  /left_gripper/cmd      std_msgs/Float64   (rad, 0 .. 0.548)
  /right_gripper/cmd     std_msgs/Float64   (rad, 0 .. 0.548)
"""
import math
import os
import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64

HELP = """
r2d2 robot teleop
--------------------
Drive (latched until another drive key or SPACE):
      q   w   e        w/s : forward / backward
      a   SPACE d      a/d : rotate left / right
          s            q/e : forward-left / forward-right arc
   z / c : decrease / increase speeds by 10%

Head:      j / l : swivel left / right
Gripper:   i / k : extend / retract pole
           u / o : fingers angle + / -
r : reset head & gripper to 0      CTRL-C : quit
"""


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class TeleopState:
    """Pure key -> state logic (no ROS), so it can be tested on its own."""

    DRIVE = {            # key: (linear dir, angular dir)  angular + = CCW (left)
        'w': (1, 0), 's': (-1, 0), 'a': (0, 1), 'd': (0, -1),
        'q': (1, 1), 'e': (1, -1), ' ': (0, 0),
    }
    EXT_LIMITS = (-0.38, 0.0)
    FINGER_LIMITS = (0.0, 0.548)

    def __init__(self, lin=0.5, ang=1.0, head_step=0.2, ext_step=0.04,
                 finger_step=0.05):
        self.lin, self.ang = lin, ang
        self.head_step, self.ext_step, self.finger_step = (
            head_step, ext_step, finger_step)
        self.dir_v = 0
        self.dir_w = 0
        self.head = 0.0
        self.ext = 0.0
        self.fingers = 0.0

    @property
    def v(self):
        return self.dir_v * self.lin

    @property
    def w(self):
        return self.dir_w * self.ang

    def handle(self, key):
        k = key.lower() if key != ' ' else key
        if k in self.DRIVE:
            self.dir_v, self.dir_w = self.DRIVE[k]
        elif k == 'z':
            self.lin *= 0.9
            self.ang *= 0.9
        elif k == 'c':
            self.lin *= 1.1
            self.ang *= 1.1
        elif k == 'j':
            self.head = clamp(self.head + self.head_step, -math.pi, math.pi)
        elif k == 'l':
            self.head = clamp(self.head - self.head_step, -math.pi, math.pi)
        elif k == 'i':
            self.ext = clamp(self.ext + self.ext_step, *self.EXT_LIMITS)
        elif k == 'k':
            self.ext = clamp(self.ext - self.ext_step, *self.EXT_LIMITS)
        elif k == 'u':
            self.fingers = clamp(self.fingers + self.finger_step,
                                 *self.FINGER_LIMITS)
        elif k == 'o':
            self.fingers = clamp(self.fingers - self.finger_step,
                                 *self.FINGER_LIMITS)
        elif k == 'r':
            self.head = self.ext = self.fingers = 0.0
        else:
            return False
        return True

    def status(self):
        return ('v=%+.2f m/s  w=%+.2f rad/s | head=%+.2f  ext=%+.2f  '
                'fingers=%.2f' % (self.v, self.w, self.head, self.ext,
                                  self.fingers))


class TeleopNode(Node):
    def __init__(self):
        super().__init__('r2d2_teleop')
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('angular_speed', 1.0)
        self.state = TeleopState(
            lin=self.get_parameter('linear_speed').value,
            ang=self.get_parameter('angular_speed').value)

        self.cmd_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        self.head_pub = self.create_publisher(Float64, 'head_swivel/cmd', 10)
        self.ext_pub = self.create_publisher(Float64, 'gripper_extension/cmd', 10)
        self.left_pub = self.create_publisher(Float64, 'left_gripper/cmd', 10)
        self.right_pub = self.create_publisher(Float64, 'right_gripper/cmd', 10)
        self.create_timer(0.1, self.publish)

    @staticmethod
    def _f(x):
        m = Float64()
        m.data = float(x)
        return m

    def publish(self):
        t = Twist()
        t.linear.x = float(self.state.v)
        t.angular.z = float(self.state.w)
        self.cmd_vel.publish(t)
        self.head_pub.publish(self._f(self.state.head))
        self.ext_pub.publish(self._f(self.state.ext))
        self.left_pub.publish(self._f(self.state.fingers))
        self.right_pub.publish(self._f(self.state.fingers))

    def stop(self):
        self.state.dir_v = self.state.dir_w = 0
        self.cmd_vel.publish(Twist())


def read_key(fd):
    ch = os.read(fd, 1).decode(errors='ignore')
    if ch == '\x1b':  # swallow arrow-key / escape sequences
        while select.select([fd], [], [], 0.01)[0]:
            os.read(fd, 1)
        return ''
    return ch


def main():
    if not sys.stdin.isatty():
        print('teleop_keyboard needs an interactive terminal (stdin is not a tty).')
        return 1

    rclpy.init()
    node = TeleopNode()
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        print(HELP)
        print(node.state.status())
        while rclpy.ok():
            if select.select([fd], [], [], 0.05)[0]:
                key = read_key(fd)
                if key == '\x03':
                    break
                if key and node.state.handle(key):
                    sys.stdout.write('\r\x1b[K' + node.state.status())
                    sys.stdout.flush()
            rclpy.spin_once(node, timeout_sec=0)
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)
        if rclpy.ok():
            node.stop()
            node.destroy_node()
            rclpy.shutdown()
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
