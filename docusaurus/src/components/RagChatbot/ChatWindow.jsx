import React from 'react';
import Message from './Message';

const ChatWindow = ({ messages, isLoading }) => {
  return (
    <div className="chat-messages">
      {messages.length === 0 ? (
        <div className="welcome-message">
          <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook.</p>
          <p>Ask me any questions about the content, or select text and ask about it specifically.</p>
        </div>
      ) : (
        messages.map((message) => (
          <Message key={message.id} message={message} />
        ))
      )}
      {isLoading && (
        <div className="message assistant-message loading-indicator">
          Thinking...
        </div>
      )}
    </div>
  );
};

export default ChatWindow;