import React, { useEffect, useState } from 'react';
import Chatbot from '../components/Chatbot';

// This is the Root component that wraps the entire application
export default function Root({children}) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    // Only render the chatbot on the client side to avoid SSR issues
    setIsClient(true);
  }, []);

  return (
    <>
      {children}
      {isClient && <Chatbot />}
    </>
  );
}