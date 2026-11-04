import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class FinalNode(Node):
    """鏈€缁堣闃呰€咃細鎹曡幏 calc1_result 鍜?calc2_result 鐨勫疄鏃跺€?""

    def __init__(self):
        super().__init__('final_node')
        self.create_subscription(Float32, '/calc1_result', self.cb1, 10)
        self.create_subscription(Float32, '/calc2_result', self.cb2, 10)

    def cb1(self, msg):
        self.get_logger().info(f'[鎹曡幏] 璁＄畻鑺傜偣1缁撴灉 = {msg.data:.4f}')

    def cb2(self, msg):
        self.get_logger().info(f'[鎹曡幏] 璁＄畻鑺傜偣2缁撴灉 = {msg.data:.4f}')


def main(args=None):
    rclpy.init(args=args)
    node = FinalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
