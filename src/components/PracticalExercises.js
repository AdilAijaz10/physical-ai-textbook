import React from 'react';
import clsx from 'clsx';
import styles from './PracticalExercises.module.css';

export default function PracticalExercises({exercises}) {
  return (
    <div className={clsx('practical-exercises', styles.practicalExercises)}>
      <h3>Practical Exercises</h3>
      {exercises.map((exercise, index) => (
        <div className={styles.exercise} key={index}>
          <h4>{exercise.title}</h4>
          <p><strong>Difficulty:</strong> {exercise.difficulty || 'Intermediate'}</p>
          <p>{exercise.description}</p>
          <h5>Instructions:</h5>
          <p>{exercise.instructions}</p>
          {exercise.expectedOutcome && (
            <>
              <h5>Expected Outcome:</h5>
              <p>{exercise.expectedOutcome}</p>
            </>
          )}
          {exercise.resources && exercise.resources.length > 0 && (
            <>
              <h5>Resources:</h5>
              <ul>
                {exercise.resources.map((resource, idx) => (
                  <li key={idx}>{resource}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      ))}
    </div>
  );
}