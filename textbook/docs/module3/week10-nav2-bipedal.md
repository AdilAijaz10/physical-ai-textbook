---
sidebar_position: 3
---

# Week 10: Nav2 for Bipedal Movement

## Learning Objectives

By the end of this week, you will be able to:
- Configure Nav2 specifically for bipedal humanoid robots
- Implement gait-based path planning and execution
- Adapt navigation parameters for bipedal locomotion characteristics
- Handle unique challenges of bipedal navigation (balance, step planning)
- Create custom controllers for humanoid-specific movement patterns

## Introduction to Bipedal Navigation

Bipedal navigation presents unique challenges compared to wheeled or tracked robots. Humanoid robots must maintain balance while navigating, plan footsteps carefully, and adapt their gait to different terrains and obstacles. Nav2 (Navigation 2) can be configured and extended to handle these unique requirements.

### Key Differences from Wheeled Navigation
- **Balance constraints**: Maintaining center of mass within support polygon
- **Step planning**: Discrete foot placement rather than continuous motion
- **Gait patterns**: Different walking styles (walking, stepping, climbing)
- **Dynamic stability**: Continuous balance adjustments during movement
- **Terrain adaptation**: Handling stairs, slopes, and uneven surfaces

## Bipedal-Specific Navigation Architecture

### High-Level Navigation Flow
```python
# bipedal_nav_architecture.py - Bipedal navigation architecture
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, OccupancyGrid
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String
import numpy as np

class BipedalNavigationSystem(Node):
    def __init__(self):
        super().__init__('bipedal_navigation_system')

        # Navigation state
        self.navigation_state = 'IDLE'  # IDLE, PLANNING, EXECUTING, PAUSED, ERROR
        self.current_gait = 'WALKING'   # WALKING, STEPPING, CLIMBING
        self.balance_state = 'STABLE'   # STABLE, UNSTABLE, RECOVERING

        # Publishers
        self.path_pub = self.create_publisher(Path, 'bipedal_path', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.gait_cmd_pub = self.create_publisher(String, 'gait_command', 10)
        self.navigation_state_pub = self.create_publisher(String, 'navigation_state', 10)

        # Subscribers
        self.goal_sub = self.create_subscription(
            PoseStamped, 'move_base_simple/goal', self.goal_callback, 10
        )
        self.map_sub = self.create_subscription(
            OccupancyGrid, 'map', self.map_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10
        )

        # Navigation parameters
        self.declare_parameter('step_size', 0.3)  # Maximum step size
        self.declare_parameter('step_height', 0.1)  # Step height for obstacles
        self.declare_parameter('max_step_up', 0.15)  # Max climb height
        self.declare_parameter('max_step_down', 0.1)  # Max descent height
        self.declare_parameter('gait_frequency', 2.0)  # Steps per second
        self.declare_parameter('balance_margin', 0.05)  # Safety margin for balance

        self.get_logger().info('Bipedal Navigation System initialized')

    def goal_callback(self, goal_msg):
        """Handle navigation goal"""
        self.get_logger().info(f'Received goal: ({goal_msg.pose.position.x}, {goal_msg.pose.position.y})')

        # Plan path considering bipedal constraints
        path = self.plan_bipedal_path(goal_msg.pose)

        if path:
            self.execute_path(path)
        else:
            self.get_logger().error('Failed to plan path')

    def plan_bipedal_path(self, goal_pose):
        """Plan path with bipedal constraints"""
        # This would integrate with Nav2 but considering step constraints
        # For now, return a simple path
        path = Path()
        path.header.frame_id = 'map'

        # In practice, this would use a step-aware planner
        # that considers foot placement locations
        return path

    def execute_path(self, path):
        """Execute the planned path with bipedal gait"""
        self.navigation_state = 'EXECUTING'
        self.publish_navigation_state()

        # Convert path to footstep plan
        footsteps = self.path_to_footsteps(path)

        # Execute footsteps with appropriate gait
        self.execute_footsteps(footsteps)

    def path_to_footsteps(self, path):
        """Convert continuous path to discrete footsteps"""
        # This is a simplified version
        # In reality, this would use sophisticated footstep planning
        footsteps = []

        for i, pose in enumerate(path.poses):
            if i % 2 == 0:  # Alternate between left and right foot
                footstep = {
                    'position': (pose.pose.position.x, pose.pose.position.y),
                    'orientation': pose.pose.orientation,
                    'foot': 'left' if i % 4 == 0 else 'right',
                    'step_type': 'normal'  # normal, step_up, step_down
                }
                footsteps.append(footstep)

        return footsteps

    def execute_footsteps(self, footsteps):
        """Execute the planned footsteps"""
        for i, footstep in enumerate(footsteps):
            self.get_logger().info(f'Executing footstep {i+1}/{len(footsteps)}')

            # Determine appropriate gait based on terrain
            gait = self.select_gait(footstep)
            self.publish_gait_command(gait)

            # Move to footstep position
            self.move_to_footstep(footstep)

            # Wait for completion
            self.wait_for_completion()

    def select_gait(self, footstep):
        """Select appropriate gait for the footstep"""
        # Analyze terrain and select gait
        if footstep['step_type'] == 'step_up':
            return 'STEP_UP'
        elif footstep['step_type'] == 'step_down':
            return 'STEP_DOWN'
        else:
            return 'WALKING'

    def move_to_footstep(self, footstep):
        """Move robot to the specified footstep"""
        # This would interface with the robot's walking controller
        cmd_vel = Twist()
        # Calculate movement to reach footstep position
        self.cmd_vel_pub.publish(cmd_vel)

    def publish_navigation_state(self):
        """Publish current navigation state"""
        state_msg = String()
        state_msg.data = self.navigation_state
        self.navigation_state_pub.publish(state_msg)

    def publish_gait_command(self, gait):
        """Publish gait command"""
        gait_msg = String()
        gait_msg.data = gait
        self.gait_cmd_pub.publish(gait_msg)

    def wait_for_completion(self):
        """Wait for current action to complete"""
        # In practice, this would monitor robot state
        import time
        time.sleep(1.0)  # Placeholder

def main(args=None):
    rclpy.init(args=args)
    nav_system = BipedalNavigationSystem()

    try:
        rclpy.spin(nav_system)
    except KeyboardInterrupt:
        pass
    finally:
        nav_system.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Footstep Planning for Humanoids

### Basic Footstep Planner
```python
# footstep_planner.py - Basic footstep planning for bipedal robots
import numpy as np
from scipy.spatial import KDTree
import math

class FootstepPlanner:
    def __init__(self):
        # Bipedal parameters
        self.step_size = 0.3  # Maximum distance between footsteps
        self.step_width = 0.25  # Distance between left and right footsteps
        self.max_step_height = 0.15  # Maximum step up height
        self.max_step_down = 0.1    # Maximum step down height
        self.support_polygon = 0.1  # Support polygon radius for stability

        # Footstep pattern (left, right alternating)
        self.foot_sequence = ['left', 'right'] * 10  # Predefined sequence

    def plan_footsteps(self, path, start_pose):
        """Plan footsteps along a given path"""
        footsteps = []

        # Start with current pose
        current_pos = np.array([start_pose.position.x, start_pose.position.y])
        current_yaw = self.quaternion_to_yaw(start_pose.orientation)

        # Determine starting foot based on path direction
        first_foot = self.determine_starting_foot(path, current_yaw)

        for i, waypoint in enumerate(path.poses):
            target_pos = np.array([waypoint.pose.position.x, waypoint.pose.position.y])

            # Calculate direction to next waypoint
            direction = target_pos - current_pos
            distance = np.linalg.norm(direction)

            if distance > self.step_size:
                # Need to take steps toward this waypoint
                num_steps = int(distance / self.step_size) + 1

                for j in range(num_steps):
                    step_pos = current_pos + (direction / distance) * self.step_size * (j + 1)

                    # Alternate feet
                    foot = self.foot_sequence[len(footsteps) % len(self.foot_sequence)]

                    # Adjust for step width (stagger feet for stability)
                    if foot == 'left':
                        step_pos[1] += self.step_width / 2
                    else:
                        step_pos[1] -= self.step_width / 2

                    footstep = {
                        'position': step_pos,
                        'yaw': current_yaw,
                        'foot': foot,
                        'step_type': self.classify_step_type(step_pos, target_pos)
                    }

                    footsteps.append(footstep)
                    current_pos = step_pos

        return footsteps

    def determine_starting_foot(self, path, current_yaw):
        """Determine which foot to start with based on path direction"""
        if len(path.poses) > 1:
            first_waypoint = np.array([path.poses[0].pose.position.x,
                                     path.poses[0].pose.position.y])
            second_waypoint = np.array([path.poses[1].pose.position.x,
                                      path.poses[1].pose.position.y])

            path_direction = second_waypoint - first_waypoint
            path_yaw = math.atan2(path_direction[1], path_direction[0])

            # Simple heuristic: start with right foot if turning right, left if turning left
            yaw_diff = path_yaw - current_yaw
            if abs(yaw_diff) < math.pi/4:  # Going straight
                return 'right'  # Start with right foot
            elif yaw_diff > 0:  # Turning left
                return 'left'
            else:  # Turning right
                return 'right'

        return 'right'  # Default

    def classify_step_type(self, step_pos, target_pos):
        """Classify the type of step based on terrain analysis"""
        # This would analyze elevation data from map
        # For now, return 'normal'
        return 'normal'

    def quaternion_to_yaw(self, quaternion):
        """Convert quaternion to yaw angle"""
        siny_cosp = 2 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y)
        cosy_cosp = 1 - 2 * (quaternion.y * quaternion.y + quaternion.z * quaternion.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def validate_footstep(self, footstep, map_data):
        """Validate that a footstep is safe and stable"""
        # Check if position is in free space
        if not self.is_free_space(footstep['position'], map_data):
            return False, "Position occupied"

        # Check if step is within bounds
        if not self.is_step_feasible(footstep):
            return False, "Step not feasible"

        # Check stability with previous steps
        if not self.is_stable(footstep):
            return False, "Would cause instability"

        return True, "Valid"

    def is_free_space(self, position, map_data):
        """Check if position is in free space on the map"""
        # This would check the costmap
        return True  # Placeholder

    def is_step_feasible(self, footstep):
        """Check if the step is physically feasible"""
        # Check step size limits
        return True  # Placeholder

    def is_stable(self, footstep):
        """Check if the footstep maintains stability"""
        # Check support polygon
        return True  # Placeholder
```

## Gait-Based Controllers

### Gait Manager Node
```python
# gait_manager.py - Gait management for bipedal navigation
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration
import numpy as np

class GaitManager(Node):
    def __init__(self):
        super().__init__('gait_manager')

        # Current gait state
        self.current_gait = 'STANDING'
        self.gait_parameters = {}

        # Publishers
        self.joint_cmd_pub = self.create_publisher(JointState, 'joint_commands', 10)
        self.balance_cmd_pub = self.create_publisher(Twist, 'balance_commands', 10)

        # Subscribers
        self.gait_cmd_sub = self.create_subscription(
            String, 'gait_command', self.gait_command_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10
        )

        # Define gait parameters
        self.gait_configs = {
            'WALKING': {
                'step_frequency': 2.0,
                'step_length': 0.3,
                'step_height': 0.05,
                'stance_width': 0.25,
                'max_speed': 0.5
            },
            'STEPPING': {
                'step_frequency': 1.0,
                'step_length': 0.2,
                'step_height': 0.1,
                'stance_width': 0.25,
                'max_speed': 0.2
            },
            'CLIMBING': {
                'step_frequency': 0.5,
                'step_length': 0.15,
                'step_height': 0.15,
                'stance_width': 0.3,
                'max_speed': 0.1
            },
            'RUNNING': {
                'step_frequency': 3.0,
                'step_length': 0.4,
                'step_height': 0.08,
                'stance_width': 0.2,
                'max_speed': 1.0
            }
        }

        # Initialize gait
        self.set_gait('WALKING')

    def gait_command_callback(self, msg):
        """Handle gait command"""
        new_gait = msg.data.upper()
        if new_gait in self.gait_configs:
            self.set_gait(new_gait)
        else:
            self.get_logger().warn(f'Unknown gait: {new_gait}')

    def set_gait(self, gait_name):
        """Set the current gait"""
        if gait_name in self.gait_configs:
            self.current_gait = gait_name
            self.gait_parameters = self.gait_configs[gait_name]
            self.get_logger().info(f'Switched to {gait_name} gait')

            # Update controller parameters
            self.update_controller_parameters()
        else:
            self.get_logger().error(f'Invalid gait: {gait_name}')

    def update_controller_parameters(self):
        """Update controller with new gait parameters"""
        # This would update the walking controller with new parameters
        # such as step frequency, height, length, etc.
        pass

    def generate_walking_pattern(self, velocity_cmd):
        """Generate walking joint commands based on velocity"""
        if self.current_gait == 'WALKING':
            return self.generate_walking_joints(velocity_cmd)
        elif self.current_gait == 'STEPPING':
            return self.generate_stepping_joints(velocity_cmd)
        elif self.current_gait == 'CLIMBING':
            return self.generate_climbing_joints(velocity_cmd)
        else:
            return self.generate_standing_joints()

    def generate_walking_joints(self, velocity_cmd):
        """Generate joint commands for walking gait"""
        # Calculate walking pattern based on desired velocity
        step_freq = self.gait_parameters['step_frequency']
        step_length = self.gait_parameters['step_length'] * velocity_cmd.linear.x

        # Simplified walking pattern
        joint_state = JointState()
        joint_state.name = ['left_hip', 'right_hip', 'left_knee', 'right_knee',
                           'left_ankle', 'right_ankle']
        joint_state.position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Placeholder

        # In practice, this would generate proper walking trajectories
        # using inverse kinematics and gait timing

        return joint_state

    def generate_stepping_joints(self, velocity_cmd):
        """Generate joint commands for stepping gait"""
        # For stepping over obstacles
        joint_state = JointState()
        # Specific stepping pattern
        return joint_state

    def generate_climbing_joints(self, velocity_cmd):
        """Generate joint commands for climbing gait"""
        # For climbing stairs or obstacles
        joint_state = JointState()
        # Specific climbing pattern
        return joint_state

    def generate_standing_joints(self):
        """Generate joint commands for standing position"""
        joint_state = JointState()
        # Zero or neutral position
        return joint_state

    def balance_control(self, current_state):
        """Generate balance control commands"""
        balance_cmd = Twist()

        # Simple balance control based on IMU or ZMP (Zero Moment Point)
        # This would interface with balance control algorithms

        return balance_cmd

def main(args=None):
    rclpy.init(args=args)
    gait_manager = GaitManager()

    try:
        rclpy.spin(gait_manager)
    except KeyboardInterrupt:
        pass
    finally:
        gait_manager.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Nav2 Configuration for Bipedal Robots

### Custom Bipedal Planner
```python
# bipedal_planner.py - Custom Nav2 planner for bipedal robots
import rclpy
from rclpy.node import Node
from nav2_core.planner import Planner
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path
from builtin_interfaces.msg import Duration
import numpy as np

class BipedalPlanner(Planner):
    def __init__(self):
        super().__init__('bipedal_planner')
        self.costmap_ros = None
        self.global_frame = 'map'
        self.robot_base_frame = 'base_link'

        # Bipedal-specific parameters
        self.step_size = 0.3  # Maximum step size
        self.support_polygon_radius = 0.1  # For balance
        self.footprint_buffer = 0.05  # Additional safety buffer

    def configure(self, tf_buffer, costmap_ros, autostart):
        """Configure the planner"""
        self.costmap_ros = costmap_ros
        self.tf_buffer = tf_buffer
        self.local_costmap = costmap_ros.get_costmap()
        self.global_frame = self.local_costmap.getGlobalFrameID()

        # Get bipedal parameters
        self.declare_parameter('step_size', 0.3)
        self.declare_parameter('support_polygon_radius', 0.1)
        self.declare_parameter('footprint_buffer', 0.05)

        self.step_size = self.get_parameter('step_size').value
        self.support_polygon_radius = self.get_parameter('support_polygon_radius').value
        self.footprint_buffer = self.get_parameter('footprint_buffer').value

        self.get_logger().info(f'Bipedal planner configured with step_size: {self.step_size}')

    def cleanup(self):
        """Cleanup the planner"""
        self.get_logger().info('Bipedal planner cleaned up')

    def setPlan(self, path):
        """Set the global plan (if needed)"""
        self.get_logger().info(f'Set plan with {len(path.poses)} poses')

    def createPlan(self, start, goal):
        """Create a plan from start to goal considering bipedal constraints"""
        self.get_logger().info(f'Creating bipedal plan from ({start.pose.position.x}, {start.pose.position.y}) to ({goal.pose.position.x}, {goal.pose.position.y})')

        # Create result path
        plan = Path()
        plan.header.frame_id = self.global_frame
        plan.header.stamp = self.get_clock().now().to_msg()

        # Simple RRT-based approach for bipedal planning
        # In practice, this would use more sophisticated footstep planning
        current_pos = np.array([start.pose.position.x, start.pose.position.y])
        goal_pos = np.array([goal.pose.position.x, goal.pose.position.y])

        # Plan footsteps
        footsteps = self.plan_footsteps_rrt(current_pos, goal_pos)

        # Convert to Path message
        for footstep in footsteps:
            pose = PoseStamped()
            pose.header.frame_id = self.global_frame
            pose.pose.position.x = footstep[0]
            pose.pose.position.y = footstep[1]
            pose.pose.position.z = 0.0  # Ground level
            # Set orientation to face next step
            if len(footsteps) > 1:
                next_idx = min(len(footsteps) - 1, footsteps.index(footstep) + 1)
                dx = footsteps[next_idx][0] - footstep[0]
                dy = footsteps[next_idx][1] - footstep[1]
                yaw = np.arctan2(dy, dx)
                pose.pose.orientation.z = np.sin(yaw/2)
                pose.pose.orientation.w = np.cos(yaw/2)

            plan.poses.append(pose)

        return plan

    def plan_footsteps_rrt(self, start_pos, goal_pos):
        """Plan footsteps using RRT adapted for bipedal constraints"""
        footsteps = [start_pos]

        current_pos = start_pos.copy()
        max_iterations = 1000
        goal_tolerance = 0.2

        for i in range(max_iterations):
            # Check if close enough to goal
            if np.linalg.norm(current_pos - goal_pos) < goal_tolerance:
                footsteps.append(goal_pos)
                break

            # Sample random point near goal with bias
            if np.random.random() < 0.3:  # 30% chance to sample near goal
                rand_pos = goal_pos + np.random.uniform(-0.5, 0.5, 2)
            else:
                rand_pos = np.random.uniform(-10, 10, 2)  # Expand search area

            # Find nearest footstep in tree
            nearest_idx = self.find_nearest(footsteps, rand_pos)
            nearest_pos = footsteps[nearest_idx]

            # Create new step in direction of random point
            direction = rand_pos - nearest_pos
            direction = direction / np.linalg.norm(direction)  # Normalize
            new_pos = nearest_pos + direction * self.step_size

            # Check if new position is valid
            if self.is_valid_footstep(new_pos):
                footsteps.append(new_pos)
                current_pos = new_pos

        return footsteps

    def find_nearest(self, footsteps, target_pos):
        """Find the nearest footstep to target position"""
        min_dist = float('inf')
        nearest_idx = 0

        for i, pos in enumerate(footsteps):
            dist = np.linalg.norm(pos - target_pos)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def is_valid_footstep(self, pos):
        """Check if a footstep position is valid"""
        # Check costmap for obstacles
        costmap = self.costmap_ros.get_costmap()

        # Convert world coordinates to costmap coordinates
        map_x, map_y = costmap.worldToMap(float(pos[0]), float(pos[1]))

        # Check if within bounds
        if map_x < 0 or map_x >= costmap.getSizeInCellsX() or \
           map_y < 0 or map_y >= costmap.getSizeInCellsY():
            return False

        # Check cost (should be free space)
        cost = costmap.getCost(map_x, map_y)
        if cost >= 253:  # Consider lethal obstacles and inscribed obstacles
            return False

        # Additional bipedal checks could go here
        # - slope analysis
        # - step height constraints
        # - balance polygon checks

        return True

def main(args=None):
    rclpy.init(args=args)
    planner = BipedalPlanner()

    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    finally:
        planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Balance and Stability Control

### Balance Controller Node
```python
# balance_controller.py - Balance control for bipedal navigation
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float32
import numpy as np

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # Balance state
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.linear_vel = Vector3()
        self.angular_vel = Vector3()

        # Balance control parameters
        self.kp_roll = 50.0   # Proportional gain for roll
        self.ki_roll = 10.0   # Integral gain for roll
        self.kd_roll = 5.0    # Derivative gain for roll

        self.kp_pitch = 50.0  # Proportional gain for pitch
        self.ki_pitch = 10.0  # Integral gain for pitch
        self.kd_pitch = 5.0   # Derivative gain for pitch

        # Integral terms
        self.roll_integral = 0.0
        self.pitch_integral = 0.0
        self.roll_prev_error = 0.0
        self.pitch_prev_error = 0.0

        # Publishers
        self.balance_cmd_pub = self.create_publisher(Twist, 'balance_cmd', 10)
        self.joint_cmd_pub = self.create_publisher(JointState, 'balance_joint_cmd', 10)

        # Subscribers
        self.imu_sub = self.create_subscription(Imu, 'imu/data', self.imu_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        # Balance control timer
        self.balance_timer = self.create_timer(0.01, self.balance_control_loop)  # 100Hz

    def imu_callback(self, msg):
        """Process IMU data for balance"""
        # Extract orientation from quaternion
        quat = msg.orientation
        self.roll, self.pitch, self.yaw = self.quaternion_to_rpy(quat)

        # Extract angular velocities
        self.angular_vel = msg.angular_velocity

    def odom_callback(self, msg):
        """Process odometry for balance"""
        self.linear_vel = msg.twist.twist.linear

    def balance_control_loop(self):
        """Main balance control loop"""
        # Calculate errors (target is zero for upright position)
        roll_error = 0.0 - self.roll  # Target roll = 0
        pitch_error = 0.0 - self.pitch  # Target pitch = 0

        # Update integral terms
        self.roll_integral += roll_error * 0.01  # dt = 0.01s
        self.pitch_integral += pitch_error * 0.01

        # Calculate derivatives
        roll_derivative = (roll_error - self.roll_prev_error) / 0.01
        pitch_derivative = (pitch_error - self.pitch_prev_error) / 0.01

        # Calculate control outputs
        roll_control = (self.kp_roll * roll_error +
                       self.ki_roll * self.roll_integral +
                       self.kd_roll * roll_derivative)

        pitch_control = (self.kp_pitch * pitch_error +
                        self.ki_pitch * self.pitch_integral +
                        self.kd_pitch * pitch_derivative)

        # Apply saturation limits
        roll_control = max(-1.0, min(1.0, roll_control))
        pitch_control = max(-1.0, min(1.0, pitch_control))

        # Create balance command
        balance_cmd = Twist()
        balance_cmd.angular.x = pitch_control  # Forward/back balance
        balance_cmd.angular.y = -roll_control  # Left/right balance
        balance_cmd.angular.z = 0.0  # Yaw control separate

        # Publish balance command
        self.balance_cmd_pub.publish(balance_cmd)

        # Generate joint commands for active balance
        joint_cmd = self.generate_balance_joints(roll_control, pitch_control)
        self.joint_cmd_pub.publish(joint_cmd)

        # Update previous errors
        self.roll_prev_error = roll_error
        self.pitch_prev_error = pitch_error

    def generate_balance_joints(self, roll_control, pitch_control):
        """Generate joint commands for balance correction"""
        joint_state = JointState()
        joint_state.name = ['left_hip_roll', 'right_hip_roll',
                           'left_hip_pitch', 'right_hip_pitch',
                           'left_ankle_roll', 'right_ankle_roll',
                           'left_ankle_pitch', 'right_ankle_pitch']

        # Calculate joint adjustments based on balance control
        adjustments = np.zeros(8)

        # Roll balance: adjust hip and ankle roll joints
        adjustments[0] = -roll_control * 0.1  # Left hip roll
        adjustments[1] = roll_control * 0.1   # Right hip roll
        adjustments[4] = -roll_control * 0.05 # Left ankle roll
        adjustments[5] = roll_control * 0.05  # Right ankle roll

        # Pitch balance: adjust hip and ankle pitch joints
        adjustments[2] = pitch_control * 0.05  # Left hip pitch
        adjustments[3] = pitch_control * 0.05  # Right hip pitch
        adjustments[6] = pitch_control * 0.02  # Left ankle pitch
        adjustments[7] = pitch_control * 0.02  # Right ankle pitch

        joint_state.position = adjustments.tolist()

        return joint_state

    def quaternion_to_rpy(self, quaternion):
        """Convert quaternion to roll, pitch, yaw"""
        import math

        q = quaternion
        sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (q.w * q.y - q.z * q.x)
        pitch = math.asin(sinp)

        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

def main(args=None):
    rclpy.init(args=args)
    balance_controller = BalanceController()

    try:
        rclpy.spin(balance_controller)
    except KeyboardInterrupt:
        pass
    finally:
        balance_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Terrain Adaptation and Step Planning

### Adaptive Step Planner
```python
# adaptive_step_planner.py - Adaptive step planning for various terrains
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32MultiArray
import numpy as np
import sensor_msgs.point_cloud2 as pc2

class AdaptiveStepPlanner(Node):
    def __init__(self):
        super().__init__('adaptive_step_planner')

        # Terrain classification
        self.terrain_types = {
            'FLAT': {'step_height': 0.02, 'friction': 0.8, 'max_incline': 0.1},
            'ROUGH': {'step_height': 0.05, 'friction': 0.6, 'max_incline': 0.2},
            'STAIRS': {'step_height': 0.15, 'friction': 0.9, 'max_incline': 0.5},
            'SLOPE': {'step_height': 0.03, 'friction': 0.7, 'max_incline': 0.3}
        }

        # Publishers
        self.terrain_map_pub = self.create_publisher(Float32MultiArray, 'terrain_map', 10)
        self.adapted_path_pub = self.create_publisher(PoseStamped, 'adapted_path', 10)

        # Subscribers
        self.pointcloud_sub = self.create_subscription(
            PointCloud2, 'points2', self.pointcloud_callback, 10
        )
        self.scan_sub = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10
        )

    def pointcloud_callback(self, msg):
        """Process point cloud for terrain analysis"""
        # Convert point cloud to numpy array
        points = []
        for point in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            points.append([point[0], point[1], point[2]])

        points = np.array(points)

        if len(points) > 0:
            # Analyze terrain characteristics
            terrain_analysis = self.analyze_terrain(points)

            # Publish terrain map
            terrain_msg = Float32MultiArray()
            terrain_msg.data = [terrain_analysis['type'],
                               terrain_analysis['roughness'],
                               terrain_analysis['slope']]
            self.terrain_map_pub.publish(terrain_msg)

    def scan_callback(self, msg):
        """Process laser scan for obstacle detection"""
        # Analyze scan data for step planning
        valid_steps = self.find_valid_steps(msg)

        # For now, just log the findings
        self.get_logger().info(f'Found {len(valid_steps)} valid steps')

    def analyze_terrain(self, points):
        """Analyze terrain from point cloud data"""
        if len(points) < 3:
            return {'type': 'FLAT', 'roughness': 0.0, 'slope': 0.0}

        # Calculate surface normal (simplified)
        # This is a basic approach - in practice, use more sophisticated methods
        z_values = points[:, 2]
        roughness = np.std(z_values)

        # Determine terrain type based on roughness and other factors
        if roughness < 0.02:
            terrain_type = 'FLAT'
        elif roughness < 0.05:
            terrain_type = 'ROUGH'
        else:
            terrain_type = 'ROUGH'  # Very rough terrain

        # Calculate approximate slope
        if len(points) >= 3:
            # Fit a plane to the points to get slope
            # This is a simplified approach
            z_mean = np.mean(z_values)
            slope = abs(np.max(z_values) - np.min(z_values)) / len(z_values)
        else:
            slope = 0.0

        return {
            'type': terrain_type,
            'roughness': roughness,
            'slope': slope
        }

    def find_valid_steps(self, scan_msg):
        """Find valid step locations from laser scan"""
        valid_steps = []

        # Convert scan to usable format
        ranges = np.array(scan_msg.ranges)
        angles = np.linspace(scan_msg.angle_min, scan_msg.angle_max, len(ranges))

        # Find gaps in scan that could be step locations
        for i in range(len(ranges) - 1):
            if ranges[i] < scan_msg.range_max and ranges[i+1] < scan_msg.range_max:
                # Check if there's a significant gap (possible step down)
                range_diff = abs(ranges[i] - ranges[i+1])
                if range_diff > 0.1:  # Potential step
                    angle = angles[i]
                    x = ranges[i] * np.cos(angle)
                    y = ranges[i] * np.sin(angle)

                    # Validate step based on robot constraints
                    if self.is_valid_step(x, y, range_diff):
                        valid_steps.append((x, y, range_diff))

        return valid_steps

    def is_valid_step(self, x, y, height_diff):
        """Check if a potential step is valid for the robot"""
        # Check height constraints
        max_step_up = 0.15
        max_step_down = 0.10

        if abs(height_diff) > max(abs(max_step_up), abs(max_step_down)):
            return False

        # Check for obstacles in the step area
        # This would involve checking costmap or additional sensors

        return True

def main(args=None):
    rclpy.init(args=args)
    step_planner = AdaptiveStepPlanner()

    try:
        rclpy.spin(step_planner)
    except KeyboardInterrupt:
        pass
    finally:
        step_planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Exercise

### Exercise 1: Bipedal Navigation Setup
1. Configure Nav2 with bipedal-specific parameters
2. Implement basic footstep planning
3. Test navigation in a simple environment
4. Evaluate path execution and balance maintenance

### Exercise 2: Gait Control Implementation
1. Create a gait manager node
2. Implement different walking patterns (walking, stepping, climbing)
3. Test gait transitions during navigation
4. Evaluate gait stability and efficiency

### Exercise 3: Balance Control
1. Implement balance controller using IMU feedback
2. Test balance recovery during navigation
3. Evaluate performance on different terrains
4. Tune PID parameters for optimal balance

## Advanced Topics

### Dynamic Walking Control
For more advanced bipedal navigation, consider:

1. **ZMP (Zero Moment Point) Control**: For stable walking dynamics
2. **Preview Control**: Using future path information for smoother walking
3. **Online Footstep Planning**: Real-time adjustment of footsteps based on sensor feedback
4. **Learning-based Approaches**: Using reinforcement learning for gait optimization

### Integration with Isaac ROS
```python
# isaac_ros_integration.py - Integrating with Isaac ROS perception
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import PoseStamped
from vision_msgs.msg import Detection2DArray
from std_msgs.msg import String

class IsaacROSIntegration(Node):
    def __init__(self):
        super().__init__('isaac_ros_integration')

        # Subscribe to Isaac ROS perception outputs
        self.detection_sub = self.create_subscription(
            Detection2DArray, 'isaac_ros/detections', self.detection_callback, 10
        )
        self.depth_sub = self.create_subscription(
            PointCloud2, 'isaac_ros/depth', self.depth_callback, 10
        )

    def detection_callback(self, msg):
        """Process object detections from Isaac ROS"""
        for detection in msg.detections:
            # Check if detection affects navigation
            if detection.results[0].hypothesis.class_id in ['obstacle', 'step', 'stair']:
                self.update_navigation_plan(detection)

    def depth_callback(self, msg):
        """Process depth information for terrain analysis"""
        # Use Isaac ROS depth data for more accurate terrain assessment
        # This could improve footstep planning accuracy
        pass

def main(args=None):
    rclpy.init(args=args)
    integration = IsaacROSIntegration()

    try:
        rclpy.spin(integration)
    except KeyboardInterrupt:
        pass
    finally:
        integration.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

This week covered Nav2 for bipedal movement:
- Bipedal-specific navigation architecture and challenges
- Footstep planning algorithms for humanoid robots
- Gait-based controllers and management
- Balance and stability control systems
- Terrain adaptation and step planning
- Integration with perception systems

## Next Week Preview

Module 4 begins with Week 11: Voice Commands with OpenAI Whisper, where you'll learn to implement speech recognition systems for humanoid robot control using advanced AI models.