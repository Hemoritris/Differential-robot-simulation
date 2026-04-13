#!/usr/bin/env python3
"""
纯导航 Launch 文件 — 使用预建地图 + RViz 导航

使用 AMCL 进行定位，map_server 提供地图。

使用方式:
  ros2 launch isaac_slam_navigation isaac_nav_only.launch.py

然后在 Rviz2 中使用 2D Nav Goal 控制机器人。
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('isaac_slam_navigation')
    nav_params = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')

    # 预建地图路径
    map_yaml = '/root/ros2_ws/maps/my_map.yaml'

    common_params = {'use_sim_time': True}

    return LaunchDescription([
        # =====================================================================
        # Map Server — 加载预建地图
        # =====================================================================
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{
                'yaml_filename': map_yaml,
                'use_sim_time': True,
            }],
            output='screen',
        ),

        # =====================================================================
        # AMCL — 粒子滤波定位
        # =====================================================================
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # =====================================================================
        # Nav2 导航堆栈
        # =====================================================================
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[nav_params, common_params],
            output='screen',
        ),
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # 生命周期管理器
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            parameters=[{
                'autostart': True,
                'use_sim_time': True,
                'node_names': [
                    'map_server',
                    'amcl',
                    'controller_server',
                    'planner_server',
                    'behavior_server',
                    'bt_navigator',
                    'velocity_smoother',
                ],
            }],
            output='screen',
        ),
    ])