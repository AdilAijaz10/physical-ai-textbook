---
sidebar_position: 2
---

# Week 4: Python Integration with rclpy

## Learning Objectives

By the end of this week, you will be able to:
- Create advanced ROS 2 nodes using Python
- Implement service clients and servers in Python
- Use actions for long-running tasks with feedback
- Manage parameters and configuration in ROS 2 nodes
- Handle node lifecycle and state management

## Introduction to rclpy

`rclpy` is the Python client library for ROS 2 that provides Python bindings to the ROS 2 client library (rcl). It allows you to create ROS 2 nodes, publishers, subscribers, services, and actions using Python.

### Key Features of rclpy
- Native Python integration with ROS 2
- Asynchronous and synchronous execution models
- Comprehensive parameter management
- Lifecycle node support
- Action client and server implementation

## Advanced Node Creation

### Creating Nodes with Parameters

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ParameterizedNode(Node):
    def __init__(self):
        super().__init__('parameterized_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'default_robot')
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('debug_mode', False)

        # Get parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.debug_mode = self.get_parameter('debug_mode').value

        # Create publisher
        self.publisher_ = self.create_publisher(String, 'robot_status', 10)

        # Create timer with dynamic rate
        self.timer = self.create_timer(
            1.0 / self.publish_rate,
            self.timer_callback
        )

        self.get_logger().info(
            f'Initialized {self.robot_name} with rate {self.publish_rate}Hz'
        )

    def timer_callback(self):
        msg = String()
        msg.data = f'{self.robot_name} is running at {self.publish_rate}Hz'
        self.publisher_.publish(msg)
        if self.debug_mode:
            self.get_logger().debug(f'Published: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = ParameterizedNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Parameter Callbacks

```python
from rcl_interfaces.msg import ParameterDescriptor
from rcl_interfaces.msg import ParameterType

class DynamicParameterNode(Node):
    def __init__(self):
        super().__init__('dynamic_param_node')

        # Declare parameter with descriptor
        descriptor = ParameterDescriptor(
            type=ParameterType.PARAMETER_INTEGER,
            description='Update rate in Hz',
            integer_range=[ParameterDescriptor().integer_range[0].set__from_value(1).set__to_value(100)]
        )

        self.declare_parameter('update_rate', 1, descriptor)

        # Register parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.publisher_ = self.create_publisher(String, 'param_updates', 10)
        self.update_timer()

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'update_rate' and param.type == ParameterType.PARAMETER_INTEGER:
                if 1 <= param.value <= 100:
                    self.get_logger().info(f'Update rate changed to {param.value}Hz')
                    self.update_timer()
                    return SetParametersResult(successful=True)
                else:
                    self.get_logger().warn(f'Invalid update rate: {param.value}')
                    return SetParametersResult(successful=False)
        return SetParametersResult(successful=True)

    def update_timer(self):
        rate = self.get_parameter('update_rate').value
        if hasattr(self, 'timer'):
            self.timer.destroy()
        self.timer = self.create_timer(1.0 / rate, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Rate: {self.get_parameter("update_rate").value}Hz'
        self.publisher_.publish(msg)
```

## Service Clients and Servers

### Service Server Implementation

```python
from example_interfaces.srv import AddTwoInts
from std_msgs.msg import String

class MathService(Node):
    def __init__(self):
        super().__init__('math_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback
        )
        self.history_publisher = self.create_publisher(String, 'calculation_history', 10)

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'{request.a} + {request.b} = {response.sum}')

        # Publish to history
        history_msg = String()
        history_msg.data = f'{request.a} + {request.b} = {response.sum}'
        self.history_publisher.publish(history_msg)

        return response

def main(args=None):
    rclpy.init(args=args)
    service = MathService()
    rclpy.spin(service)
    service.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service Client Implementation

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MathClient(Node):
    def __init__(self):
        super().__init__('math_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints)

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    client = MathClient()

    response = client.send_request(42, 38)
    if response:
        client.get_logger().info(f'Result: {response.sum}')
    else:
        client.get_logger().error('Service call failed')

    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Action Implementation

Actions are used for long-running tasks that provide feedback and can be canceled:

### Action Server

```python
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import rclpy

from my_robot_interfaces.action import NavigateToPose  # Custom action
from geometry_msgs.msg import Pose
from std_msgs.msg import String

class NavigateActionServer(Node):
    def __init__(self):
        super().__init__('navigate_action_server')

        # Use reentrant callback group for actions
        callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            NavigateToPose,
            'navigate_to_pose',
            execute_callback=self.execute_callback,
            callback_group=callback_group,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.feedback_publisher = self.create_publisher(String, 'navigation_feedback', 10)

    def goal_callback(self, goal_request):
        self.get_logger().info('Received navigation goal')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing navigation goal...')

        feedback_msg = NavigateToPose.Feedback()
        result = NavigateToPose.Result()

        # Simulate navigation
        for i in range(0, 101, 10):  # 0% to 100%
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                result.success = False
                return result

            # Update feedback
            feedback_msg.progress = float(i)
            goal_handle.publish_feedback(feedback_msg)

            # Publish to feedback topic
            feedback_topic_msg = String()
            feedback_topic_msg.data = f'Navigation progress: {i}%'
            self.feedback_publisher.publish(feedback_topic_msg)

            # Simulate work
            await asyncio.sleep(0.5)

        goal_handle.succeed()
        result.success = True
        self.get_logger().info('Navigation completed successfully')

        return result

def main(args=None):
    rclpy.init(args=args)
    action_server = NavigateActionServer()

    executor = MultiThreadedExecutor()
    executor.add_node(action_server)

    try:
        executor.spin()
    finally:
        action_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    import asyncio
    main()
```

### Action Client

```python
from rclpy.action import ActionClient
from rclpy.node import Node
import rclpy

from my_robot_interfaces.action import NavigateToPose
from geometry_msgs.msg import Pose

class NavigateActionClient(Node):
    def __init__(self):
        super().__init__('navigate_action_client')
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

    def send_goal(self, target_pose):
        goal_msg = NavigateToPose.Goal()
        goal_msg.target_pose = target_pose

        self._action_client.wait_for_server()

        # Send goal and get future
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.progress}%')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.success}')

def main(args=None):
    rclpy.init(args=args)
    action_client = NavigateActionClient()

    # Create a sample target pose
    target_pose = Pose()
    target_pose.position.x = 1.0
    target_pose.position.y = 2.0
    target_pose.position.z = 0.0

    action_client.send_goal(target_pose)

    rclpy.spin(action_client)
    action_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Asynchronous Programming in ROS 2

### Using Async/Await with rclpy

```python
import asyncio
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class AsyncNode(Node):
    def __init__(self):
        super().__init__('async_node')
        self.publisher = self.create_publisher(String, 'async_topic', 10)

        # Create an async timer
        self.async_timer = self.create_timer(
            1.0,  # 1 second
            self.async_timer_callback
        )

        # Create async executor
        self.loop = asyncio.get_event_loop()

    async def async_timer_callback(self):
        # Simulate async work
        await asyncio.sleep(0.1)

        msg = String()
        msg.data = f'Async message at {self.get_clock().now()}'
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AsyncNode()

    # Use MultiThreadedExecutor for async operations
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Exercise

### Exercise 1: Robot Arm Controller
Create a ROS 2 package with:
1. An action server for controlling a robot arm with feedback
2. A client that sends joint position goals
3. Parameter management for safety limits
4. Service for querying current joint states

### Exercise 2: Sensor Fusion Node
Create a node that:
1. Subscribes to multiple sensor topics
2. Uses parameters to configure fusion algorithms
3. Publishes fused sensor data
4. Provides services for calibration

## Advanced Topics

### Timer Management
```python
# Create timer with different rates
slow_timer = self.create_timer(2.0, self.slow_callback)  # Every 2 seconds
fast_timer = self.create_timer(0.1, self.fast_callback)  # Every 0.1 seconds

# Destroy timer when needed
slow_timer.destroy()
```

### Node Composition
```python
from rclpy.node import Node
from rclpy import Parameter

class CompositeNode(Node):
    def __init__(self):
        super().__init__('composite_node')

        # Initialize multiple components within one node
        self.sensor_component = SensorComponent(self)
        self.control_component = ControlComponent(self)
        self.planning_component = PlanningComponent(self)
```

## Summary

This week covered advanced Python integration with ROS 2:
- Parameter management and dynamic reconfiguration
- Service implementation with clients and servers
- Action patterns for long-running tasks
- Asynchronous programming techniques
- Advanced node composition patterns

## Next Week Preview

Week 5 will focus on URDF (Unified Robot Description Format) for creating humanoid robot models, including kinematic chains, joint constraints, and physical properties.