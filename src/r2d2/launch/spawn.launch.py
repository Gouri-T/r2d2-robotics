import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('r2d2')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    urdf_path = os.path.join(pkg_share, 'urdf', 'r2d2.urdf')
    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    # Lets Gazebo resolve package://r2d2/meshes/... URIs
    set_resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg_share))

    args = [
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_share, 'worlds', 'r2d2.sdf'),
            description='World file (must load the gz Sensors system for camera/lidar)'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Start RViz2'),
        DeclareLaunchArgument('teleop', default_value='false',
                              description='Open keyboard teleop in an xterm window '
                                          '(needs xterm; otherwise run it in your own terminal)'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        # Wheels hang ~0.47 m below base_link, so spawn a bit above that
        DeclareLaunchArgument('z', default_value='0.52'),
    ]

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ', LaunchConfiguration('world')]}.items(),
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-name', 'r2d2',
                   '-topic', 'robot_description',
                   '-x', LaunchConfiguration('x'),
                   '-y', LaunchConfiguration('y'),
                   '-z', LaunchConfiguration('z')],
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # Sensors
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            # ROS -> Gazebo drive + joint commands
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/head_swivel/cmd@std_msgs/msg/Float64]gz.msgs.Double',
            '/gripper_extension/cmd@std_msgs/msg/Float64]gz.msgs.Double',
            '/left_gripper/cmd@std_msgs/msg/Float64]gz.msgs.Double',
            '/right_gripper/cmd@std_msgs/msg/Float64]gz.msgs.Double',
        ],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'r2d2.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    teleop = Node(
        package='r2d2',
        executable='teleop_keyboard.py',
        output='screen',
        prefix='xterm -e',
        condition=IfCondition(LaunchConfiguration('teleop')),
    )

    return LaunchDescription(
        [set_resource_path, *args, gz_sim, rsp, spawn, bridge, rviz, teleop])
