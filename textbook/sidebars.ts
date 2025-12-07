import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Custom sidebar for the Physical AI & Humanoid Robotics textbook
  textbookSidebar: [
    {
      type: 'category',
      label: 'Course Overview',
      items: [
        'intro',
        'course-objectives',
        'prerequisites',
        'hardware-requirements',
        'assessment-guidelines'
      ],
      collapsed: false
    },
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module1/week3-ros2-architecture',
        'module1/week4-python-integration',
        'module1/week5-urdf-humanoid'
      ],
      collapsed: false
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'module2/week6-physics-simulation',
        'module2/week7-high-fidelity-rendering'
      ],
      collapsed: false
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
      items: [
        'module3/week8-isaac-sim',
        'module3/week9-isaac-ros-vslam',
        'module3/week10-nav2-bipedal'
      ],
      collapsed: false
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module4/week11-voice-commands',
        'module4/week12-llm-cognitive-planning',
        'module4/week13-capstone-project'
      ],
      collapsed: false
    },
    {
      type: 'category',
      label: 'Additional Resources',
      items: [
        'glossary',
        'references',
        'appendix'
      ],
      collapsed: true
    }
  ],
};

export default sidebars;
