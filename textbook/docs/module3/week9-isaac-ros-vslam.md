---
sidebar_position: 2
---

# Week 9: Isaac ROS for VSLAM and Navigation

## Learning Objectives

By the end of this week, you will be able to:
- Install and configure NVIDIA Isaac ROS packages
- Implement Visual SLAM (VSLAM) systems for humanoid robots
- Set up perception pipelines using Isaac ROS
- Configure and tune navigation systems for bipedal robots
- Integrate SLAM with navigation for autonomous humanoid operation

## Introduction to Isaac ROS

Isaac ROS is NVIDIA's collection of GPU-accelerated perception and navigation packages built for ROS 2. It provides high-performance implementations of essential robotics algorithms optimized for NVIDIA GPUs, making it ideal for humanoid robots that require real-time perception and navigation capabilities.

### Key Isaac ROS Packages
- **Isaac ROS Visual SLAM**: GPU-accelerated SLAM with visual-inertial odometry
- **Isaac ROS Apriltag**: High-performance fiducial detection
- **Isaac ROS Stereo Image Proc**: GPU-accelerated stereo processing
- **Isaac ROS Object Detection**: Real-time object detection and tracking
- **Isaac ROS Manipulation**: GPU-accelerated manipulation algorithms

## Installing Isaac ROS

### Prerequisites
- **Hardware**: NVIDIA GPU with CUDA support (RTX 3060 or better)
- **Software**: ROS 2 Humble Hawksbill, CUDA 11.8+, cuDNN 8.6+
- **System**: Ubuntu 20.04 or 22.04 LTS

### Installation Methods

#### Method 1: Debian Package Installation
```bash
# Add NVIDIA repository
curl -sL https://nvidia.github.io/nvidia-container-runtime/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -sL https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list

# Update package lists
sudo apt update

# Install Isaac ROS packages
sudo apt install nvidia-isaaс-ros-<package-name>
```

#### Method 2: Docker Installation
```bash
# Pull Isaac ROS Docker image
docker pull nvcr.io/nvidia/isaac-ros:latest

# Run Isaac ROS container
docker run --gpus all -it --rm \
  --env NVIDIA_VISIBLE_DEVICES=all \
  --env NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --env ROS_DOMAIN_ID=1 \
  --network host \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --env DISPLAY=$DISPLAY \
  nvcr.io/nvidia/isaac-ros:latest
```

## Isaac ROS Visual SLAM

### Overview of Visual SLAM
Visual SLAM (Simultaneous Localization and Mapping) allows robots to build a map of their environment while simultaneously tracking their position within it using visual sensors. Isaac ROS Visual SLAM combines:
- Visual-inertial odometry for accurate pose estimation
- Loop closure detection for map consistency
- GPU acceleration for real-time performance

### Setting up Visual SLAM
```python
# visual_slam_setup.py - Isaac ROS Visual SLAM configuration
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
import message_filters
import cv2
from cv_bridge import CvBridge

class IsaacROSVisualSLAM(Node):
    def __init__(self):
        super().__init__('isaac_ros_visual_slam')

        # Parameters
        self.declare_parameter('enable_slam', True)
        self.declare_parameter('enable_localization', False)
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        # Publishers
        self.pose_pub = self.create_publisher(PoseStamped, 'slam/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, 'slam/odometry', 10)
        self.map_pub = self.create_publisher(OccupancyGrid, 'slam/map', 10)

        # Subscribers with synchronization
        self.left_image_sub = message_filters.Subscriber(
            self, Image, 'camera/left/image_rect_color'
        )
        self.right_image_sub = message_filters.Subscriber(
            self, Image, 'camera/right/image_rect_color'
        )
        self.imu_sub = message_filters.Subscriber(
            self, Imu, 'imu/data'
        )

        # Synchronize topics
        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.left_image_sub, self.right_image_sub, self.imu_sub],
            queue_size=10,
            slop=0.1
        )
        self.ts.registerCallback(self.slam_callback)

        # CV Bridge for image processing
        self.cv_bridge = CvBridge()

        self.get_logger().info('Isaac ROS Visual SLAM node initialized')

    def slam_callback(self, left_msg, right_msg, imu_msg):
        """Process synchronized sensor data for SLAM"""
        try:
            # Convert ROS images to OpenCV
            left_cv = self.cv_bridge.imgmsg_to_cv2(left_msg, 'bgr8')
            right_cv = self.cv_bridge.imgmsg_to_cv2(right_msg, 'bgr8')

            # Process with Isaac ROS Visual SLAM
            # This is a conceptual example - actual implementation uses Isaac ROS nodes
            pose = self.process_visual_slam(left_cv, right_cv, imu_msg)

            # Publish results
            self.publish_pose(pose, left_msg.header.stamp)
            self.publish_odometry(pose, left_msg.header.stamp)

        except Exception as e:
            self.get_logger().error(f'Error in SLAM callback: {e}')

    def process_visual_slam(self, left_image, right_image, imu_data):
        """Process visual SLAM (conceptual implementation)"""
        # In practice, this would interface with Isaac ROS Visual SLAM nodes
        # For now, we'll return a dummy pose
        import numpy as np
        pose = {
            'position': np.array([0.0, 0.0, 0.0]),
            'orientation': np.array([0.0, 0.0, 0.0, 1.0])  # w, x, y, z
        }
        return pose

    def publish_pose(self, pose, timestamp):
        """Publish pose estimate"""
        pose_msg = PoseStamped()
        pose_msg.header.stamp = timestamp
        pose_msg.header.frame_id = self.get_parameter('map_frame').value
        pose_msg.pose.position.x = pose['position'][0]
        pose_msg.pose.position.y = pose['position'][1]
        pose_msg.pose.position.z = pose['position'][2]
        pose_msg.pose.orientation.w = pose['orientation'][0]
        pose_msg.pose.orientation.x = pose['orientation'][1]
        pose_msg.pose.orientation.y = pose['orientation'][2]
        pose_msg.pose.orientation.z = pose['orientation'][3]

        self.pose_pub.publish(pose_msg)

    def publish_odometry(self, pose, timestamp):
        """Publish odometry"""
        odom_msg = Odometry()
        odom_msg.header.stamp = timestamp
        odom_msg.header.frame_id = self.get_parameter('odom_frame').value
        odom_msg.child_frame_id = self.get_parameter('base_frame').value
        odom_msg.pose.pose.position.x = pose['position'][0]
        odom_msg.pose.pose.position.y = pose['position'][1]
        odom_msg.pose.pose.position.z = pose['position'][2]
        odom_msg.pose.pose.orientation.w = pose['orientation'][0]
        odom_msg.pose.pose.orientation.x = pose['orientation'][1]
        odom_msg.pose.pose.orientation.y = pose['orientation'][2]
        odom_msg.pose.pose.orientation.z = pose['orientation'][3]

        self.odom_pub.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    slam_node = IsaacROSVisualSLAM()

    try:
        rclpy.spin(slam_node)
    except KeyboardInterrupt:
        pass
    finally:
        slam_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Launch File for Visual SLAM
```xml
<!-- launch/visual_slam.launch.xml -->
<launch>
  <!-- Arguments -->
  <arg name="enable_slam" default="true"/>
  <arg name="enable_localization" default="false"/>
  <arg name="map_frame" default="map"/>
  <arg name="odom_frame" default="odom"/>
  <arg name="base_frame" default="base_link"/>

  <!-- Isaac ROS Visual SLAM node -->
  <node pkg="isaac_ros_visual_slam"
        exec="visual_slam_node"
        name="visual_slam"
        output="screen">
    <param name="enable_slam" value="$(var enable_slam)"/>
    <param name="enable_localization" value="$(var enable_localization)"/>
    <param name="map_frame" value="$(var map_frame)"/>
    <param name="odom_frame" value="$(var odom_frame)"/>
    <param name="base_frame" value="$(var base_frame)"/>
    <param name="use_sim_time" value="true"/>
  </node>

  <!-- Image processing nodes -->
  <node pkg="isaac_ros_stereo_image_proc"
        exec="stereo_image_rectify_node"
        name="stereo_rectify"
        output="screen">
    <param name="use_sim_time" value="true"/>
  </node>

  <!-- IMU filter -->
  <node pkg="imu_filter_madgwick"
        exec="imu_filter_madgwick_node"
        name="imu_filter"
        output="screen">
    <param name="use_mag" value="false"/>
    <param name="publish_tf" value="false"/>
    <param name="use_sim_time" value="true"/>
  </node>
</launch>
```

## Isaac ROS Perception Pipeline

### Stereo Processing
```python
# stereo_processing.py - Isaac ROS stereo processing
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from stereo_msgs.msg import DisparityImage
from sensor_msgs.msg import PointCloud2
import message_filters

class IsaacROSPerceptionPipeline(Node):
    def __init__(self):
        super().__init__('isaac_ros_perception')

        # Parameters
        self.declare_parameter('disparity_range', 128)
        self.declare_parameter('min_disparity', 0)
        self.declare_parameter('max_disparity', 127)

        # Publishers
        self.disparity_pub = self.create_publisher(DisparityImage, 'disparity', 10)
        self.pointcloud_pub = self.create_publisher(PointCloud2, 'points2', 10)

        # Subscribers with approximate synchronization
        self.left_sub = message_filters.Subscriber(self, Image, 'left/image_rect')
        self.right_sub = message_filters.Subscriber(self, Image, 'right/image_rect')
        self.left_info_sub = message_filters.Subscriber(self, CameraInfo, 'left/camera_info')
        self.right_info_sub = message_filters.Subscriber(self, CameraInfo, 'right/camera_info')

        # Approximate time synchronizer
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.left_sub, self.right_sub, self.left_info_sub, self.right_info_sub],
            queue_size=10,
            slop=0.1
        )
        self.sync.registerCallback(self.stereo_callback)

        self.get_logger().info('Isaac ROS Perception Pipeline initialized')

    def stereo_callback(self, left_msg, right_msg, left_info_msg, right_info_msg):
        """Process stereo images for depth estimation"""
        # In practice, this would call Isaac ROS stereo processing nodes
        # For demonstration, we'll publish a placeholder
        self.get_logger().info(f'Processing stereo pair: {left_msg.header.stamp}')

        # Publish disparity image (conceptual)
        disparity_msg = DisparityImage()
        disparity_msg.header = left_msg.header
        # Actual disparity computation would happen here
        self.disparity_pub.publish(disparity_msg)

def main(args=None):
    rclpy.init(args=args)
    perception_node = IsaacROSPerceptionPipeline()

    try:
        rclpy.spin(perception_node)
    except KeyboardInterrupt:
        pass
    finally:
        perception_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Object Detection Integration
```python
# object_detection_integration.py - Isaac ROS object detection
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, ObjectHypothesisWithPose
from geometry_msgs.msg import Point
import numpy as np

class IsaacROSObjectDetection(Node):
    def __init__(self):
        super().__init__('isaac_ros_object_detection')

        # Parameters
        self.declare_parameter('model_path', '/models/yolov8n_640x640.onnx')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('nms_threshold', 0.4)

        # Publishers
        self.detections_pub = self.create_publisher(Detection2DArray, 'detections', 10)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )

        self.get_logger().info('Isaac ROS Object Detection initialized')

    def image_callback(self, msg):
        """Process image for object detection"""
        # In practice, this would interface with Isaac ROS object detection nodes
        # For now, we'll create a mock detection
        detections = Detection2DArray()
        detections.header = msg.header

        # Add mock detections (in practice, this would come from the detection model)
        for i in range(3):  # Create 3 mock detections
            detection = Detection2D()
            detection.header = msg.header
            detection.bbox.center.x = 100 + i * 50
            detection.bbox.center.y = 100 + i * 30
            detection.bbox.size_x = 50
            detection.bbox.size_y = 80

            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = f'object_{i}'
            hypothesis.hypothesis.score = 0.8 - i * 0.1
            detection.results.append(hypothesis)

            detections.detections.append(detection)

        self.detections_pub.publish(detections)

def main(args=None):
    rclpy.init(args=args)
    detection_node = IsaacROSObjectDetection()

    try:
        rclpy.spin(detection_node)
    except KeyboardInterrupt:
        pass
    finally:
        detection_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Navigation Setup for Humanoid Robots

### Configuring Nav2 for Bipedal Navigation
```yaml
# config/nav2_params.yaml
amcl:
  ros__parameters:
    use_sim_time: True
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_footprint"
    beam_span: 0.0628318530718
    bmt_threshold: 0.25
    freq: 10.0
    inv_squash: 0.5
    lambda_short: 0.1
    likelihood_max_dist: 2.0
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05
    scan_topic: scan

bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: True
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    # Humanoid-specific behavior tree
    default_nav_to_pose_bt_xml: "humanoid_nav_to_pose.xml"

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.001
    min_theta_velocity_threshold: 0.001
    # Humanoid-specific controllers
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # Humanoid FollowPath controller
    FollowPath:
      plugin: "nav2_mppi_controller::Controller"
      time_steps: 50
      model_dt: 0.05
      batch_size: 2000
      vx_std: 0.3
      vy_std: 0.05
      wz_std: 0.4
      vx_max: 0.8
      vx_min: -0.2
      vy_max: 0.3
      wz_max: 1.0
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      simulation_timeout: 2.0
      penalty_dt: 0.2
      # Humanoid-specific penalties
      goal_angle_penalty: 2.0
      goal_dist_penalty: 5.0
      ref_vel_penalty: 1.0
      obstacle_penalty: 50.0
      obstacle_etheta_penalty: 5.0
      max_robot_acceleration: 2.5  # Humanoid-specific acceleration limits
      max_robot_deceleration: 5.0  # Humanoid-specific deceleration limits

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 10.0
      publish_frequency: 10.0
      global_frame: odom
      robot_base_frame: base_footprint
      use_sim_time: True
      rolling_window: true
      width: 6
      height: 6
      resolution: 0.05
      robot_radius: 0.3  # Humanoid-specific radius
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.2
        z_voxels: 8
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_footprint
      use_sim_time: True
      robot_radius: 0.3
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner::NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

### Humanoid-Specific Navigation Controller
```python
# humanoid_controller.py - Custom controller for humanoid navigation
import rclpy
from rclpy.node import Node
from nav2_core.controller import Controller
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, Twist
from tf2_ros import Buffer
import numpy as np

class HumanoidController(Controller):
    def __init__(self, name):
        super().__init__(name)
        self.initialized = False

    def configure(self, tf_client):
        """Configure the controller"""
        self.tf_buffer = Buffer()
        self.initialized = True
        self.get_logger().info(f'{self.get_name()} controller configured')

    def cleanup(self):
        """Cleanup the controller"""
        self.get_logger().info(f'{self.get_name()} controller cleaned up')

    def activate(self):
        """Activate the controller"""
        self.get_logger().info(f'{self.get_name()} controller activated')

    def deactivate(self):
        """Deactivate the controller"""
        self.get_logger().info(f'{self.get_name()} controller deactivated')

    def setPlan(self, path):
        """Set the global plan"""
        self.global_plan = path
        self.get_logger().info(f'Set plan with {len(path.poses)} poses')

    def computeVelocityCommands(self, pose, velocity, goal_checker):
        """Compute velocity commands for humanoid navigation"""
        # Humanoid-specific velocity computation
        cmd_vel = Twist()

        # Calculate distance to next waypoint
        if len(self.global_plan.poses) > 0:
            next_waypoint = self.global_plan.poses[0].pose.position
            current_pos = pose.position

            dx = next_waypoint.x - current_pos.x
            dy = next_waypoint.y - current_pos.y
            distance = np.sqrt(dx*dx + dy*dy)

            # Humanoid-specific approach
            # Bipedal robots need to be more careful with turning
            cmd_vel.linear.x = min(0.3, distance * 0.5)  # Conservative speed
            cmd_vel.angular.z = np.arctan2(dy, dx) * 0.5  # Gentle turning

            # Apply humanoid constraints
            cmd_vel.linear.x = max(-0.1, min(cmd_vel.linear.x, 0.5))  # Speed limits
            cmd_vel.angular.z = max(-0.5, min(cmd_vel.angular.z, 0.5))  # Turn limits

        return cmd_vel

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidController('HumanoidController')

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## SLAM and Navigation Integration

### Launch File for Complete System
```xml
<!-- launch/humanoid_navigation.launch.xml -->
<launch>
  <!-- Arguments -->
  <arg name="use_sim_time" default="true"/>
  <arg name="map" default=""/>

  <!-- Map server -->
  <node pkg="nav2_map_server"
        exec="map_server"
        name="map_server"
        output="screen">
    <param name="yaml_filename" value="$(var map)"/>
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>

  <!-- Local and global costmap servers -->
  <node pkg="nav2_costmap_2d"
        exec="nav2_costmap_2d"
        name="local_costmap"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <node pkg="nav2_costmap_2d"
        exec="nav2_costmap_2d"
        name="global_costmap"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <!-- Isaac ROS Visual SLAM -->
  <include file="$(find-pkg-share isaac_ros_visual_slam)/launch/visual_slam.launch.py">
    <arg name="use_sim_time" value="$(var use_sim_time)"/>
  </include>

  <!-- Navigation stack -->
  <node pkg="nav2_planner"
        exec="planner_server"
        name="planner_server"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <node pkg="nav2_controller"
        exec="controller_server"
        name="controller_server"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <node pkg="nav2_recoveries"
        exec="recoveries_server"
        name="recoveries_server"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <node pkg="nav2_bt_navigator"
        exec="bt_navigator"
        name="bt_navigator"
        output="screen">
    <param from="$(find-pkg-share my_robot_bringup)/config/nav2_params.yaml"/>
  </node>

  <!-- Lifecycle manager -->
  <node pkg="nav2_lifecycle_manager"
        exec="lifecycle_manager"
        name="lifecycle_manager_navigation"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
    <param name="autostart" value="true"/>
    <param name="node_names" value="[map_server, local_costmap, global_costmap, planner_server, controller_server, recoveries_server, bt_navigator]"/>
  </node>
</launch>
```

## Performance Tuning

### Optimizing Isaac ROS Performance
```python
# performance_tuner.py - Isaac ROS performance tuning
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
import time

class IsaacROSPeformanceTuner(Node):
    def __init__(self):
        super().__init__('isaac_ros_performance_tuner')

        # Parameters for tuning
        self.declare_parameter('input_queue_size', 10)
        self.declare_parameter('processing_rate', 30.0)
        self.declare_parameter('gpu_memory_fraction', 0.8)

        # Publishers for performance metrics
        self.fps_pub = self.create_publisher(Float32, 'performance/fps', 10)
        self.processing_time_pub = self.create_publisher(Float32, 'performance/processing_time', 10)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'input/image_raw', self.process_image,
            self.get_parameter('input_queue_size').value
        )

        # Timer for performance monitoring
        self.processing_rate = self.get_parameter('processing_rate').value
        self.timer = self.create_timer(1.0/self.processing_rate, self.performance_callback)

        self.frame_count = 0
        self.last_time = time.time()

    def process_image(self, msg):
        """Process image with performance monitoring"""
        start_time = time.time()

        # Simulate Isaac ROS processing
        # In reality, this would call Isaac ROS nodes
        self.simulate_processing()

        processing_time = time.time() - start_time

        # Publish performance metrics
        processing_time_msg = Float32()
        processing_time_msg.data = processing_time
        self.processing_time_pub.publish(processing_time_msg)

        self.frame_count += 1

    def simulate_processing(self):
        """Simulate Isaac ROS processing (replace with actual Isaac ROS calls)"""
        # This would be replaced with actual Isaac ROS processing
        import time
        time.sleep(0.01)  # Simulate processing time

    def performance_callback(self):
        """Publish performance metrics"""
        current_time = time.time()
        elapsed = current_time - self.last_time

        if elapsed > 0:
            fps = self.frame_count / elapsed
            fps_msg = Float32()
            fps_msg.data = fps
            self.fps_pub.publish(fps_msg)

        self.frame_count = 0
        self.last_time = current_time

def main(args=None):
    rclpy.init(args=args)
    tuner = IsaacROSPeformanceTuner()

    try:
        rclpy.spin(tuner)
    except KeyboardInterrupt:
        pass
    finally:
        tuner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Exercise

### Exercise 1: Isaac ROS Installation and Setup
1. Install Isaac ROS packages using Docker or native installation
2. Verify installation with basic perception nodes
3. Test stereo processing with sample data
4. Validate GPU acceleration is working

### Exercise 2: Visual SLAM Implementation
1. Set up stereo cameras in your simulation environment
2. Configure Isaac ROS Visual SLAM node
3. Test SLAM with moving robot
4. Evaluate map quality and pose accuracy

### Exercise 3: Navigation System
1. Configure Nav2 with humanoid-specific parameters
2. Set up costmaps for humanoid navigation
3. Test path planning and execution
4. Evaluate navigation performance in various environments

## Advanced Topics

### Multi-Sensor Fusion
```python
# multi_sensor_fusion.py - Fusing Isaac ROS with other sensors
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu, LaserScan
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf2_ros import TransformBroadcaster
import numpy as np

class MultiSensorFusion(Node):
    def __init__(self):
        super().__init__('multi_sensor_fusion')

        # Publishers
        self.pose_pub = self.create_publisher(PoseWithCovarianceStamped, 'fused_pose', 10)

        # Subscribers
        self.image_sub = self.create_subscription(Image, 'camera/image_raw', self.image_callback, 10)
        self.imu_sub = self.create_subscription(Imu, 'imu/data', self.imu_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)

        # Sensor fusion state
        self.last_image_time = None
        self.last_imu_data = None
        self.last_scan_data = None

        # Covariance matrices for fusion
        self.process_noise = np.eye(6) * 0.1
        self.observation_noise = np.eye(6) * 0.5

        self.get_logger().info('Multi-sensor fusion node initialized')

    def image_callback(self, msg):
        """Handle image data for visual odometry"""
        self.last_image_time = msg.header.stamp
        # Process with Isaac ROS visual processing
        pass

    def imu_callback(self, msg):
        """Handle IMU data"""
        self.last_imu_data = msg
        # Integrate with visual odometry
        pass

    def scan_callback(self, msg):
        """Handle laser scan data"""
        self.last_scan_data = msg
        # Use for localization and mapping
        pass

def main(args=None):
    rclpy.init(args=args)
    fusion_node = MultiSensorFusion()

    try:
        rclpy.spin(fusion_node)
    except KeyboardInterrupt:
        pass
    finally:
        fusion_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

This week covered Isaac ROS for VSLAM and navigation:
- Isaac ROS installation and setup
- Visual SLAM implementation with GPU acceleration
- Perception pipeline configuration
- Navigation system setup for humanoid robots
- Performance optimization techniques
- Multi-sensor fusion approaches

## Next Week Preview

Week 10 will focus on Nav2 for bipedal movement, where you'll learn to configure navigation systems specifically for humanoid robot locomotion patterns and gait planning.