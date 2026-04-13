#!/usr/bin/env python3
"""
主 Launch 文件 — 自主探索建图 + 导航

使用方式:
  Phase 1 (建图):
    ros2 launch isaac_slam_navigation isaac_nav.launch.py
    → explore_lite 自动进行前沿探索建图
    → 探索完成或手动切换到导航模式

  Phase 2 (导航):
    ros2 topic pub /explore_node/resume std_msgs/Bool "data: false"
    → explore_lite 停止发布 cmd_vel，Nav2 接管
    → 在 Rviz2 中使用 2D Nav Goal 控制机器人

地图保存（任意时刻均可）:
  ros2 run nav2_map_server map_saver_cli -f /tmp/my_map
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 获取 isaac_slam_navigation 包安装路径，用于定位配置文件
    pkg_dir = get_package_share_directory('isaac_slam_navigation')
    explore_lite_pkg_dir = get_package_share_directory('explore_lite')
    nav_params = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
    explore_lite_params = os.path.join(explore_lite_pkg_dir, 'config', 'params.yaml')

    # 所有节点共享参数：使用仿真时间（Isaac Sim 场景）
    common_params = {'use_sim_time': True}

    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true', description='Use simulation/Gazebo clock'
    )

    return LaunchDescription([
        # =====================================================================
        # Launch 参数声明
        # =====================================================================
        declare_use_sim_time,

        # =====================================================================
        # SLAM Toolbox — 实时建图
        # =====================================================================
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            parameters=[{
                'use_sim_time': True,
                'scan_topic': '/scan',         # 激光雷达话题
                'scan_frame': 'Lidar',          # 激光雷达坐标系
                'base_frame': 'base_link',      # 机器人本体坐标系
                'odom_frame': 'odom',            # 里程计参考坐标系
                'map_frame': 'map',              # 地图坐标系
                'map_update_interval': 0.5,     # 地图更新间隔 (s)
                'map_builder_window_size': 10,
                'minimum_travel_distance': 0.08,  # 触发建图更新的最小移动距离 (m)
                'minimum_travel_heading': 0.05,  # 触发建图更新的最小旋转角度 (rad)
                'max_laser_range': 30.0,         # 激光雷达最大射程 (m)
                'enable_debug': False,
                'visualize': True,                # 在 rviz 中可视化
                # 保存 posegraph 文件（用于后续定位模式）
                'pose_graph_file_name': '/root/ros2_ws/maps/my_map',
            }],
            output='screen',
        ),

        # =====================================================================
        # Nav2 导航堆栈 — 所有节点同时启动
        # =====================================================================

        # 控制器服务器：执行路径跟踪控制器
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # 规划服务器：计算全局路径
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # 行为服务器：恢复动作（旋转、后退等）
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # BT导航器：执行行为树决策
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # 速度平滑器：平滑路径速度指令
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            parameters=[nav_params, common_params],
            output='screen',
        ),

        # 生命周期管理器：统一管理以上所有节点的生命周期状态
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            parameters=[{
                'autostart': True,
                'use_sim_time': True,
                'node_names': [
                    'controller_server',
                    'planner_server',
                    'behavior_server',
                    'bt_navigator',
                    'velocity_smoother',
                ],
                'timeout': 30000,
            }],
            output='screen',
        ),

        # =====================================================================
        # Explore Lite — 自主探索建图
        # =====================================================================
        Node(
            package='explore_lite',
            executable='explore',
            name='explore_node',
            parameters=[explore_lite_params, {'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])
