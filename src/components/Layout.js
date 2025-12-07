import React from 'react';
import Layout from '@theme/Layout';

export default function TextbookLayout(props) {
  return (
    <Layout
      {...props}
      wrapperClassName="textbook-content"
    >
      {props.children}
    </Layout>
  );
}