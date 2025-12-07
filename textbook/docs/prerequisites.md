---
sidebar_position: 3
---

# Prerequisites and Setup Instructions

## Prerequisites

### Required Knowledge
- **Programming**: Basic to intermediate knowledge of Python programming
- **Mathematics**: Understanding of linear algebra and calculus fundamentals
- **Robotics**: Basic knowledge of robotics concepts (kinematics, dynamics)
- **Operating Systems**: Familiarity with Linux command line and basic system administration

### Recommended Background
- Experience with version control systems (Git)
- Basic understanding of computer vision and machine learning concepts
- Familiarity with containerization (Docker)

## System Requirements

### Minimum System Requirements
- **CPU**: Intel i7 or AMD Ryzen 7 with 8+ cores
- **RAM**: 16GB minimum, 32GB recommended
- **GPU**: NVIDIA RTX 3060 or equivalent with CUDA support
- **Storage**: 500GB SSD minimum
- **OS**: Ubuntu 20.04 LTS or Windows 10/11 with WSL2

### Recommended Hardware for Advanced Work
- **CPU**: Intel i9 or AMD Ryzen 9 with 16+ cores
- **RAM**: 64GB or more
- **GPU**: NVIDIA RTX 4080 or A6000 for advanced simulation
- **Additional**: Multiple monitors for development

## Software Installation

### Core Software Stack
1. **ROS 2 Humble Hawksbill** (or later LTS version)
   - Installation guide: [ROS 2 Installation](https://docs.ros.org/en/humble/Installation.html)
   - Verify installation: `ros2 --version`

2. **Gazebo Garden** (or Fortress)
   - Installation guide: [Gazebo Installation](https://gazebosim.org/docs/garden/install)
   - Verify installation: `gz --version`

3. **Unity 2022.3 LTS** (or later LTS version)
   - Download from [Unity Hub](https://unity.com/download)
   - Install with Linux Build Support if targeting Linux

4. **NVIDIA Isaac ROS**
   - Installation guide: [Isaac ROS](https://nvidia-isaac-ros.github.io/repositories_and_packages/index.html)
   - Requires NVIDIA GPU with CUDA support

### Development Tools
1. **Python 3.8+**
   ```bash
   python3 --version
   pip3 --version
   ```

2. **Git Version Control**
   ```bash
   git --version
   ```

3. **Docker** (for containerized environments)
   ```bash
   docker --version
   ```

4. **Code Editor**
   - Recommended: VS Code with ROS extensions
   - Alternative: Vim/Emacs with appropriate plugins

### Additional Libraries and Dependencies

1. **Python Libraries** (install via pip):
   ```bash
   pip3 install numpy scipy matplotlib
   pip3 install opencv-python
   pip3 install torch torchvision  # For AI components
   pip3 install openai  # For Whisper integration
   ```

2. **System Libraries** (Ubuntu):
   ```bash
   sudo apt update
   sudo apt install build-essential cmake pkg-config
   sudo apt install libeigen3-dev libopencv-dev
   sudo apt install python3-dev python3-pip
   ```

## Environment Setup

### ROS 2 Environment
1. Source the ROS 2 installation in your shell:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Add to your `~/.bashrc` for persistent sourcing:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   ```

### Workspace Setup
1. Create a ROS 2 workspace:
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws
   colcon build
   source install/setup.bash
   ```

2. Add workspace sourcing to your `~/.bashrc`:
   ```bash
   echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
   ```

## Testing Your Setup

### Basic ROS 2 Test
1. Open two terminal windows
2. In the first terminal, run:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 topic echo /chatter std_msgs/msg/String
   ```
3. In the second terminal, run:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run demo_nodes_cpp talker
   ```
4. You should see messages passing between the nodes

### Python Integration Test
```python
import rclpy
from std_msgs.msg import String

print("ROS 2 Python integration working!")
```

## Troubleshooting Common Issues

### ROS 2 Installation Issues
- Ensure correct Ubuntu version (20.04 LTS recommended)
- Check that locale settings are correct: `locale` should show UTF-8
- Verify network connectivity for package downloads

### GPU/CUDA Issues
- Verify GPU drivers are correctly installed
- Check CUDA version compatibility with Isaac ROS requirements
- Test CUDA: `nvidia-smi` and `nvcc --version`

### Permission Issues
- Add user to required groups: `sudo usermod -a -G dialout $USER`
- For Docker: `sudo usermod -aG docker $USER`
- Log out and back in for group changes to take effect

## Next Steps

Once you have completed the setup and verified all components are working:

1. Review the [Hardware Requirements](./hardware-requirements.md) for physical robot options
2. Familiarize yourself with the [Assessment Guidelines](./assessment-guidelines.md)
3. Begin with [Module 1: The Robotic Nervous System (ROS 2)](./module1/week3-ros2-architecture.md)