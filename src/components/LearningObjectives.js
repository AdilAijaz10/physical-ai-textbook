import React from 'react';
import clsx from 'clsx';
import styles from './LearningObjectives.module.css';

export default function LearningObjectives({objectives}) {
  return (
    <div className={clsx('learning-objectives', styles.learningObjectives)}>
      <h3>Learning Objectives</h3>
      <ul>
        {objectives.map((objective, index) => (
          <li key={index}>{objective}</li>
        ))}
      </ul>
    </div>
  );
}