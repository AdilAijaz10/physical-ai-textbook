---
sidebar_position: 1
---

# Week 6: Physics Simulation in Gazebo

## Learning Objectives

By the end of this week, you will be able to:
- Set up and configure Gazebo simulation environments
- Create realistic physics models for humanoid robots
- Implement sensor simulation for LiDAR, cameras, and IMUs
- Configure physics parameters for stable humanoid locomotion
- Debug and optimize simulation performance

## Introduction to Gazebo

Gazebo is a 3D dynamic simulator with accurate physics simulation, rendering, and sensor models. For humanoid robotics, Gazebo provides a realistic environment to test control algorithms, sensor fusion, and locomotion patterns before deployment on physical robots.

### Key Features of Gazebo
- **Physics Engine**: ODE (Open Dynamics Engine) for accurate physics simulation
- **Sensor Simulation**: Realistic models for cameras, LiDAR, IMUs, and other sensors
- **Rendering**: High-quality 3D visualization with OGRE graphics engine
- **ROS Integration**: Native support for ROS/ROS 2 communication
- **Plugin System**: Extensible architecture for custom behaviors and sensors

## Installing and Setting Up Gazebo

### Installing Gazebo Garden
```bash
# Add Gazebo repository
sudo apt update && sudo apt install wget lsb-release gnupg
wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/gazebo-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo.list > /dev/null
sudo apt update

# Install Gazebo Garden
sudo apt install gazebo-garden
```

### Verifying Installation
```bash
# Launch Gazebo GUI
gazebo

# Launch Gazebo server (headless)
gz sim -s
```

## Basic Gazebo Concepts

### Worlds
A world file defines the environment, including:
- Terrain and static objects
- Physics parameters
- Lighting and atmospheric conditions
- Initial robot placements

Example world file:
```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="humanoid_world">
    <!-- Physics parameters -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <gravity>0 0 -9.8</gravity>
    </physics>

    <!-- Include a ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Include a sun light -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Your robot model -->
    <include>
      <uri>model://humanoid_robot</uri>
      <pose>0 0 1 0 0 0</pose>
    </include>

    <!-- Add other objects -->
    <model name="table">
      <pose>2 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 0.5 0.8</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 0.5 0.8</size>
            </box>
          </geometry>
        </visual>
        <inertial>
          <mass>10</mass>
          <inertia>
            <ixx>1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1</iyy>
            <iyz>0</iyz>
            <izz>1</izz>
          </inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

## Physics Configuration for Humanoid Robots

### Time Step and Real-time Factor
```xml
<physics type="ode">
  <!-- Smaller time steps for stability -->
  <max_step_size>0.001</max_step_size>

  <!-- Real-time performance -->
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>

  <!-- Gravity -->
  <gravity>0 0 -9.8</gravity>

  <!-- ODE solver parameters -->
  <ode>
    <solver>
      <type>quick</type>
      <iters>10</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Material Properties
```xml
<!-- In your URDF/SDF model -->
<collision name="foot_collision">
  <geometry>
    <box>
      <size>0.2 0.1 0.05</size>
    </box>
  </geometry>
  <surface>
    <friction>
      <ode>
        <mu>0.8</mu>
        <mu2>0.8</mu2>
        <fdir1>0 0 1</fdir1>
      </ode>
    </friction>
    <bounce>
      <restitution_coefficient>0.01</restitution_coefficient>
      <threshold>100000</threshold>
    </bounce>
    <contact>
      <ode>
        <soft_cfm>0.00000001</soft_cfm>
        <soft_erp>0.2</soft_erp>
        <kp>1000000000000.0</kp>
        <kd>1.0</kd>
        <max_vel>100.0</max_vel>
        <min_depth>0.001</min_depth>
      </ode>
    </contact>
  </surface>
</collision>
```

## Sensor Simulation

### Camera Sensors
```xml
<sdf version="1.7">
  <model name="humanoid_robot">
    <!-- ... other links and joints ... -->

    <link name="camera_link">
      <sensor name="head_camera" type="camera">
        <camera>
          <horizontal_fov>1.047</horizontal_fov> <!-- 60 degrees -->
          <image>
            <width>640</width>
            <height>480</height>
            <format>R8G8B8</format>
          </image>
          <clip>
            <near>0.1</near>
            <far>100</far>
          </clip>
        </camera>
        <update_rate>30</update_rate>
        <always_on>true</always_on>
        <visualize>true</visualize>
      </sensor>
    </link>
  </model>
</sdf>
```

### LiDAR Sensors
```xml
<link name="lidar_link">
  <sensor name="front_lidar" type="gpu_lidar">
    <pose>0.1 0 0.1 0 0 0</pose>
    <gpu_lidar>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-1.570796</min_angle> <!-- -90 degrees -->
          <max_angle>1.570796</max_angle>    <!-- 90 degrees -->
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
      <always_on>true</always_on>
      <update_rate>10</update_rate>
      <visualize>true</visualize>
    </gpu_lidar>
  </sensor>
</link>
```

### IMU Sensors
```xml
<link name="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.001</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.001</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.001</stddev>
          </noise>
        </z>
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
  </sensor>
</link>
```

## Gazebo Plugins for Humanoid Robots

### ROS 2 Control Plugin
```xml
<gazebo>
  <plugin filename="libgazebo_ros2_control-system.so" name="gazebo_ros2_control::GazeboSystem">
    <robot_param>robot_description</robot_param>
    <robot_param_node>robot_state_publisher</robot_param_node>
    <parameters>/path/to/ros2_control_config.yaml</parameters>
  </plugin>
</gazebo>
```

### Joint State Publisher
```xml
<gazebo>
  <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
    <robot_namespace>/humanoid</robot_namespace>
    <joint_name>left_hip_joint</joint_name>
    <joint_name>left_knee_joint</joint_name>
    <joint_name>left_ankle_joint</joint_name>
    <!-- Add all joint names -->
    <update_rate>30</update_rate>
  </plugin>
</gazebo>
```

### Contact Sensors
```xml
<gazebo reference="left_foot">
  <sensor name="left_foot_contact" type="contact">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <contact>
      <collision>left_foot_collision</collision>
    </contact>
    <plugin name="left_foot_contact_plugin" filename="libgazebo_ros_bumper.so">
      <alwaysOn>true</alwaysOn>
      <updateRate>100.0</updateRate>
      <frameName>left_foot</frameName>
      <bumperTopicName>left_foot_bumper</bumperTopicName>
      <gaussianNoise>0.0</gaussianNoise>
    </plugin>
  </sensor>
</gazebo>
```

## Launching Gazebo with ROS 2

### Creating a Launch File
```python
# launch/humanoid_gazebo.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='humanoid_world.sdf')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': world,
            'verbose': 'true'
        }.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': open(PathJoinSubstitution([
                FindPackageShare('my_robot_description'),
                'urdf',
                'humanoid.urdf'
            ]).perform({})).read()
        }]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'humanoid_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '1.0'
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='humanoid_world.sdf',
            description='Choose one of the world files from `/my_robot_gazebo/worlds`'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity
    ])
```

## Performance Optimization

### Reducing Simulation Load
```xml
<!-- In your world file -->
<physics type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>

  <!-- Optimize for humanoid simulation -->
  <ode>
    <solver>
      <type>quick</type>
      <iters>50</iters>  <!-- Increase for stability -->
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>1e-5</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>10.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Sensor Optimization
```xml
<!-- Reduce sensor update rates for performance -->
<sensor name="camera" type="camera">
  <update_rate>15</update_rate>  <!-- Lower from 30 -->
  <camera>
    <image>
      <width>320</width>  <!-- Lower resolution -->
      <height>240</height>
    </image>
  </camera>
</sensor>
```

## Debugging Simulation Issues

### Common Problems and Solutions

1. **Robot falls through ground**:
   - Check collision geometries in URDF
   - Verify inertial properties
   - Adjust friction parameters

2. **Jittery or unstable movement**:
   - Reduce time step size
   - Increase solver iterations
   - Adjust ERP and CFM values

3. **High CPU usage**:
   - Reduce update rates
   - Simplify collision geometries
   - Use fewer sensors during development

### Debugging Commands
```bash
# Check physics parameters
gz topic -t /world/humanoid_world/physics -n 1

# Monitor joint states
ros2 topic echo /joint_states

# Check TF tree
ros2 run tf2_tools view_frames
```

## Practical Exercise

### Exercise 1: Basic Humanoid Simulation
1. Create a simple humanoid URDF model
2. Create a Gazebo world file with ground plane
3. Launch the simulation and verify the robot spawns correctly
4. Test joint movements using ROS 2 commands

### Exercise 2: Sensor Integration
1. Add camera and IMU sensors to your humanoid model
2. Configure sensor parameters appropriately
3. Verify sensor data publication in ROS 2
4. Visualize sensor data in RViz

## Advanced Topics

### Terrain and Environment
```xml
<world name="outdoor_world">
  <!-- Add uneven terrain -->
  <model name="terrain">
    <static>true</static>
    <link name="terrain_link">
      <collision name="collision">
        <geometry>
          <heightmap>
            <uri>file://path/to/heightmap.png</uri>
            <size>100 100 10</size>
            <pos>0 0 0</pos>
          </heightmap>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <heightmap>
            <uri>file://path/to/texture.png</uri>
            <size>100 100 10</size>
          </heightmap>
        </geometry>
      </visual>
    </link>
  </model>
</world>
```

### Multi-Robot Simulation
```xml
<!-- In your world file -->
<include>
  <uri>model://humanoid_robot</uri>
  <name>robot1</name>
  <pose>0 0 1 0 0 0</pose>
</include>

<include>
  <uri>model://humanoid_robot</uri>
  <name>robot2</name>
  <pose>2 0 1 0 0 0</pose>
</include>
```

## Summary

This week covered physics simulation in Gazebo:
- Gazebo installation and basic concepts
- World file creation and physics configuration
- Sensor simulation for humanoid robots
- ROS 2 integration and launch files
- Performance optimization techniques
- Debugging common simulation issues

## Next Week Preview

Week 7 will focus on high-fidelity rendering in Unity and advanced sensor simulation techniques for creating photorealistic environments.