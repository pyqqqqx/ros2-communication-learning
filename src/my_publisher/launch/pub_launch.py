from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """启动 5 个发布节点，node_id 分别为 1~5。"""
    nodes = []
    for i in range(1, 6):
        nodes.append(
            Node(
                package='my_publisher',
                executable='my_pub',
                name='my_pub_{}'.format(i),
                parameters=[{'node_id': i}],
                output='screen',
            )
        )
    return LaunchDescription(nodes)
