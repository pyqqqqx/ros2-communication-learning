# ROS2 通讯学习笔记（智能巴哈车队·规控组）

> 完成时间：2026-11-03
> 环境：VMware + Ubuntu 22.04 + ROS2 Humble
> 工作空间：`~/-`（目录名是 `-`）

## 一、任务总览

完整走通一次 ROS2 通讯链路，包含四个环节：

1. **读队友发布**：clone 队友代码，`ros2 topic echo` 读数据
2. **接收方计算**：订阅队友数据，做数学计算并发布结果
3. **自定义接口**：定义自己的消息类型 `.msg`
4. **自己的发布**：参数化节点 + launch 一键启动

| 环节 | 包名 | 类型 | 说明 |
|------|------|------|------|
| 队友发布 | （对方仓库） | — | `git clone --` 避开 `-` 特殊字符 |
| 接收方 | `data_subscriber` | ament_python | calc1/calc2/final 三个节点 |
| 自定义接口 | `my_interfaces` | ament_cmake | `MyData.msg` |
| 自己的发布 | `my_publisher` | ament_python | 参数化节点 + launch |

---

## 二、四个环节的代码骨架

### 1. 接收方计算节点（订阅 + 计算 + 发布）

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from status_interfaces.msg import NodeStatus  # 队友的消息类型

class CalcNode(Node):
    def __init__(self):
        super().__init__('calc1')
        # 缓存最新值（做法 A：取最新一条，不做时间戳对齐）
        self.a1 = self.a2 = self.a3 = 0.0
        self.b1 = self.b2 = self.b3 = 0.0
        self.c1 = self.c2 = self.c3 = 0.0
        # 订阅多个话题
        for topic in ['/node1', '/node2', '/node3']:
            self.create_subscription(NodeStatus, topic, self.make_cb(topic), 10)
        # 发布结果
        self.pub = self.create_publisher(Float32, '/calc1_result', 10)
        # 定时器触发计算
        self.timer = self.create_timer(0.1, self.timer_callback)

    def make_cb(self, topic):
        # 闭包：根据话题名存到对应变量
        def cb(msg):
            val = msg.cpu_usage  # 以队友字段为准
            if topic == '/node1':
                self.a1, self.b1, self.c1 = val, val, val
            # ... 以此类推
        return cb

    def timer_callback(self):
        result = (self.a1 + self.a2 + self.a3) - (self.b1 + self.b2 + self.b3) + (self.c1 + self.c2 + self.c3)
        out = Float32()
        out.data = float(result)  # 关键：必须 float() 转原生 float
        self.pub.publish(out)
```

> ⚠️ **踩坑**：`Float32.data` 只接受原生 `float`，如果直接塞 `numpy.float32` 会报类型错误。务必 `float(result)`（小写 `float`，不是 `Float`）。

### 2. 自定义接口包 `my_interfaces`（ament_cmake）

**`msg/MyData.msg`**：

```
builtin_interfaces/Time stamp
float32[3] data_group
```

**`CMakeLists.txt`** 关键部分：

```cmake
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MyData.msg"
  DEPENDENCIES builtin_interfaces
)
```

**`package.xml`**（重点看结构）：

```xml
<package format="3">
  <name>my_interfaces</name>
  <version>0.0.0</version>
  <description>...</description>
  <maintainer email="...">...</maintainer>
  <license>Apache-2.0</license>

  <!-- ⚠️ 必须在 package 直接子层级，绝对不能放 <export> 里 -->
  <member_of_group>rosidl_interface_packages</member_of_group>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <build_depend>builtin_interfaces</build_depend>
  <exec_depend>builtin_interfaces</exec_depend>
  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

> ⚠️ **最严重踩坑**：`<member_of_group>rosidl_interface_packages</member_of_group>` 一度放在 `<export>` 里，导致 colcon 直接 FATAL。它必须在 `<package>` 的直接子层级。验证方法：
> ```bash
> python3 -c "import catkin_pkg.package as p; print(p.parse_package('package.xml').member_of_groups)"
> ```
> 正常应输出 `[GroupMembership(...)]`，而不是 `[]`。

### 3. 自己的发布节点（参数化 + 5Hz）

**`my_publisher/my_pub.py`**：

```python
import rclpy
import random
from rclpy.node import Node
from my_interfaces.msg import MyData

class MyPub(Node):
    def __init__(self):
        super().__init__("my_pub")
        self.declare_parameter("node_id", 1)          # 声明参数
        node_id = self.get_parameter("node_id").value  # 读参数
        self.topic = f"/pub{node_id}"
        self.publisher = self.create_publisher(MyData, self.topic, 10)
        self.timer = self.create_timer(0.2, self.timer_callback)  # 5Hz

    def timer_callback(self):
        msg = MyData()
        msg.stamp = self.get_clock().now().to_msg()
        msg.data_group = [random.uniform(-20.0, 20.0) for _ in range(3)]
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MyPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### 4. launch 文件（一键启动 5 个节点）

**`launch/pub_launch.py`** —— **标准 launch 文件格式**：

```python
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
                parameters=[{'node_id': i}],   # 通过参数区分节点
                output='screen',
            )
        )
    return LaunchDescription(nodes)
```

**`setup.py` 必须注册 launch 文件**：

```python
from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'my_publisher'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ⚠️ 关键：这一行把 launch 目录装到 share 下，漏了 launch 文件就找不到
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pyqqqx',
    maintainer_email='pyqqqx@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'my_pub = my_publisher.my_pub:main',
        ],
    },
)
```

---

## 三、踩坑记录（按严重程度排序）

### 坑 1：launch 文件内容张冠李戴 → `invalid command 'launch'`（最坑）

**现象**：`ros2 launch my_publisher pub_launch.py` 报：
```
error: invalid command 'launch'
```

**根因**：`pub_launch.py` 里误写了 `setup.py` 的内容（`from setuptools import ...` + `setup(...)`），没有 `generate_launch_description()` 入口函数。

**迷惑点**：报错是 `invalid command 'launch'`，看起来像 `ros2 launch` 这个子命令本身没装好，实际是 launch 文件 import 后找不到入口导致的。

**排查过程（完整试错链）**：
1. 一开始怀疑 `catkin_pkg` 版本冲突 → 清理后 `catkin_pkg` 干净了（1.1.1），还是报错
2. 怀疑 `ros2cli` 扩展没装 → `dpkg -l | grep ros2cli` 显示装了
3. 查 `get_command_extensions('command')` 返回 `[]` → 一度以为扩展发现机制坏了
4. 查 `importlib.metadata` / `pkg_resources` 的 entry_points → 都能读到 20 个扩展（含 launch）
5. 查 `importlib_metadata`、`PLUGIN_SYSTEM_VERSION`、`instantiate_extensions` → 全部正常（返回 20）
6. 最后用 `python3 -c "...main()"` 复现，发现 `[INFO] [launch]` 已经打印了（说明 launch 命令已识别），才定位到是 launch 文件内容问题
7. `cat` launch 文件 → 发现里面是 `setup.py` 的内容，真相大白

**教训**：报错信息有时会误导。当所有"机制"都验证正常时，要回头检查**输入文件本身**。`invalid command 'launch'` 不一定代表命令没装，也可能是 launch 文件坏了。

### 坑 2：`<member_of_group>` 位置错误（最严重，直接 FATAL）

**现象**：colcon build 报 FATAL 错误，接口包编译不过。

**根因**：`<member_of_group>rosidl_interface_packages</member_of_group>` 放进了 `<export>` 块里。

**正确**：放在 `<package>` 的直接子层级（和 `<name>`、`<license>` 平级）。

**排查方法**：对比系统自带的 `status_interfaces/package.xml` 结构，发现正确位置。

### 坑 3：`numpy.float32` 类型错误

**现象**：`Float32.data` 赋值报类型错误。

**根因**：计算结果 `result` 是 `numpy.float32`，而 `Float32.data` 要求原生 `float`。

**修复**：`out.data = float(result)`（注意小写 `float`，别误写成 `Float`）。

### 坑 4：MobaXterm 粘贴破坏代码

**现象**：代码缩进丢失、出现零宽字符、路径变成 `~/--src`。

**修复**：**Python 代码只用 VS Code 写，终端只敲命令**。这是最重要的操作纪律。

### 坑 5：catkin_pkg 版本冲突

**现象**：`ros2 launch` 报 `invalid command`（早期误判）。

**根因**：`pip` 装的 catkin_pkg 0.5.2 与 apt 的 `catkin-pkg-modules` 1.1.1 冲突。

**修复**：清理 pip 版本，只保留 apt 的 1.1.1。

### 坑 6：launch 文件未注册到 setup.py

**现象**：`ros2 launch` 报 `file 'pub_launch.py' not found`。

**根因**：`setup.py` 的 `data_files` 缺了这一行：
```python
(os.path.join('share', package_name, 'launch'), glob('launch/*.py'))
```

---

## 四、关键命令速查

```bash
# 编译（回到工作空间根目录）
cd ~/-
colcon build                              # 全量编译
colcon build --packages-select my_publisher  # 只编译某个包

# 配置环境（每个新终端都要做）
source /opt/ros/humble/setup.bash
source ~/-/install/setup.bash

# 启动 launch
ros2 launch my_publisher pub_launch.py

# 查看话题
ros2 topic list | grep pub
ros2 topic echo /pub1          # 看某话题数据

# 验证接口包的 package.xml 结构
python3 -c "import catkin_pkg.package as p; print(p.parse_package('package.xml').member_of_groups)"
```

---

## 五、验证结果（最终）

- ✅ `/pub1` 话题正常发布：`stamp`（时间戳）+ `data_group`（3 个随机 float），5Hz
- ✅ 5 个话题齐全：`/pub1` `/pub2` `/pub3` `/pub4` `/pub5`
- ✅ 接收方 calc1/calc2 计算正确，final 节点能打印结果

---

## 六、核心收获

1. **launch 文件标准格式**：`generate_launch_description()` + `return LaunchDescription(nodes)`，用 `Node` 的 `parameters` 传参数区分多个同类节点。
2. **接口包 package.xml 规范**：`<member_of_group>` 在 package 直接子层级。
3. **setup.py 三件套**：`packages`（找包）、`data_files`（装 launch/package.xml）、`entry_points`（注册可执行节点）。
4. **调试方法论**：报错信息可能误导，当机制层面都验证正常时，回头检查输入文件本身；用 `python3 -c "...main()"` 复现可以绕过日志吞异常。
5. **操作纪律**：Python 代码 VS Code 写、终端只敲命令；自定义接口包用 ament_cmake，普通节点包用 ament_python。
