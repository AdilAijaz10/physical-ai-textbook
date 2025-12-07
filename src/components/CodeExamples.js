import React from 'react';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import clsx from 'clsx';
import styles from './CodeExamples.module.css';

export default function CodeExamples({examples}) {
  const hasMultipleLanguages = examples.length > 1;

  if (!hasMultipleLanguages) {
    const example = examples[0];
    return (
      <div className={clsx('code-examples', styles.codeExamples)}>
        <h3>{example.title || 'Code Example'}</h3>
        <p>{example.description}</p>
        <pre>
          <code className={example.language ? `language-${example.language}` : ''}>
            {example.code}
          </code>
        </pre>
        {example.explanation && <div className={styles.explanation}>{example.explanation}</div>}
      </div>
    );
  }

  return (
    <div className={clsx('code-examples', styles.codeExamples)}>
      <Tabs>
        {examples.map((example, index) => (
          <TabItem value={example.language} label={example.language} key={index}>
            <h3>{example.title}</h3>
            <p>{example.description}</p>
            <pre>
              <code className={example.language ? `language-${example.language}` : ''}>
                {example.code}
              </code>
            </pre>
            {example.explanation && <div className={styles.explanation}>{example.explanation}</div>}
          </TabItem>
        ))}
      </Tabs>
    </div>
  );
}