---
sidebar_position: 3
---

# Week 5: URDF for Humanoid Robots

## Learning Objectives

By the end of this week, you will be able to:
- Create comprehensive URDF models for humanoid robots
- Define kinematic chains and joint constraints
- Specify physical properties and collision geometries
- Integrate sensors into humanoid robot models
- Validate and debug URDF models

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML-based format used to describe robots in ROS. For humanoid robots, URDF defines the physical structure, kinematic properties, and sensor placements.

### Key Components of URDF
- **Links**: Rigid parts of the robot (torso, limbs, head)
- **Joints**: Connections between links (revolute, prismatic, fixed)
- **Inertial properties**: Mass, center of mass, and inertia tensor
- **Visual and collision geometries**: How the robot looks and interacts with the environment
- **Sensors**: Placement and properties of sensors

## URDF Structure for Humanoid Robots

### Basic Humanoid Structure

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.2"/>
      </geometry>
    </collision>
  </link>

  <!-- Torso -->
  <link name="torso">
    <inertial>
      <mass value="5.0"/>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.4"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.4"/>
      </geometry>
    </collision>
  </link>

  <!-- Joint connecting base to torso -->
  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>

  <!-- Left leg -->
  <link name="left_hip">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="torso_to_left_hip" type="revolute">
    <parent link="torso"/>
    <child link="left_hip"/>
    <origin xyz="0 0.1 0.4" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <!-- Add more links and joints for complete humanoid model -->
</robot>
```

## Joint Types for Humanoid Robots

### Revolute Joints
For rotational movement (shoulders, elbows, knees, hips):
```xml
<joint name="left_knee" type="revolute">
  <parent link="left_thigh"/>
  <child link="left_shin"/>
  <origin xyz="0 0 -0.3" rpy="0 0 0"/>
  <axis xyz="1 0 0"/>
  <limit lower="0" upper="2.356" effort="50" velocity="2"/>
  <dynamics damping="0.1" friction="0.0"/>
</joint>
```

### Continuous Joints
For unlimited rotation (waist, neck):
```xml
<joint name="waist_yaw" type="continuous">
  <parent link="torso"/>
  <child link="waist"/>
  <origin xyz="0 0 0.4" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <dynamics damping="0.1"/>
</joint>
```

### Fixed Joints
For rigid connections:
```xml
<joint name="head_camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.05" rpy="0 0 0"/>
</joint>
```

## Advanced URDF Features

### Xacro for Complex Models

Xacro (XML Macros) helps manage complex humanoid models:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_xacro">

  <!-- Define properties -->
  <xacro:property name="PI" value="3.1415926535897931"/>
  <xacro:property name="torso_mass" value="5.0"/>
  <xacro:property name="leg_mass" value="2.0"/>
  <xacro:property name="link_radius" value="0.05"/>
  <xacro:property name="link_length" value="0.3"/>

  <!-- Macro for creating limbs -->
  <xacro:macro name="limb_link" params="name xyz mass radius length">
    <link name="${name}">
      <inertial>
        <mass value="${mass}"/>
        <origin xyz="${xyz}" rpy="0 0 0"/>
        <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
      </inertial>
      <visual>
        <origin xyz="${xyz}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${radius}" length="${length}"/>
        </geometry>
        <material name="gray">
          <color rgba="0.5 0.5 0.5 1"/>
        </material>
      </visual>
      <collision>
        <origin xyz="${xyz}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${radius}" length="${length}"/>
        </geometry>
      </collision>
    </link>
  </xacro:macro>

  <!-- Macro for creating joints -->
  <xacro:macro name="hinge_joint" params="name parent child xyz axis lower upper">
    <joint name="${name}" type="revolute">
      <parent link="${parent}"/>
      <child link="${child}"/>
      <origin xyz="${xyz}" rpy="0 0 0"/>
      <axis xyz="${axis}"/>
      <limit lower="${lower}" upper="${upper}" effort="100" velocity="1"/>
      <dynamics damping="0.1"/>
    </joint>
  </xacro:macro>

  <!-- Use macros to build the robot -->
  <xacro:limb_link name="torso" xyz="0 0 0.2" mass="5.0" radius="0.1" length="0.4"/>
  <xacro:limb_link name="left_thigh" xyz="0 0 -0.15" mass="2.0" radius="0.05" length="0.3"/>
  <xacro:hinge_joint name="hip_joint" parent="torso" child="left_thigh"
                     xyz="0 0.1 0.2" axis="1 0 0" lower="-1.57" upper="1.57"/>

</robot>
```

## Sensor Integration

### Camera Sensors
```xml
<link name="camera_link">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.05 0.05 0.03"/>
    </geometry>
    <material name="black">
      <color rgba="0 0 0 1"/>
    </material>
  </visual>
</link>

<joint name="head_to_camera" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.05" rpy="0 0 0"/>
</joint>

<!-- Gazebo plugin for camera simulation -->
<gazebo reference="camera_link">
  <sensor type="camera" name="head_camera">
    <update_rate>30</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.047</horizontal_fov>
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
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <frame_name>camera_link</frame_name>
      <topic_name>head_camera/image_raw</topic_name>
    </plugin>
  </sensor>
</gazebo>
```

### IMU Sensors
```xml
<link name="imu_link">
  <inertial>
    <mass value="0.01"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/>
  </inertial>
</link>

<joint name="torso_to_imu" type="fixed">
  <parent link="torso"/>
  <child link="imu_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>

<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <visualize>true</visualize>
  </sensor>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
    <frame_name>imu_link</frame_name>
    <topic_name>imu/data</topic_name>
  </plugin>
</gazebo>
```

## Physical Properties and Dynamics

### Inertial Calculations
```xml
<!-- For a cylinder (torso) -->
<inertial>
  <mass value="5.0"/>
  <origin xyz="0 0 0.2" rpy="0 0 0"/>
  <inertia
    ixx="0.05"  <!-- (1/12)*m*(3*r² + h²) -->
    ixy="0.0"
    ixz="0.0"
    iyy="0.05"
    iyz="0.0"
    izz="0.025"/> <!-- (1/2)*m*r² -->
</inertial>
```

### Friction and Damping
```xml
<joint name="knee_joint" type="revolute">
  <parent link="thigh"/>
  <child link="shin"/>
  <origin xyz="0 0 -0.3" rpy="0 0 0"/>
  <axis xyz="1 0 0"/>
  <limit lower="0" upper="2.356" effort="50" velocity="2"/>
  <dynamics damping="1.0" friction="0.5"/>
</joint>
```

## URDF Validation and Debugging

### Checking URDF with check_urdf
```bash
# Install urdfdom package
sudo apt install ros-humble-urdfdom-py

# Validate your URDF
check_urdf /path/to/your/robot.urdf

# Get detailed info
check_urdf --verbose /path/to/your/robot.urdf
```

### Visualizing URDF
```bash
# Launch robot state publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(cat /path/to/your/robot.urdf)'

# Visualize in RViz
ros2 run rviz2 rviz2
```

### Common URDF Issues and Solutions

1. **Missing joint connections**: Ensure every link (except the base) has exactly one parent joint
2. **Inconsistent units**: Use meters for lengths, kilograms for mass
3. **Invalid joint limits**: Ensure lower < upper for revolute joints
4. **Collision issues**: Check that collision geometries match visual geometries

## Practical Exercise

### Exercise 1: Complete Humanoid Model
Create a URDF model for a simple humanoid robot with:
1. Torso with head
2. Two arms with 3 DOF each (shoulder, elbow, wrist)
3. Two legs with 3 DOF each (hip, knee, ankle)
4. Camera sensor in the head
5. IMU sensor in the torso

### Exercise 2: Validation and Testing
1. Validate your URDF using check_urdf
2. Visualize in RViz
3. Load into Gazebo simulation
4. Test joint limits and ranges

## Advanced Topics

### Transmission Elements
```xml
<transmission name="left_shoulder_trans">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_shoulder_pitch">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_shoulder_motor">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

### Gazebo Integration
```xml
<gazebo>
  <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
    <robotNamespace>/humanoid</robotNamespace>
  </plugin>
</gazebo>
```

## Summary

This week covered URDF for humanoid robots:
- Basic URDF structure and components
- Joint types and constraints for humanoid kinematics
- Xacro macros for managing complex models
- Sensor integration in URDF
- Physical properties and dynamics
- Validation and debugging techniques

## Next Week Preview

Module 2 begins with Week 6: Physics Simulation in Gazebo, where you'll learn to create realistic simulation environments for your humanoid robots.