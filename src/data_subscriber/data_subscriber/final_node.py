import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class FinalNode(Node):
    """最终订阅者：捕获 calc1_result 和 calc2_result 的实时值"""

    def __init__(self):
        super().__init__('final_node')
        self.create_subscription(Float32, '/calc1_result', self.cb1, 10)
        self.create_subscription(Float32, '/calc2_result', self.cb2, 10)

    def cb1(self, msg):
        self.get_logger().info(f'[捕获] 计算节点1结果 = {msg.data:.4f}')

    def cb2(self, msg):
        self.get_logger().info(f'[捕获] 计算节点2结果 = {msg.data:.4f}')


def main(args=None):
    rclpy.init(args=args)
    node = FinalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
