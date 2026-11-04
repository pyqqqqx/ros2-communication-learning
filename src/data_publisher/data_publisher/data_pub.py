import rclpy
from rclpy.node import Node
import random
from status_interfaces.msg import Data  # 自定义消息接口


class DataPub(Node):
    def __init__(self):
        super().__init__('data_pub')
        self.declare_parameter('node_id', 1)
        self.node_id = self.get_parameter('node_id').value
        self.publisher = self.create_publisher(Data, f'/node{self.node_id}', 10)
        self.create_timer(0.2, self.timer_callback)  # 5Hz

    def timer_callback(self):
        msg = Data()
        msg.stamp = self.get_clock().now().to_msg()
        data_list=[]
        for i in range(3):
            data=random.uniform(-20,20)  # 生成随机数
            data_list.append(data)
        # 用 random 生成三维数组，每次回调现场生成
        # 也可以用 msg.data = [random.uniform(-20, 20) for _ in range(3)] 列表生成器
        msg.data_group= data_list
        self.publisher.publish(msg)
        self.get_logger().info(f'node{self.node_id} published: {msg}')  # 日志带时间戳和数据


def main(args=None):
    rclpy.init(args=args)
    node = DataPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()