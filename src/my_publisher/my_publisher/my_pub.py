import rclpy
import random
from rclpy.node import Node
from my_interfaces.msg import MyData


class MyPub(Node):
    def __init__(self):
        super().__init__("my_pub")
        self.declare_parameter("node_id", 1)
        node_id = self.get_parameter("node_id").value
        self.topic = f"/pub{node_id}"
        self.publisher = self.create_publisher(MyData, self.topic, 10)
        self.timer = self.create_timer(0.2, self.timer_callback)

    def timer_callback(self):
        msg = MyData()
        msg.stamp = self.get_clock().now().to_msg()
        msg.data_group = [random.uniform(-20.0, 20.0) for _ in range(3)]
        self.publisher.publish(msg)
        self.get_logger().info(f"pub {self.topic}: {list(msg.data_group)}")


def main(args=None):
    rclpy.init(args=args)
    node = MyPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
