# ROS2 订阅方开发学习笔记

> 规控组第一次 ROS2 任务 —— 接收方（订阅+计算）实操记录
> 记录人：pyqqqx ｜ 时间：2026-11-03 ｜ 环境：VMware Ubuntu 22.04 + ROS2 Humble

---

## 一、任务背景

对方（陈明丰）交付了一个发布方工作空间，内含 5 个发布节点，向 `/node1` ~ `/node5` 发自定义消息。我方作为接收方，需要：

1. 读懂对方的发布；
2. 写两个计算节点 + 一个最终订阅者；
3. 自己再写一套 5 个发布节点交给对方。

---

## 二、读懂对方的发布

### 消息接口（status_interfaces/msg/Data）

```
builtin_interfaces/Time stamp      # 时间戳
float32[3] data_group              # 三维数组 = a b c
```

- `data_group[0]` → a，`data_group[1]` → b，`data_group[2]` → c
- 5 个话题 `/node1` ~ `/node5`，频率 5Hz，数据为 [-20, 20] 随机数
- 5 个话题相互独立、不同步，`stamp` 只是各节点各自发布时刻

### 验证命令（按顺序）

```bash
ros2 node list                          # 看到 data_pub_1 ~ data_pub_5
ros2 topic list -t                      # 看到 /node1~5，类型 status_interfaces/msg/Data
ros2 interface show status_interfaces/msg/Data
ros2 topic echo /node1                  # 实时读到 data_group（就是 a b c）
ros2 topic hz /node1                    # 验证约 5.0 Hz
```

---

## 三、克隆对方仓库的坑

仓库名是 `-`（特殊字符），直接写会被当成命令选项：

```bash
git clone -- https://github.com/MingfengChen-mf/-.git   # 必须加 --
cd ./-                                                  # 进入叫 - 的目录，不能用 cd -
```

---

## 四、接收方功能包 data_subscriber 的搭建

### 1. 建包

```bash
ros2 pkg create data_subscriber --build-type ament_python \
  --dependencies rclpy std_msgs status_interfaces --license Apache-2.0
```

> **踩坑**：`ros2 pkg create` 会把包建在当前目录。必须在工作空间根目录下先 `cd ~/-` 再建，且建完后确认包在 `src/` 下，否则 `colcon build` 找不到。若建错位置，用 `mv` 移到 `src/`。

### 2. 三个节点

| 节点 | 订阅 | 公式 | 输出话题 |
|---|---|---|---|
| calc1_node | /node1 /node2 /node3 | (a1+a2+a3)-(b1+b2+b3)+(c1+c2+c3) | /calc1_result |
| calc2_node | /node4 /node5 | (a4+b4)*(a5-b5) | /calc2_result |
| final_node | /calc1_result /calc2_result | 只打印捕获值 | — |

结果类型用 `std_msgs/Float32`。

### 3. 缓存最新值策略（做法 A）

三个话题不同步，所以每个节点用一个字典缓存各话题最新一次收到的 `data_group`，只要所有依赖话题都有值就重算一次：

```python
self.latest = {'node1': None, 'node2': None, 'node3': None}

def cb(self, msg, key):
    self.latest[key] = list(msg.data_group)
    if all(v is not None for v in self.latest.values()):
        self.compute()
```

### 4. setup.py 注册（重点踩坑）

`entry_points` 必须是 `setup()` 的**顶层参数**，和 `extras_require` 平级：

```python
extras_require={
    'test': ['pytest'],
},
entry_points={
    'console_scripts': [
        'calc1_node = data_subscriber.calc1_node:main',
        'calc2_node = data_subscriber.calc2_node:main',
        'final_node = data_subscriber.final_node:main',
    ],
},
```

> **踩坑**：手动改 setup.py 时，容易把 `entry_points` 错误地嵌进 `extras_require` 的 `'test'` 列表里，导致结构错乱。手动粘贴反复出错时，用 `cat > 文件 <<'EOF'` 直接整段写入更可靠。

---

## 五、两个关键报错（必记）

### 报错 1：`AssertionError: The 'data' field must be of type 'float'`

- 原因：`msg.data_group` 元素是 `numpy.float32`，算出来的 `result` 也是 numpy 类型，而 `Float32().data` 要求原生 `float`。
- 解决：赋值前强制转换 `out.data = float(result)`。

### 报错 2：`NameError: name 'Float' is not defined`

- 原因：把 `float` 误写成大写 `Float`（Python 大小写敏感）。
- 解决：改成小写 `float(result)`。

### 报错 3：`Package 'data_subscriber' not found`

- 原因：新开的终端没 source 工作空间。
- 解决：每个新终端先 `source ~/-/install/setup.bash`。

---

## 六、构建与运行完整流程

```bash
cd ~/-
colcon build                 # 看到 3 packages finished
source ~/-/install/setup.bash

# 终端1：启动对方发布
ros2 launch data_publisher pub_launch.py

# 终端2/3/4：分别启动自己的节点（每个终端都要先 source）
ros2 run data_subscriber calc1_node
ros2 run data_subscriber calc2_node
ros2 run data_subscriber final_node
```

---

## 七、心得总结

1. **注册体系三分法**：节点代码走 `entry_points`，launch 文件走 `data_files`，msg 走 `CMakeLists.txt`。
2. **每个新终端都要 source**，这是 ROS2 最容易被忽略的坑。
3. **numpy 类型 vs 原生类型**：ROS2 消息字段对类型有严格要求，赋值前注意转换。
4. **改 .py 后要重新 `colcon build`**（除非用了 `--symlink-install`）。
5. 遇到报错先读最后一行错误信息，往往直接点出根因。
