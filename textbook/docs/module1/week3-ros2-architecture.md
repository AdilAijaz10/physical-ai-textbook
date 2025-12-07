---
sidebar_position: 1
---

# Week 3: ROS 2 Architecture Fundamentals

## Learning Objectives

By the end of this week, you will be able to:
- Explain the core concepts of ROS 2 architecture
- Create and run basic ROS 2 nodes, topics, and services
- Understand the differences between ROS 1 and ROS 2
- Implement publisher/subscriber patterns for robot communication

## Introduction to ROS 2

ROS 2 (Robot Operating System 2) is the next-generation robotics framework designed for production environments. Unlike ROS 1, ROS 2 is built on DDS (Data Distribution Service) for robust, real-time communication between robot components.

### Key Improvements in ROS 2
- **Real-time support**: Deterministic behavior for time-critical applications
- **Multi-robot systems**: Native support for multi-robot coordination
- **Security**: Built-in security features for production deployment
- **Cross-platform**: Support for Linux, Windows, and macOS
- **Quality of Service (QoS)**: Configurable reliability and performance settings

## Core Concepts

### Nodes
Nodes are the fundamental building blocks of ROS 2. Each node runs a specific task and communicates with other nodes through topics, services, or actions.

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1
```

### Topics and Messages
Topics enable asynchronous communication between nodes through a publish/subscribe pattern. Messages are the data structures passed between nodes.

Common message types:
- `std_msgs`: Basic data types (String, Int32, Float64, etc.)
- `sensor_msgs`: Sensor data (LaserScan, Image, Imu, etc.)
- `geometry_msgs`: Spatial information (Pose, Twist, Point, etc.)
- `nav_msgs`: Navigation data (Odometry, Path, OccupancyGrid, etc.)

### Services
Services provide synchronous request/response communication between nodes.

```python
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning: {response.sum}')
        return response
```

### Actions
Actions are used for long-running tasks with feedback and goal management.

## Installation and Environment Setup

### Installing ROS 2 Humble Hawksbill

```bash
# Add ROS 2 apt repository
sudo apt update && sudo apt install -y curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install ros-humble-desktop
```

### Environment Configuration

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Add to ~/.bashrc for persistent sourcing
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

## Creating Your First ROS 2 Package

### Package Structure
```
ros2_ws/
├── src/
    └── my_robot_package/
        ├── CMakeLists.txt
        ├── package.xml
        ├── launch/
        ├── rviz/
        ├── src/
        └── test/
```

### Creating the Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_robot_package
cd my_robot_package
```

## Publisher/Subscriber Example

Let's create a simple publisher and subscriber to understand the communication pattern:

### Publisher Code
```python
# my_robot_package/my_robot_package/talker.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2 World: {self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    talker = Talker()
    rclpy.spin(talker)
    talker.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Subscriber Code
```python
# my_robot_package/my_robot_package/listener.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    listener = Listener()
    rclpy.spin(listener)
    listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Running the Example
```bash
# Terminal 1: Run the publisher
cd ~/ros2_ws
source install/setup.bash
ros2 run my_robot_package talker

# Terminal 2: Run the subscriber
cd ~/ros2_ws
source install/setup.bash
ros2 run my_robot_package listener
```

## Quality of Service (QoS) Settings

QoS profiles allow you to configure communication behavior:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# Create a QoS profile for reliable communication
qos_profile = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST
)

publisher = self.create_publisher(String, 'topic', qos_profile)
```

## Lifecycle Nodes

Lifecycle nodes provide better control over node state transitions:

```python
from rclpy.lifecycle import LifecycleNode, LifecycleState
from rclpy.lifecycle import TransitionCallbackReturn

class LifecycleTalker(LifecycleNode):
    def __init__(self):
        super().__init__('lifecycle_talker')
        self.publisher = None

    def on_configure(self, state):
        self.publisher = self.create_publisher(String, 'chatter', 10)
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state):
        self.timer = self.create_timer(0.5, self.timer_callback)
        return super().on_activate(state)

    def timer_callback(self):
        msg = String()
        msg.data = 'Lifecycle node message'
        self.publisher.publish(msg)
```

## Practical Exercise

### Exercise 1: Temperature Monitor
Create a ROS 2 package with:
1. A publisher node that simulates temperature readings
2. A subscriber node that logs temperatures and alerts if above threshold
3. A service that returns the current temperature status

### Exercise 2: Robot Command Interface
Create a service that accepts movement commands and returns execution status.

## Summary

This week covered the fundamental concepts of ROS 2 architecture:
- Nodes as the basic execution units
- Topics for asynchronous communication
- Services for synchronous request/response
- Actions for long-running tasks with feedback
- Quality of Service settings for communication behavior
- Lifecycle management for robust node operation

## Next Week Preview

Week 4 will focus on Python integration with rclpy, covering advanced node programming, parameter management, and client library usage.