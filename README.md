# ROS2 通讯任务交付包

> 智能巴哈车队 · 规控组
> 作者：pyqqqqx
> 交付日期：2026-11-03
> 环境要求：Ubuntu 22.04 + ROS2 Humble

## 一、这是什么

这是一套完整的 ROS2 通讯学习/任务代码，包含 **5 个功能包**，实现了从"队友发布 → 接收计算 → 自定义接口 → 自己发布"的完整通讯链路。

| 包名 | 类型 | 作用 |
|------|------|------|
| `data_publisher` | ament_python | 发布 node1~5 数据（发布方） |
| `status_interfaces` | ament_cmake | 队友的消息接口（`Data.msg`） |
| `data_subscriber` | ament_python | 订阅并计算（calc1/calc2/final） |
| `my_interfaces` | ament_cmake | 自定义消息接口（`MyData.msg`） |
| `my_publisher` | ament_python | 参数化发布节点 + launch |

## 二、如何复现

### 1. 准备环境

确保已安装 ROS2 Humble（Ubuntu 22.04）。如果没有，参考官方文档安装。

### 2. 创建工作空间并放入代码

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
# 把交付包解压到 src 下
tar xzf ~/ros2_task_deliver.tar.gz
```

解压后 `src/` 下应该有这 5 个目录：
```
data_publisher/  data_subscriber/  my_interfaces/  my_publisher/  status_interfaces/
```

### 3. 编译

```bash
cd ~/ros2_ws
colcon build
```

> 预期：编译成功，`Summary: 5 packages finished`。

### 4. 配置环境（每个新终端都要做）

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

### 5. 运行

#### 方式一：launch 一键启动自己的发布节点

```bash
ros2 launch my_publisher pub_launch.py
```

会启动 `my_pub_1` ~ `my_pub_5` 五个节点，分别往 `/pub1` ~ `/pub5` 发数据（5Hz）。

#### 方式二：手动逐个启动（队友的发布节点）

```bash
# 终端 1：启动队友的发布节点（node1~5）
ros2 run data_publisher data_pub --ros-args -p node_id:=1
# ... 以此类推启动 node2~5，或看 data_publisher/launch/pub_launch.py

# 终端 2：启动接收计算节点
ros2 run data_subscriber calc1_node
ros2 run data_subscriber calc2_node
ros2 run data_subscriber final_node
```

### 6. 验证

```bash
# 查看所有话题
ros2 topic list

# 查看发布数据
ros2 topic echo /pub1

# 查看计算结果
ros2 topic echo /calc1_result
ros2 topic echo /calc2_result
```

---

## 三、各包说明

### data_publisher（队友的发布方）
- 节点：`data_pub`
- 发布话题：`/node1` ~ `/node5`
- 消息类型：`status_interfaces/msg/Data`

### status_interfaces（队友的接口包）
- `msg/Data.msg`：数据消息定义

### data_subscriber（接收计算）
- `calc1_node.py`：订阅 `/node1`~`/node3`，计算 `(a1+a2+a3)-(b1+b2+b3)+(c1+c2+c3)`，发布到 `/calc1_result`
- `calc2_node.py`：订阅 `/node4`~`/node5`，计算 `(a4+b4)*(a5-b5)`，发布到 `/calc2_result`
- `final_node.py`：订阅两个结果并打印

### my_interfaces（自定义接口）
- `msg/MyData.msg`：
  ```
  builtin_interfaces/Time stamp
  float32[3] data_group
  ```

### my_publisher（自己的发布方）
- 节点：`my_pub`（参数化，`node_id` 参数区分节点）
- 发布话题：`/pub{node_id}`，即 `/pub1` ~ `/pub5`
- 消息类型：`my_interfaces/msg/MyData`
- launch：`pub_launch.py` 一键启动 5 个节点

---

## 四、关键踩坑提醒（避免重复踩坑）

1. **launch 文件格式**：必须是 `generate_launch_description()` + `return LaunchDescription(...)`，不能写成 setup.py 内容。
2. **接口包 package.xml**：`<member_of_group>rosidl_interface_packages</member_of_group>` 必须在 `<package>` 直接子层级，不能放 `<export>` 里。
3. **Float32 赋值**：`msg.data = float(结果)`，必须用原生 `float` 转换，不能用 numpy.float32。
4. **setup.py 三件套**：`packages`（找包）+ `data_files`（装 launch/package.xml）+ `entry_points`（注册节点）。
