from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='data_publisher', executable='data_pub',
             parameters=[{'node_id': i}], name=f'data_pub_{i}')
        for i in range(1, 6)
    ])