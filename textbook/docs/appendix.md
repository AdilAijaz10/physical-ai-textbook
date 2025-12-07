---
sidebar_position: 3
---

# Appendix

## A. Mathematical Foundations

### A.1 Coordinate Systems and Transformations

In robotics, proper handling of coordinate systems is crucial. The most common representations include:

#### Homogeneous Transformations
A 4×4 matrix that combines rotation and translation:
```
T = [R  p]
    [0  1]
```
Where R is a 3×3 rotation matrix and p is a 3×1 translation vector.

#### Euler Angles vs. Quaternions
- **Euler Angles**: Three angles (roll, pitch, yaw) that describe orientation but suffer from gimbal lock
- **Quaternions**: Four parameters (w, x, y, z) that avoid singularities and are more efficient for interpolation

Conversion from quaternion to rotation matrix:
```
R = [1-2(y²+z²)  2(xy-wz)    2(xz+wy)]
    [2(xy+wz)    1-2(x²+z²)  2(yz-wx)]
    [2(xz-wy)    2(yz+wx)    1-2(x²+y²)]
```

### A.2 Kinematics Equations

#### Forward Kinematics
Given joint angles θ, compute end-effector pose:
```
T = A₁(θ₁) × A₂(θ₂) × ... × Aₙ(θₙ)
```

#### Inverse Kinematics
Given desired end-effector pose, solve for joint angles. For redundant systems, use:
```
θ̇ = J⁺ × ẋ
```
Where J⁺ is the pseudoinverse of the Jacobian matrix.

### A.3 Control Theory Basics

#### PID Controller
```
u(t) = Kₚe(t) + Kᵢ∫e(τ)dτ + Kd de(t)/dt
```

#### State-Space Representation
```
ẋ = Ax + Bu
y = Cx + Du
```

## B. ROS 2 Command Reference

### B.1 Essential Commands

```bash
# Start a ROS 2 node
ros2 run <package_name> <executable_name>

# List active nodes
ros2 node list

# Get information about a specific node
ros2 node info <node_name>

# List topics
ros2 topic list

# Echo messages on a topic
ros2 topic echo <topic_name> <message_type>

# Publish a message to a topic
ros2 topic pub <topic_name> <message_type> <values>

# List services
ros2 service list

# Call a service
ros2 service call <service_name> <service_type> <request_values>

# List actions
ros2 action list

# Send a goal to an action server
ros2 action send_goal <action_name> <action_type> <goal_values>
```

### B.2 Package Management

```bash
# Create a new package
ros2 pkg create --build-type ament_python <package_name>

# Build the workspace
colcon build

# Source the workspace
source install/setup.bash

# Run tests
colcon test
```

## C. URDF/SDF Syntax Reference

### C.1 URDF Elements

```xml
<!-- Robot definition -->
<robot name="robot_name">
  <!-- Link definition -->
  <link name="link_name">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="1 1 1"/>
        <!-- or <cylinder radius="0.5" length="1"/> -->
        <!-- or <sphere radius="0.5"/> -->
      </geometry>
      <material name="color">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </collision>
  </link>

  <!-- Joint definition -->
  <joint name="joint_name" type="revolute">
    <parent link="parent_link"/>
    <child link="child_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>
</robot>
```

## D. Isaac Sim Configuration Parameters

### D.1 Physics Parameters

```python
# Common Isaac Sim physics settings
physics_settings = {
    "solver_position_iteration_count": 8,      # Position solver iterations
    "solver_velocity_iteration_count": 4,      # Velocity solver iterations
    "solver_projection_iteration_count": 4,    # Projection iterations for joints
    "sleep_threshold": 0.005,                  # Sleep threshold for static objects
    "stabilization_threshold": 0.01,           # Stabilization threshold
    "default_dt": 1.0/60.0,                    # Default time step (60 FPS)
    "use_gpu": True,                          # Use GPU for physics
    "gpu_max_particles": 100000               # Max particles for fluid simulation
}
```

### D.2 Rendering Settings

```python
# Rendering quality settings
rendering_settings = {
    "render_mode": "Ray Tracing",              # Options: "Ray Tracing", "Rasterization"
    "resolution": [1920, 1080],               # Render resolution
    "anti_aliasing": "TAA",                   # Temporal Anti-Aliasing
    "shadows": "full",                        # Full shadows
    "reflections": "ray_traced",              # Ray-traced reflections
    "subsurface_scattering": True,            # Enable SSS
    "global_illumination": True               # Enable GI
}
```

## E. Common Troubleshooting

### E.1 ROS 2 Issues

**Problem**: Nodes can't communicate across machines
**Solution**: Ensure ROS_DOMAIN_ID is the same and network settings allow multicast

**Problem**: "Failed to contact master" errors
**Solution**: Check that ROS 2 daemon is running: `ros2 daemon start`

**Problem**: Permission denied when creating nodes
**Solution**: Check user permissions and ensure proper ROS 2 installation

### E.2 Simulation Issues

**Problem**: Robot falls through the ground
**Solution**: Check collision geometries, mass properties, and friction coefficients

**Problem**: Jittery or unstable simulation
**Solution**: Reduce time step, increase solver iterations, or adjust ERP/CFM values

**Problem**: High CPU usage in simulation
**Solution**: Reduce update rates, simplify collision geometries, or lower physics quality

### E.3 AI/ML Issues

**Problem**: LLM responses are too slow for real-time applications
**Solution**: Use smaller models, implement caching, or optimize API calls

**Problem**: Whisper transcription accuracy is poor
**Solution**: Improve audio quality, adjust model parameters, or use domain-specific fine-tuning

## F. Performance Optimization

### F.1 GPU Optimization

For Isaac Sim and other GPU-intensive applications:

```python
# Enable GPU acceleration
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Optimize memory usage
torch.backends.cudnn.benchmark = True  # Optimize for fixed input sizes
torch.backends.cudnn.deterministic = False  # Allow non-deterministic algorithms
```

### F.2 Real-time Performance

```python
# ROS 2 Quality of Service settings for real-time performance
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# High-performance QoS profile
high_performance_qos = QoSProfile(
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST,
    liveliness=LivelinessPolicy.AUTOMATIC,
    deadline=Duration(seconds=0, nanoseconds=100000000),  # 100ms deadline
    lifespan=Duration(seconds=1)
)
```

## G. Safety Considerations

### G.1 Physical Safety

When deploying humanoid robots in real environments:

1. **Emergency Stop**: Always implement a reliable emergency stop mechanism
2. **Force Limiting**: Implement joint torque limits to prevent injury
3. **Collision Detection**: Use sensors to detect unexpected contacts
4. **Safe Velocities**: Limit joint velocities to safe values
5. **Enclosure Safety**: Ensure safe operating areas with proper barriers

### G.2 Data Privacy

When using LLMs and cloud services:

1. **Data Minimization**: Only send necessary information to cloud services
2. **Local Processing**: Where possible, use local models for sensitive data
3. **Encryption**: Use encrypted connections for all data transmission
4. **Consent**: Obtain proper consent when recording voice or video

## H. Future Technologies

### H.1 Emerging Trends

1. **Foundation Models**: Large models that can handle multiple robotic tasks
2. **Embodied Intelligence**: AI systems with physical interaction capabilities
3. **Sim-to-Real Transfer**: Improved methods for transferring simulation learning to reality
4. **Collaborative Robots**: Safe robots that work alongside humans
5. **Swarm Robotics**: Coordinated behavior of multiple robots

### H.2 Research Directions

1. **Learning from Demonstration**: Robots learning tasks from human examples
2. **Common Sense Reasoning**: Robots understanding everyday physics and social norms
3. **Long-term Autonomy**: Robots operating independently for extended periods
4. **Adaptive Behavior**: Robots adjusting behavior based on environment and user preferences

## I. Code Templates

### I.1 ROS 2 Python Node Template

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TemplateNode(Node):
    def __init__(self):
        super().__init__('template_node')

        # Create publisher
        self.publisher = self.create_publisher(String, 'topic_name', 10)

        # Create subscriber
        self.subscription = self.create_subscription(
            String,
            'input_topic',
            self.listener_callback,
            10
        )

        # Create timer
        self.timer = self.create_timer(0.5, self.timer_callback)

        self.i = 0

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello {self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    node = TemplateNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### I.2 Launch File Template

```xml
<launch>
  <!-- Arguments -->
  <arg name="use_sim_time" default="false"/>

  <!-- Node with parameters -->
  <node pkg="package_name"
        exec="executable_name"
        name="node_name"
        output="screen">
    <param name="param1" value="value1"/>
    <param name="param2" value="value2"/>
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>

  <!-- Include other launch files -->
  <include file="$(find-pkg-share other_package)/launch/other_launch.py"/>
</launch>
```

This appendix provides essential reference information for students and practitioners working with Physical AI and Humanoid Robotics systems. It covers mathematical foundations, technical commands, configuration parameters, troubleshooting guides, and best practices that are frequently needed when developing and deploying robotic systems.