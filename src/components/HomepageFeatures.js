import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

import RobotRos from '@site/static/img/robot-ros.svg';
import RobotSimulation from '@site/static/img/robot-simulation.svg';
import RobotAi from '@site/static/img/robot-ai.svg';
import RobotVla from '@site/static/img/robot-vla.svg';

const FeatureList = [
  {
    title: 'Module 1: The Robotic Nervous System',
    Svg: RobotRos,
    description: (
      <>
        Learn ROS 2 architecture, nodes, topics, services, Python integration with rclpy,
        and URDF for humanoid robots.
      </>
    ),
  },
  {
    title: 'Module 2: The Digital Twin',
    Svg: RobotSimulation,
    description: (
      <>
        Explore physics simulation in Gazebo, high-fidelity rendering in Unity,
        and sensor simulation (LiDAR, cameras, IMUs).
      </>
    ),
  },
  {
    title: 'Module 3: The AI-Robot Brain',
    Svg: RobotAi,
    description: (
      <>
        Work with Isaac Sim for photorealistic simulation, Isaac ROS for VSLAM and navigation,
        and Nav2 for bipedal movement.
      </>
    ),
  },
  {
    title: 'Module 4: Vision-Language-Action',
    Svg: RobotVla,
    description: (
      <>
        Implement voice commands with OpenAI Whisper, LLM cognitive planning,
        and complete a capstone autonomous humanoid project.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--3')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}