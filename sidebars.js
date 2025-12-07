// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  textbookSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1/week-1/introduction',
        'module-1/week-1/ros-architecture',
        'module-1/week-2/python-integration',
        'module-1/week-3/urdf-concepts',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'module-2/week-4/physics-simulation',
        'module-2/week-5/high-fidelity-rendering',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
      items: [
        'module-3/week-6/isaac-sim',
        'module-3/week-7/isaac-ros',
        'module-3/week-8/nav2-bipedal',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module-4/week-9/voice-commands',
        'module-4/week-10/llm-cognitive-planning',
        'module-4/week-11/capstone-project',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Appendices',
      items: [
        'hardware-requirements',
        'glossary',
        'additional-resources',
      ],
      collapsed: false,
    }
  ],
};

export default sidebars;