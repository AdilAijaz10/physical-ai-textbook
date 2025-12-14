import React from 'react';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <p className="message-text">{message.content}</p>

      {message.citations && message.citations.length > 0 && (
        <div className="citations">
          <strong>Sources:</strong>
          {message.citations.map((citation, index) => (
            <div key={index} className="citation-item">
              {citation.file_path} (Chunk {citation.chunk_index})
            </div>
          ))}
        </div>
      )}

      {message.selectedText && (
        <div className="selected-text-context">
          <small><em>Context: "{message.selectedText}"</em></small>
        </div>
      )}
    </div>
  );
};

export default Message;