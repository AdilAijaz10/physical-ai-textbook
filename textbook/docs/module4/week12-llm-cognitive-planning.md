---
sidebar_position: 2
---

# Week 12: LLM Cognitive Planning

## Learning Objectives

By the end of this week, you will be able to:
- Integrate large language models (LLMs) with humanoid robot systems
- Implement cognitive planning using LLMs for task decomposition
- Create reasoning systems that can adapt to dynamic environments
- Design multimodal interfaces combining vision, language, and action
- Evaluate and validate LLM-based planning decisions

## Introduction to LLM Cognitive Planning

Large Language Models (LLMs) have emerged as powerful tools for cognitive planning in robotics. Unlike traditional planning algorithms that rely on predefined rules and state spaces, LLMs can reason about complex, natural language instructions and generate flexible, context-aware plans for humanoid robots.

### Key Benefits of LLM Cognitive Planning
- **Natural Language Understanding**: Interpret complex human instructions
- **Common Sense Reasoning**: Apply general knowledge to robot tasks
- **Adaptive Planning**: Adjust plans based on changing environments
- **Task Decomposition**: Break complex tasks into executable subtasks
- **Learning from Interaction**: Improve planning through experience

## Setting Up LLM Integration

### Prerequisites and Installation
```bash
# Install required packages
pip install openai  # For OpenAI models
pip install transformers  # For local models
pip install torch  # For PyTorch models
pip install rclpy  # For ROS 2 integration
pip install langchain  # For LLM orchestration
pip install tiktoken  # For token counting
```

### Basic LLM Interface
```python
# llm_interface.py - Basic LLM interface for robotics
import openai
import json
import time
from typing import Dict, List, Any, Optional
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose

class LLMInterface:
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        if api_key:
            openai.api_key = api_key
        self.model = model
        self.conversation_history = []

    def query(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Query the LLM with a prompt"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error querying LLM: {e}")
            return "Error: Could not process request"

    def get_system_prompt(self) -> str:
        """Get system prompt for robotics context"""
        return """
        You are an AI assistant helping a humanoid robot plan and execute tasks.
        The robot has capabilities like moving, grasping objects, navigating spaces,
        and interacting with people. Respond with clear, executable plans or
        explanations that the robot can understand and act upon. Be specific about
        locations, objects, and actions. Consider safety and feasibility.
        """

class LLMCognitivePlanner(Node):
    def __init__(self):
        super().__init__('llm_cognitive_planner')

        # Initialize LLM interface
        self.llm = LLMInterface(api_key="your-api-key-here")  # Replace with actual key

        # Publishers and subscribers
        self.plan_pub = self.create_publisher(String, 'cognitive_plan', 10)
        self.task_sub = self.create_subscription(
            String, 'high_level_task', self.task_callback, 10
        )
        self.perception_sub = self.create_subscription(
            String, 'perception_data', self.perception_callback, 10
        )

        # Internal state
        self.current_plan = []
        self.robot_capabilities = [
            'move_forward', 'move_backward', 'turn_left', 'turn_right',
            'grasp_object', 'release_object', 'navigate_to', 'detect_object',
            'wave', 'speak', 'listen'
        ]
        self.environment_state = {}

        self.get_logger().info('LLM Cognitive Planner initialized')

    def task_callback(self, msg):
        """Handle high-level tasks from user or other systems"""
        task_description = msg.data
        self.get_logger().info(f'Received task: {task_description}')

        # Generate plan using LLM
        plan = self.generate_plan(task_description)

        if plan:
            self.current_plan = plan
            self.execute_plan(plan)

    def perception_callback(self, msg):
        """Update environment state with perception data"""
        try:
            perception_data = json.loads(msg.data)
            self.environment_state.update(perception_data)
            self.get_logger().info(f'Updated environment state: {perception_data}')
        except json.JSONDecodeError:
            self.get_logger().warn('Could not parse perception data as JSON')

    def generate_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate a plan using LLM cognitive reasoning"""
        # Create context for the LLM
        context = self.build_context(task_description)

        # Create prompt for planning
        prompt = f"""
        Task: {task_description}

        Current environment state: {self.environment_state}
        Robot capabilities: {self.robot_capabilities}

        Please create a detailed step-by-step plan to accomplish this task.
        Each step should be a specific action that the robot can execute.
        Format each step as: ACTION: [action_name], PARAMETERS: {{param1: value1, ...}}

        Return the plan as a JSON list of steps.
        """

        try:
            response = self.llm.query(prompt, max_tokens=1500, temperature=0.2)

            # Parse the response
            plan = self.parse_plan_response(response)
            return plan

        except Exception as e:
            self.get_logger().error(f'Error generating plan: {e}')
            return []

    def build_context(self, task_description: str) -> Dict[str, Any]:
        """Build context for the LLM"""
        return {
            'task': task_description,
            'environment': self.environment_state,
            'capabilities': self.robot_capabilities,
            'current_plan': self.current_plan
        }

    def parse_plan_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into executable plan"""
        # Try to parse as JSON first
        try:
            # Look for JSON in the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1

            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                plan = json.loads(json_str)
                return plan
        except json.JSONDecodeError:
            pass

        # If not JSON, try to parse as structured text
        plan = []
        lines = response.split('\n')

        for line in lines:
            if 'ACTION:' in line.upper():
                # Parse action and parameters
                action_part = line.split('ACTION:')[1].split(',')[0].strip()
                param_part = ''

                if 'PARAMETERS:' in line:
                    param_part = line.split('PARAMETERS:')[1].strip()

                try:
                    params = json.loads(param_part) if param_part else {}
                    plan.append({
                        'action': action_part,
                        'parameters': params
                    })
                except json.JSONDecodeError:
                    plan.append({
                        'action': action_part,
                        'parameters': {}
                    })

        return plan

    def execute_plan(self, plan: List[Dict[str, Any]]):
        """Execute the generated plan"""
        self.get_logger().info(f'Executing plan with {len(plan)} steps')

        for i, step in enumerate(plan):
            self.get_logger().info(f'Step {i+1}/{len(plan)}: {step["action"]}')

            # Publish step for execution by other nodes
            step_msg = String()
            step_msg.data = json.dumps(step)
            self.plan_pub.publish(step_msg)

            # Wait for step completion (simplified)
            time.sleep(1)  # In practice, wait for feedback from executor

def main(args=None):
    rclpy.init(args=args)
    planner = LLMCognitivePlanner()

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

## Task Decomposition and Reasoning

### Hierarchical Task Planning
```python
# hierarchical_planning.py - Hierarchical task decomposition
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Task:
    id: str
    description: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    subtasks: List['Task'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, executing, completed, failed

class HierarchicalPlanner:
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0

    def decompose_task(self, description: str, llm_interface: LLMInterface) -> Task:
        """Decompose high-level task into subtasks using LLM"""
        prompt = f"""
        Decompose the following task into smaller, executable subtasks:
        Task: {description}

        Consider the following when decomposing:
        1. Each subtask should be atomic (cannot be further decomposed)
        2. Subtasks should follow logical order
        3. Identify dependencies between subtasks
        4. Consider what information each subtask needs from previous ones

        Return the task decomposition as a JSON object with:
        - main_task: the original task
        - subtasks: array of subtasks with id, description, action, parameters, dependencies
        """

        response = llm_interface.query(prompt, max_tokens=2000, temperature=0.1)

        try:
            result = json.loads(response)
            main_task = self.create_task_from_dict(result['main_task'])

            for subtask_data in result['subtasks']:
                subtask = self.create_task_from_dict(subtask_data)
                main_task.subtasks.append(subtask)
                self.tasks[subtask.id] = subtask

            self.tasks[main_task.id] = main_task
            return main_task

        except json.JSONDecodeError:
            # Fallback: create simple task if parsing fails
            task_id = f"task_{self.task_counter}"
            self.task_counter += 1
            return Task(id=task_id, description=description, action="execute")

    def create_task_from_dict(self, task_data: Dict[str, Any]) -> Task:
        """Create Task object from dictionary data"""
        return Task(
            id=task_data.get('id', f"task_{self.task_counter}"),
            description=task_data.get('description', ''),
            action=task_data.get('action', 'execute'),
            parameters=task_data.get('parameters', {}),
            dependencies=task_data.get('dependencies', []),
            status='pending'
        )

    def get_executable_tasks(self) -> List[Task]:
        """Get tasks that can be executed (dependencies satisfied)"""
        executable = []

        for task_id, task in self.tasks.items():
            if task.status == 'pending':
                # Check if all dependencies are completed
                deps_satisfied = True
                for dep_id in task.dependencies:
                    if dep_id in self.tasks:
                        if self.tasks[dep_id].status != 'completed':
                            deps_satisfied = False
                            break

                if deps_satisfied:
                    executable.append(task)

        return executable

    def update_task_status(self, task_id: str, status: str):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status

class LLMHierarchicalPlanner(LLMCognitivePlanner):
    def __init__(self):
        super().__init__()
        self.hierarchical_planner = HierarchicalPlanner()

        # Additional publisher for task status
        self.task_status_pub = self.create_publisher(String, 'task_status', 10)

    def generate_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate hierarchical plan using LLM"""
        # Decompose task hierarchically
        main_task = self.hierarchical_planner.decompose_task(
            task_description, self.llm
        )

        # Convert to flat execution plan
        execution_plan = self.flatten_task(main_task)

        # Publish plan structure for monitoring
        plan_msg = String()
        plan_msg.data = json.dumps({
            'main_task': main_task.id,
            'subtasks': [t.id for t in main_task.subtasks],
            'description': main_task.description
        })
        self.plan_pub.publish(plan_msg)

        return execution_plan

    def flatten_task(self, task: Task) -> List[Dict[str, Any]]:
        """Flatten hierarchical task to execution steps"""
        steps = []

        for subtask in task.subtasks:
            steps.append({
                'id': subtask.id,
                'action': subtask.action,
                'parameters': subtask.parameters,
                'description': subtask.description
            })

        return steps
```

## Multimodal Reasoning

### Vision-Language Integration
```python
# multimodal_reasoning.py - Vision-language integration for LLM planning
import base64
from io import BytesIO
import numpy as np
from PIL import Image
import requests
from typing import List, Dict, Any

class MultimodalCognitivePlanner(LLMHierarchicalPlanner):
    def __init__(self):
        super().__init__()

        # Subscribe to image topics
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )

        # Store recent images for multimodal queries
        self.recent_images = []
        self.max_images = 5

        # Vision-specific LLM interface (for models that support images)
        self.vision_llm = None  # Will be set up if using vision-capable model

    def image_callback(self, msg):
        """Handle incoming image data"""
        # Convert ROS Image to format suitable for LLM
        image_data = self.ros_image_to_pil(msg)

        # Store for later use
        self.recent_images.append(image_data)
        if len(self.recent_images) > self.max_images:
            self.recent_images.pop(0)

    def ros_image_to_pil(self, ros_image):
        """Convert ROS image message to PIL Image"""
        # This is a simplified conversion
        # In practice, you'd need to handle different encodings
        height = ros_image.height
        width = ros_image.width
        encoding = ros_image.encoding

        # Convert image data to numpy array based on encoding
        if encoding == 'rgb8':
            image_array = np.frombuffer(ros_image.data, dtype=np.uint8)
            image_array = image_array.reshape((height, width, 3))
            return Image.fromarray(image_array)
        else:
            # Handle other encodings as needed
            return None

    def generate_multimodal_plan(self, task_description: str, image_data=None) -> List[Dict[str, Any]]:
        """Generate plan using both text and visual information"""
        if image_data is None and self.recent_images:
            image_data = self.recent_images[-1]  # Use most recent image

        if image_data:
            # Prepare multimodal prompt
            prompt = f"""
            Task: {task_description}

            Analyze the provided image and create a plan to accomplish the task.
            Consider objects, locations, and spatial relationships visible in the image.

            Current environment state: {self.environment_state}
            Robot capabilities: {self.robot_capabilities}

            Create a detailed step-by-step plan with specific actions.
            """

            # For models that support images (like GPT-4 Vision)
            try:
                # This is a conceptual example - actual implementation depends on the model
                response = self.query_multimodal(prompt, image_data)
                return self.parse_plan_response(response)
            except:
                # Fallback to text-only planning
                return super().generate_plan(task_description)
        else:
            # Fall back to text-only planning
            return super().generate_plan(task_description)

    def query_multimodal(self, prompt: str, image: Image) -> str:
        """Query multimodal LLM with image and text"""
        # Convert image to base64 for API
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Example for OpenAI's vision models (API may vary)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        return response.json()['choices'][0]['message']['content']

    def analyze_scene(self, image_data: Image) -> Dict[str, Any]:
        """Analyze scene content for planning context"""
        prompt = """
        Analyze this image and describe:
        1. Objects present and their locations
        2. Surfaces and navigable areas
        3. Potential obstacles
        4. Any text or signs visible
        5. People or other agents present

        Format your response as a JSON object with keys: objects, locations, obstacles, people
        """

        try:
            response = self.query_multimodal(prompt, image_data)

            # Extract scene information
            scene_info = json.loads(response)
            return scene_info
        except:
            return {"objects": [], "locations": [], "obstacles": [], "people": []}

    def update_environment_with_vision(self):
        """Update environment state using visual perception"""
        if self.recent_images:
            latest_image = self.recent_images[-1]
            scene_analysis = self.analyze_scene(latest_image)
            self.environment_state.update(scene_analysis)
```

## Context-Aware Planning

### Memory and Context Management
```python
# context_management.py - Context and memory management for LLM planning
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pickle
import os

@dataclass
class MemoryItem:
    timestamp: datetime.datetime
    context_type: str  # 'perception', 'action', 'conversation', 'environment'
    content: Any
    importance: float = 1.0  # 0.0 to 1.0

class ContextManager:
    def __init__(self, max_memory_items: int = 100):
        self.memory_items: List[MemoryItem] = []
        self.max_memory_items = max_memory_items
        self.memory_file = "robot_memory.pkl"

    def add_memory(self, context_type: str, content: Any, importance: float = 1.0):
        """Add a memory item to the context"""
        memory_item = MemoryItem(
            timestamp=datetime.datetime.now(),
            context_type=context_type,
            content=content,
            importance=importance
        )

        self.memory_items.append(memory_item)

        # Keep memory size manageable
        if len(self.memory_items) > self.max_memory_items:
            self.memory_items = self._compress_memory()

    def get_relevant_context(self, query: str, max_items: int = 10) -> List[MemoryItem]:
        """Get context items relevant to the current query"""
        # Simple approach: return most recent and important items
        # In practice, you'd use semantic similarity or other methods

        # Sort by importance and recency
        sorted_items = sorted(
            self.memory_items,
            key=lambda x: x.importance * (1.0 / (1.0 + (datetime.datetime.now() - x.timestamp).total_seconds() / 3600)),  # Recent items get higher score
            reverse=True
        )

        return sorted_items[:max_items]

    def _compress_memory(self) -> List[MemoryItem]:
        """Compress memory by removing less important items"""
        # Keep important items, remove older, less important ones
        important_items = [item for item in self.memory_items if item.importance > 0.5]

        if len(important_items) < self.max_memory_items // 2:
            # Keep all important items, add some less important recent ones
            recent_items = sorted(
                [item for item in self.memory_items if item.importance <= 0.5],
                key=lambda x: x.timestamp,
                reverse=True
            )[:self.max_memory_items - len(important_items)]

            return important_items + recent_items
        else:
            # Just keep the most important items
            return sorted(important_items, key=lambda x: x.importance, reverse=True)[:self.max_memory_items]

    def save_memory(self):
        """Save memory to file"""
        with open(self.memory_file, 'wb') as f:
            pickle.dump(self.memory_items, f)

    def load_memory(self):
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'rb') as f:
                self.memory_items = pickle.load(f)

class ContextAwarePlanner(MultimodalCognitivePlanner):
    def __init__(self):
        super().__init__()

        # Initialize context manager
        self.context_manager = ContextManager()
        self.context_manager.load_memory()

        # Subscribe to conversation topics
        self.conversation_sub = self.create_subscription(
            String, 'conversation_history', self.conversation_callback, 10
        )

        # Track task history
        self.task_history = []

    def conversation_callback(self, msg):
        """Handle conversation history updates"""
        conversation_data = json.loads(msg.data)
        self.context_manager.add_memory(
            'conversation',
            conversation_data,
            importance=0.8
        )

    def generate_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate plan with context awareness"""
        # Get relevant context
        relevant_context = self.context_manager.get_relevant_context(
            task_description, max_items=20
        )

        # Build context string for LLM
        context_str = self.build_context_string(relevant_context)

        # Create enhanced prompt with context
        prompt = f"""
        Task: {task_description}

        Relevant context from memory:
        {context_str}

        Current environment state: {self.environment_state}
        Robot capabilities: {self.robot_capabilities}

        Please create a detailed step-by-step plan considering the context.
        The plan should be adaptive to the environment and previous interactions.
        Format each step as: ACTION: [action_name], PARAMETERS: {{param1: value1, ...}}

        Return the plan as a JSON list of steps.
        """

        try:
            response = self.llm.query(prompt, max_tokens=1500, temperature=0.2)

            # Parse the response
            plan = self.parse_plan_response(response)

            # Add to task history
            self.task_history.append({
                'task': task_description,
                'plan': plan,
                'timestamp': datetime.datetime.now()
            })

            # Add to memory
            self.context_manager.add_memory(
                'action',
                {'task': task_description, 'plan': plan},
                importance=0.9
            )

            return plan

        except Exception as e:
            self.get_logger().error(f'Error generating plan: {e}')
            return []

    def build_context_string(self, context_items: List[MemoryItem]) -> str:
        """Build context string from memory items"""
        context_parts = []

        for item in context_items:
            if item.context_type == 'perception':
                context_parts.append(f"Perception: {item.content}")
            elif item.context_type == 'action':
                context_parts.append(f"Previous action: {item.content.get('task', 'Unknown task')}")
            elif item.context_type == 'conversation':
                context_parts.append(f"Conversation: {item.content.get('utterance', 'Unknown utterance')}")
            elif item.context_type == 'environment':
                context_parts.append(f"Environment: {item.content}")

        return "\n".join(context_parts)

    def update_environment_state(self, new_state: Dict[str, Any]):
        """Update environment state and add to memory"""
        self.environment_state.update(new_state)

        self.context_manager.add_memory(
            'environment',
            new_state,
            importance=0.7
        )

    def execute_plan(self, plan: List[Dict[str, Any]]):
        """Execute plan with context updates"""
        self.get_logger().info(f'Executing plan with {len(plan)} steps')

        for i, step in enumerate(plan):
            self.get_logger().info(f'Step {i+1}/{len(plan)}: {step["action"]}')

            # Publish step for execution
            step_msg = String()
            step_msg.data = json.dumps(step)
            self.plan_pub.publish(step_msg)

            # Wait for step completion and update context
            # In practice, this would wait for feedback from action executors
            time.sleep(1)

            # Update context based on step completion
            self.context_manager.add_memory(
                'action',
                {
                    'step': step,
                    'status': 'completed',
                    'timestamp': datetime.datetime.now()
                },
                importance=0.6
            )

        # Save memory after plan completion
        self.context_manager.save_memory()
```

## Planning Validation and Safety

### Plan Validation and Safety Checks
```python
# plan_validation.py - Plan validation and safety for LLM planning
from typing import Dict, Any, List, Tuple
import math

class PlanValidator:
    def __init__(self):
        self.safety_rules = [
            self.check_collision_avoidance,
            self.check_reachability,
            self.check_physical_constraints,
            self.check_task_feasibility
        ]

    def validate_plan(self, plan: List[Dict[str, Any]], environment_state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a plan against safety and feasibility rules"""
        errors = []

        for i, step in enumerate(plan):
            step_errors = self.validate_step(step, environment_state)
            errors.extend([f"Step {i+1}: {error}" for error in step_errors])

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_step(self, step: Dict[str, Any], environment_state: Dict[str, Any]) -> List[str]:
        """Validate a single step"""
        errors = []

        for rule in self.safety_rules:
            rule_errors = rule(step, environment_state)
            errors.extend(rule_errors)

        return errors

    def check_collision_avoidance(self, step: Dict[str, Any], env_state: Dict[str, Any]) -> List[str]:
        """Check if the step might cause collisions"""
        errors = []

        action = step.get('action', '')
        params = step.get('parameters', {})

        if action in ['navigate_to', 'move_forward', 'move_backward', 'turn_left', 'turn_right']:
            # Check if destination is free of obstacles
            if 'x' in params and 'y' in params:
                target_pos = (params['x'], params['y'])
                obstacles = env_state.get('obstacles', [])

                for obs in obstacles:
                    obs_pos = (obs.get('x', 0), obs.get('y', 0))
                    distance = math.sqrt((target_pos[0] - obs_pos[0])**2 + (target_pos[1] - obs_pos[1])**2)
                    if distance < 0.5:  # 50cm safety margin
                        errors.append(f"Collision risk at position {target_pos}")

        return errors

    def check_reachability(self, step: Dict[str, Any], env_state: Dict[str, Any]) -> List[str]:
        """Check if the robot can physically reach the target"""
        errors = []

        action = step.get('action', '')
        params = step.get('parameters', {})

        if action == 'grasp_object':
            obj_name = params.get('object', '')
            objects = env_state.get('objects', [])

            obj_found = False
            for obj in objects:
                if obj.get('name', '') == obj_name:
                    obj_found = True
                    # Check if object is within reach
                    obj_pos = (obj.get('x', 0), obj.get('y', 0), obj.get('z', 0))
                    # Assume robot at origin for simplicity
                    distance = math.sqrt(obj_pos[0]**2 + obj_pos[1]**2 + obj_pos[2]**2)
                    if distance > 1.0:  # 1 meter reach limit
                        errors.append(f"Object {obj_name} is out of reach at {obj_pos}")
                    break

            if not obj_found:
                errors.append(f"Object {obj_name} not found in environment")

        return errors

    def check_physical_constraints(self, step: Dict[str, Any], env_state: Dict[str, Any]) -> List[str]:
        """Check physical constraints like weight limits"""
        errors = []

        action = step.get('action', '')
        params = step.get('parameters', {})

        if action == 'grasp_object':
            obj_name = params.get('object', '')
            objects = env_state.get('objects', [])

            for obj in objects:
                if obj.get('name', '') == obj_name:
                    weight = obj.get('weight', 0)
                    if weight > 5.0:  # 5kg weight limit
                        errors.append(f"Object {obj_name} weighs {weight}kg, exceeds 5kg limit")
                    break

        return errors

    def check_task_feasibility(self, step: Dict[str, Any], env_state: Dict[str, Any]) -> List[str]:
        """Check if the task is generally feasible"""
        errors = []

        action = step.get('action', '')

        # Example: check if robot is capable of the action
        available_actions = [
            'move_forward', 'move_backward', 'turn_left', 'turn_right',
            'grasp_object', 'release_object', 'navigate_to', 'detect_object',
            'wave', 'speak', 'listen'
        ]

        if action not in available_actions:
            errors.append(f"Action {action} not supported by robot")

        return errors

class SafeLLMPlanner(ContextAwarePlanner):
    def __init__(self):
        super().__init__()
        self.validator = PlanValidator()

        # Publisher for validation results
        self.validation_pub = self.create_publisher(String, 'plan_validation', 10)

    def generate_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate and validate plan"""
        plan = super().generate_plan(task_description)

        # Validate the plan
        is_valid, errors = self.validator.validate_plan(plan, self.environment_state)

        # Publish validation results
        validation_msg = String()
        validation_msg.data = json.dumps({
            'task': task_description,
            'is_valid': is_valid,
            'errors': errors,
            'plan_length': len(plan)
        })
        self.validation_pub.publish(validation_msg)

        if not is_valid:
            self.get_logger().warn(f'Plan validation failed with errors: {errors}')
            # Try to fix the plan or generate a safer alternative
            plan = self.revise_plan(plan, errors)

        return plan

    def revise_plan(self, plan: List[Dict[str, Any]], errors: List[str]) -> List[Dict[str, Any]]:
        """Revise plan based on validation errors"""
        # For now, return the original plan
        # In practice, you'd implement plan revision logic
        self.get_logger().info(f'Attempting to revise plan with {len(errors)} errors')

        # You could call the LLM again to fix the plan:
        error_str = "; ".join(errors)
        revision_prompt = f"""
        The following plan had validation errors: {error_str}

        Original plan: {plan}

        Please revise the plan to address these issues while still accomplishing the task.
        Return the revised plan as a JSON list of steps.
        """

        try:
            response = self.llm.query(revision_prompt, max_tokens=1500, temperature=0.1)
            revised_plan = self.parse_plan_response(response)
            return revised_plan
        except:
            # If revision fails, return original plan
            return plan
```

## Practical Exercise

### Exercise 1: LLM Integration Setup
1. Set up OpenAI API access or local LLM
2. Create basic LLM interface for robotics
3. Test with simple robot commands
4. Evaluate response quality and latency

### Exercise 2: Hierarchical Planning
1. Implement task decomposition using LLM
2. Create hierarchical plan structure
3. Test with complex multi-step tasks
4. Evaluate plan breakdown effectiveness

### Exercise 3: Multimodal Integration
1. Integrate vision data with LLM planning
2. Test scene understanding capabilities
3. Evaluate spatial reasoning accuracy
4. Combine vision and language for planning

## Advanced Topics

### Learning from Execution
```python
# learning_from_execution.py - Learning from plan execution
class LearningPlanner(SafeLLMPlanner):
    def __init__(self):
        super().__init__()

        # Execution feedback tracking
        self.execution_feedback = []

        # Subscribe to execution feedback
        self.feedback_sub = self.create_subscription(
            String, 'execution_feedback', self.feedback_callback, 10
        )

    def feedback_callback(self, msg):
        """Handle execution feedback"""
        try:
            feedback = json.loads(msg.data)
            self.execution_feedback.append(feedback)

            # Update LLM based on feedback (conceptual)
            self.adapt_to_feedback(feedback)
        except json.JSONDecodeError:
            self.get_logger().warn('Could not parse feedback as JSON')

    def adapt_to_feedback(self, feedback: Dict[str, Any]):
        """Adapt planning based on execution feedback"""
        success = feedback.get('success', False)
        task = feedback.get('task', '')
        execution_details = feedback.get('details', {})

        if not success:
            # Learn from failure
            error_type = feedback.get('error_type', 'unknown')
            self.get_logger().info(f'Learning from {error_type} in task: {task}')

            # Store failure case for future reference
            self.context_manager.add_memory(
                'failure',
                {
                    'task': task,
                    'error_type': error_type,
                    'details': execution_details
                },
                importance=1.0
            )
        else:
            # Learn from success
            self.context_manager.add_memory(
                'success',
                {
                    'task': task,
                    'execution': execution_details
                },
                importance=0.8
            )

    def generate_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate plan considering past experiences"""
        # Include failure cases in context to avoid repeating mistakes
        recent_failures = [item for item in self.context_manager.memory_items
                          if item.context_type == 'failure' and
                          task_description.lower() in item.content.get('task', '').lower()]

        # Modify the base method to include failure context
        relevant_context = self.context_manager.get_relevant_context(
            task_description, max_items=15
        )

        # Add recent failures to context
        failure_context = []
        for failure in recent_failures[-3:]:  # Last 3 failures
            failure_context.append(f"Avoid: {failure.content.get('error_type', 'Unknown error')} - {failure.content.get('details', {})}")

        context_str = self.build_context_string(relevant_context)
        if failure_context:
            context_str += "\n\nIMPORTANT: Avoid these previous failures:\n" + "\n".join(failure_context)

        # Continue with normal planning process using enhanced context
        prompt = f"""
        Task: {task_description}

        Relevant context from memory:
        {context_str}

        Current environment state: {self.environment_state}
        Robot capabilities: {self.robot_capabilities}

        Please create a detailed step-by-step plan considering the context.
        Pay special attention to avoiding the failures mentioned above.
        The plan should be adaptive to the environment and previous interactions.
        Format each step as: ACTION: [action_name], PARAMETERS: {{param1: value1, ...}}

        Return the plan as a JSON list of steps.
        """

        try:
            response = self.llm.query(prompt, max_tokens=1500, temperature=0.2)
            plan = self.parse_plan_response(response)

            self.task_history.append({
                'task': task_description,
                'plan': plan,
                'timestamp': datetime.datetime.now()
            })

            self.context_manager.add_memory(
                'action',
                {'task': task_description, 'plan': plan},
                importance=0.9
            )

            return plan

        except Exception as e:
            self.get_logger().error(f'Error generating plan: {e}')
            return []
```

## Summary

This week covered LLM cognitive planning:
- LLM integration with robotic systems
- Hierarchical task decomposition and reasoning
- Multimodal integration (vision-language planning)
- Context-aware planning with memory management
- Plan validation and safety considerations
- Learning from execution feedback

## Next Week Preview

Week 13 will focus on the capstone project: Autonomous Humanoid, where you'll integrate all the modules learned throughout the course into a complete autonomous humanoid robot system.