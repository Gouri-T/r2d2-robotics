import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from geometry_msgs.msg import Twist

from robot_interfaces.action import RotateRobot


class RotateServer(Node):

    def __init__(self):
        super().__init__('rotate_server')

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.action_server = ActionServer(
            self,
            RotateRobot,
            '/rotate_robot',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info('Rotate action server ready.')

    def goal_callback(self, goal_request):

        if goal_request.angle_degrees == 0:
            return GoalResponse.REJECT

        if not math.isfinite(goal_request.angle_degrees):
            return GoalResponse.REJECT

        if not math.isfinite(goal_request.angular_speed):
            return GoalResponse.REJECT

        if not 0.05 <= abs(goal_request.angular_speed) <= 0.5:
            return GoalResponse.REJECT

        if abs(goal_request.angle_degrees) > 360:
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Rotation cancellation requested.')
        return CancelResponse.ACCEPT

    def stop_robot(self):
        msg = Twist()
        self.cmd_pub.publish(msg)

    def execute_callback(self, goal_handle):

        requested_angle = goal_handle.request.angle_degrees
        angular_speed = abs(goal_handle.request.angular_speed)

        direction = 1.0 if requested_angle > 0 else -1.0

        target_angle = math.radians(abs(requested_angle))

        # This is a simple open-loop demonstration.
        # It assumes the robot follows the commanded angular velocity.
        estimated_duration = target_angle / angular_speed

        start_time = time.monotonic()

        feedback = RotateRobot.Feedback()
        result = RotateRobot.Result()

        try:
            while True:

                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    result.success = False
                    result.message = 'Rotation cancelled.'
                    return result

                elapsed = time.monotonic() - start_time

                progress = min(
                    100.0,
                    100.0 * elapsed / estimated_duration
                )

                if progress >= 100.0:
                    break

                cmd = Twist()
                cmd.angular.z = direction * angular_speed
                self.cmd_pub.publish(cmd)

                feedback.progress = progress
                goal_handle.publish_feedback(feedback)

                time.sleep(0.05)

            self.stop_robot()

            goal_handle.succeed()

            result.success = True
            result.message = (
                f'Rotation command completed: '
                f'{requested_angle:.1f} degrees.'
            )

            return result

        finally:
            self.stop_robot()



def main(args=None):

    rclpy.init(args=args)

    node = RotateServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
