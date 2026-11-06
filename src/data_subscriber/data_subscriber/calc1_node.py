import rclpy
from rclpy.node import Node
from status_interfaces.msg import Data
from std_msgs.msg import Float32


class Calc1Node(Node):
    """计算节点1：订阅 /node1 /node2 /node3，算 (a1+a2+a3)-(b1+b2+b3)+(c1+c2+c3)"""

    def __init__(self):
        super().__init__('calc1_node')
        self.latest = {'node1': None, 'node2': None, 'node3': None}

        self.create_subscription(Data, '/node1', lambda m: self.cb(m, 'node1'), 10)
        self.create_subscription(Data, '/node2', lambda m: self.cb(m, 'node2'), 10)
        self.create_subscription(Data, '/node3', lambda m: self.cb(m, 'node3'), 10)

        self.result_pub = self.create_publisher(Float32, '/calc1_result', 10)

    def cb(self, msg, key):
        self.latest[key] = list(msg.data_group)
        if all(v is not None for v in self.latest.values()):
            self.compute()

    def compute(self):
        a1, b1, c1 = self.latest['node1']
        a2, b2, c2 = self.latest['node2']
        a3, b3, c3 = self.latest['node3']

        result = (a1 + a2 + a3) - (b1 + b2 + b3) + (c1 + c2 + c3)

        out = Float32()
        out.data = float(result)
        self.result_pub.publish(out)
        self.get_logger().info(f'calc1 result = {result:.4f}')


def main(args=None):
    rclpy.init(args=args)
    node = Calc1Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
