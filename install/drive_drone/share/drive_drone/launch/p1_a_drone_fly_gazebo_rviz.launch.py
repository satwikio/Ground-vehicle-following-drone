#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription , ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro

def generate_launch_description():

    drone_pkg = get_package_share_directory('sjtu_drone_bringup')
    gv_pkg = get_package_share_directory('minimal_diff_drive_robot')
    #dc_pkg = get_package_share_directory('drone_controller')



    gv_bringup = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gv_pkg, 'launch', 'gazebo_and_rviz.launch.py')
            )

        )

    drone_bringup= IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(drone_pkg, 'launch', 'sjtu_drone_bringup.launch.py')
            )

        )

    takeoff_cmd= ExecuteProcess(
            cmd=['ros2', 'topic', 'pub', '/drone/takeoff', 'std_msgs/msg/Empty', '{}','--once'],
            shell=True,
            output="screen"
        )
        


    drive_drone= Node(
            package="drive_drone",
            executable="p1_a_drive_node",
            output="screen"
        )
        
#    drone_controller= Node(
 #           package=dc_pkg,
  #          executable="img_sub",
            #output="screen"
   #     )

    nodes_to_run = [
        gv_bringup,
        drone_bringup,
        takeoff_cmd,
        #drone_controller
        # drive_drone
        


    ]

    return LaunchDescription(nodes_to_run)
