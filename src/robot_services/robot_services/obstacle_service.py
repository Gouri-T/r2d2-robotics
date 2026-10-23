import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Trigger


class ObstacleService(Node):

    def __init__(self):
        super().__init__('obstacle_service')

        self.latest_scan = None

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.service = self.create_service(
            Trigger,
            '/check_obstacle',
            self.check_obstacle_callback
        )

        self.get_logger().info(
            'Obstacle service ready. Waiting for LiDAR data...'
        )

    def scan_callback(self, msg):
        self.latest_scan = msg

    def check_obstacle_callback(self, request, response):

        if self.latest_scan is None:
            response.success = False
            response.message = 'No LiDAR data received yet.'
            return response

        scan = self.latest_scan

        # Consider readings within approximately +/- 15 degrees
        # of the centre of the scan.
        valid_ranges = []

        for i, distance in enumerate(scan.ranges):

            angle = scan.angle_min + i * scan.angle_increment

            if abs(angle) <= math.radians(15):

                if (
                    math.isfinite(distance)
                    and scan.range_min <= distance <= scan.range_max
                ):
                    valid_ranges.append(distance)

        if not valid_ranges:
            response.success = False
            response.message = 'No valid LiDAR readings in the forward sector.'
            return response

        min_distance = min(valid_ranges)

        if min_distance < 1.0:
            response.success = True
            response.message = (
                f'Obstacle detected! Nearest distance: '
                f'{min_distance:.2f} m'
            )
        else:
            response.success = True
            response.message = (
                f'No obstacle within 1 metre. '
                f'Nearest distance: {min_distance:.2f} m'
            )

        return response


def main(args=None):
    rclpy.init(args=args)

    node = ObstacleService()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
