import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Define the launch arguments for the Gazebo launch file
    gazebo_launch_args = {
        'verbose': 'false',
        'pause': 'false',
    }

   # Include the Gazebo launch file with the modified launch arguments
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
        launch_arguments=gazebo_launch_args.items(),
    )

    robot_desc_path = os.path.join(get_package_share_directory(
        "minimal_diff_drive_robot"), "urdf", "minimal_diff_drive_robot.urdf")
        
    with open(robot_desc_path, 'r') as file:
    	robot_desc = file.read()

    robot_name = "robot1"

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'use_sim_time': use_sim_time,
                     'robot_description': Command(['xacro ', robot_desc_path, ' robot_name:=', robot_name])}],
        output="screen"
    )

    robot_state_publisher1 = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        namespace=robot_name,
        output="screen",
        parameters=[{"use_sim_time": use_sim_time, "robot_description": robot_desc}],
        arguments=[robot_desc]
    )


    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'robot1', '-x', '0.0', '-y', '0.0', '-z', '0.0',
                   '-topic', 'robot1/robot_description']
    )
    

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(
        'minimal_diff_drive_robot'), 'config', 'robot.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir])

    return LaunchDescription([
        gazebo,
       	robot_state_publisher1,
        spawn_robot,
        rviz_node,
        Node(
            package="teleop_twist_keyboard",
            executable="teleop_twist_keyboard",
            namespace="/robot1",
            output="screen",
            prefix="xterm -e"
        )
    ])
