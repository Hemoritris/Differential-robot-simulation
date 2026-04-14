# Two-Wheel Differential Robot SLAM Simulation Based on ROS2 + IsaacSim

基于 ROS 2 + Isaac Sim 的两轮差速机器人（turtlebot3）自主探索建图与导航项目。

## 机器人模型

本项目使用 **TurtleBot3 Burger** 作为仿真机器人模型：

| 参数 | 规格 |
|------|------|
| 尺寸 | 138 × 178 × 158 mm |
| 重量 | 约 1 kg |
| 轮半径 | 0.033 m (66 mm 直径) |
| 轮距 | 0.16 m (两轮中心距) |
| 最大线速度 | 0.22 m/s |
| 驱动方式 | 两轮差速驱动 (Differential Drive) |
| 传感器 | 360° 激光雷达、IMU |
| 控制 | ROS 2 (Humble) |

TurtleBot3 Burger 是 ROBOTIS 推出的开源教育机器人平台，采用两轮差速驱动结构，适合 SLAM、导航和 ROS 2 学习研究。

## 功能概览

- **实时 SLAM 建图**：使用 `slam_toolbox` 进行激光雷达二维建图，支持姿态图优化和地图保存
- **自主探索**：基于 `explore_lite` 前沿探索算法，实现无需人工干预的自主地图构建
- **自主导航**：基于 Nav2 导航栈，实现已知地图定位与路径规划导航
- **两种运行模式**：
  - 建图 + 探索模式：边探索边建图，实时构建未知环境地图
  - 纯导航模式：使用预构建地图（`my_map`），通过 AMCL 实现定位与导航

## 主要算法与模块

| 组件 | 算法/模块 | 说明 |
|------|-----------|------|
| SLAM | `slam_toolbox` (async) | 实时 2D 激光建图，支持姿态图优化 |
| 定位 | AMCL | 自适应蒙特卡洛定位，粒子滤波 |
| 全局规划 | Navfn (GridBased) | 基于 Dijkstra/A* 的栅格地图路径规划 |
| 路径跟踪 | Regulated Pure Pursuit | 正则化纯追踪控制器，带速度约束 |
| 速度平滑 | `nav2_velocity_smoother` | 平滑速度指令，防止运动抖动 |
| 自主探索 | `explore_lite` | 前沿边界探索算法 |
| 行为树导航 | `nav2_bt_navigator` | 基于行为树的导航决策与恢复策略 |

## 目录结构

```
Differential-robot-simulation/
├── maps/                              # 预构建地图
│   ├── my_map.yaml                    # 地图元数据
│   ├── my_map.pgm                     # 地图图像
│   ├── my_map.data                    # 地图数据
│   └── my_map.posegraph               # 姿态图文件
├── USD/                               # Isaac Sim 仿真场景资产
│   └── turtlebot3.usd                 # USD文件
├── vidoes/                             # 演示视频
│   ├── Demo1.mp4                       # 建图+探索模式演示
│   └── Demo2.mp4                       # 纯导航模式演示
└── src/
    ├── isaac_slam_navigation/         # 本项目 ROS2 包 
    │   ├── config/nav2_params.yaml    # Nav2 导航参数配置
    │   └── launch/
    │       ├── isaac_nav.launch.py    # 建图+导航启动文件
    │       └── isaac_nav_only.launch.py # 纯导航启动文件
    └── m-explore-ros2/                # explore_lite 依赖包
```

## 运行环境

- **ROS 2** (测试版本：Humble / Foxy)
- **Isaac Sim** (需安装并配置 GPU 驱动)
- **依赖包**：
  - `slam_toolbox`
  - `nav2_bringup` / `nav2_controller` / `nav2_planner` / `nav2_behaviors` / `nav2_bt_navigator`
  - `nav2_amcl` / `nav2_map_server` / `nav2_velocity_smoother` / `nav2_lifecycle_manager`
  - `explore_lite` (子模块：`m-explore-ros2`)

## 部署步骤

### 1. 安装依赖

```bash
source /opt/ros/humble/setup.bash

# 安装 Nav2 相关包
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-slam-toolbox ros-humble-explore-lite

# 克隆并构建本仓库
cd ~/workspace
mkdir -p src && cd src

# 克隆
git clone https://github.com/Hemoritris/Differential-robot-simulation.git

# 克隆 explore_lite 依赖
git clone https://github.com/robo-friends/m-explore-ros2.git

cd ..
colcon build --packages-select isaac_slam_navigation explore_lite
source install/setup.bash
```

### 2. 配置 Isaac Sim

确保 Isaac Sim 已安装并配置好 GPU 环境变量。参考 [Isaac Sim 官方文档](https://docs.omniverse.nvidia.com/isaacsim/) 配置机器人模型和传感器参数。本仓库给出的 USD 资产中，包含：物流仓库场景、turtlebot3 机器人、各传感器 Visual Graph（Imu_Sensor、Lidar、odom、tf），Isaac Sim 负责发布以下话题数据，并订阅 `/cmd_vel` 控制机器人运动：

| 类型 | 话题 | 消息类型 | 说明 |
|------|------|----------|------|
| **发布** | `/scan` | `sensor_msgs/LaserScan` | 激光雷达扫描数据 |
| **发布** | `/odom` | `nav_msgs/Odometry` | 里程计数据|
| **发布** | `/imu` | `sensor_msgs/Imu` | IMU 惯性测量数据 |
| **发布** | `/tf` | `tf2_msgs/TFMessage` | 坐标变换树 |
| **订阅** | `/cmd_vel` | `geometry_msgs/Twist` | 速度控制指令 |



### 3. 启动

**建图 + 探索模式**（用于未知环境）：


```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch isaac_slam_navigation isaac_nav.launch.py
```

> **Rviz2 可视化**：启动后添加以下显示项
> - `Map` → 话题选择 `/map`（实时建图结果）
> - `LaserScan` → 话题 `/scan`（激光雷达数据）
> - `RobotModel`（机器人模型）
> - `Path` 显示已经规划的路径
> - `TF`（坐标变换：map → odom → base_link）

暂停探索（不停止建图）：

```bash
ros2 topic pub /explore_node/resume std_msgs/Bool "data: false"
```

**纯导航模式**（使用预构建地图）：


```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch isaac_slam_navigation isaac_nav_only.launch.py
```

> **Rviz2 可视化**：启动后添加以下显示项
> - `Map` → 话题 `/map`（预构建地图）
> - `LaserScan` → 话题 `/scan`（激光雷达实时数据）
> - `RobotModel`（机器人模型）
> - `TF`（坐标变换：map → odom → base_link）
> - `Path` 显示已经规划的路径
> - 设置 `2D Goal Pose` 即可在地图上指定导航目标

## 关键参数说明 (`nav2_params.yaml`)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| controller_server (frequency) | 30 Hz | 控制频率 |
| lookahead_max | 0.6 m | 最大前瞻距离 |
| lookahead_min | 0.3 m | 最小前瞻距离 |
| rotation_smoorther | 2.0 | 旋转平滑系数 |
| amcl (particle_count) | 500–2000 | AMCL 粒子数 |
| map (resolution) | 0.05 m/px | 地图分辨率 |
| map (occupied_thresh) | > 0.65 | 占用阈值 |
| map (free_thresh) | < 0.25 | 自由区域阈值 |


## 参考资料

- [ROS 2 Documentation (Humble)](https://docs.ros.org/en/humble/)
- [Navigation 2 (Nav2)](https://navigation.ros.org/)
- [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [explore_lite (m-explore-ros2)](https://github.com/robo-friends/m-explore-ros2)
- [TurtleBot3 Burger](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)
- [Isaac Sim Documentation](https://docs.omniverse.nvidia.com/isaacsim/)
- [Nav2 Regulated Pure Pursuit Controller](https://navigation.ros.org/plugins/controllers.html#regulated-pure-pursuit)

## 相关教学视频
- [ROS 2机器人开发从入门到实践](https://www.bilibili.com/video/BV1GW42197Ck?vd_source=4d2ca99b593d2f2b9c234c77d695c78c)
- [NVIDIA_Isaac_Sim](https://www.bilibili.com/video/BV1G8kBBvEzR?p=5&vd_source=4d2ca99b593d2f2b9c234c77d695c78c)
- [Isaac_sim(b站搬运)](https://www.bilibili.com/video/BV1PmvsBcEAd?vd_source=4d2ca99b593d2f2b9c234c77d695c78c)
- [Isaac_sim(YouTube原视频)](https://youtube.com/playlist?list=PLU_rF1cv2oRneZp6fsJ2U2Gsn2jY5F8ve&si=QZhPZnxY_vitlig6)

## License

本项目基于 Apache 2.0 许可证开源。
