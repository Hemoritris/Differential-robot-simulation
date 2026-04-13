from setuptools import setup

setup(
    name='isaac_slam_navigation',
    version='0.1.0',
    packages=['isaac_slam_navigation'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/isaac_slam_navigation']),
        ('share/isaac_slam_navigation/launch', [
            'launch/isaac_nav.launch.py',
            'launch/isaac_nav_only.launch.py',
        ]),
        ('share/isaac_slam_navigation/config', [
            'config/nav2_params.yaml',
        ]),
    ],
)
