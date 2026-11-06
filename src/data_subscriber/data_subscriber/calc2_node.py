import rclpy
from rclpy.node import Node
from status_interfaces.msg import Data
from std_msgs.msg import Float32


class Calc2Node(Node):
    """计算节点2：订阅 /node4 /node5，算 (a4+b4)*(a5-b5)"""

    def __init__(self):
        super().__init__('calc2_node')
        self.latest = {'node4': None, 'node5': None}

        self.create_subscription(Data, '/node4', lambda m: self.cb(m, 'node4'), 10)
        self.create_subscription(Data, '/node5', lambda m: self.cb(m, 'node5'), 10)

        self.result_pub = self.create_publisher(Float32, '/calc2_result', 10)

    def cb(self, msg, key):
        self.latest[key] = list(msg.data_group)
        if all(v is not None for v in self.latest.values()):
            self.compute()

    def compute(self):
        a4, b4, c4 = self.latest['node4']
        a5, b5, c5 = self.latest['node5']

        result = (a4 + b4) * (a5 - b5)

        out = Float32()
        out.data = float(result)
        self.result_pub.publish(out)
        self.get_logger().info(f'calc2 result = {result:.4f}')


def main(args=None):
    rclpy.init(args=args)
    node = Calc2Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
