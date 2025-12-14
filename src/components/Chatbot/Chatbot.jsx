import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Determine color mode based on data-theme attribute in the document
  const effectiveColorMode = typeof document !== 'undefined' && document.documentElement
    ? document.documentElement.getAttribute('data-theme') || 'light'
    : 'light';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue.trim() };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get the model from environment variables (default to gpt-3.5-turbo)
      const model = process.env.OPENAI_MODEL || 'gpt-3.5-turbo';

      // Call the backend API to get the response
      // The backend will handle the OpenAI API key securely
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: newMessages.map(msg => ({ role: msg.role, content: msg.content })),
          model: model,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { role: 'assistant', content: data.content };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      let errorMessageContent = 'Sorry, I encountered an error. ';

      if (error.message.includes('fetch') || error.message.includes('network')) {
        errorMessageContent += 'Please make sure the backend server is running on http://localhost:8000.';
      } else {
        errorMessageContent += 'Please check that the backend server is properly configured.';
      }

      errorMessageContent += ' For setup instructions, please refer to the README file.';

      const errorMessage = {
        role: 'assistant',
        content: errorMessageContent
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <>
      <button
        className={`chatbot-toggle-button ${isOpen ? 'open' : ''} ${effectiveColorMode}`}
        onClick={toggleChat}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        💬
      </button>

      {isOpen && (
        <div className={`chatbot-container ${effectiveColorMode}`}>
          <div className="chatbot-header">
            <h3>AI Assistant</h3>
            <div className="chatbot-header-actions">
              <button
                className="chatbot-clear-button"
                onClick={clearChat}
                title="Clear chat"
              >
                🗑️
              </button>
              <button
                className="chatbot-close-button"
                onClick={toggleChat}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="chatbot-welcome">
                <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook.</p>
                <p>Ask me anything about the content, and I'll do my best to help!</p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`chatbot-message ${message.role}`}
                >
                  <div className="chatbot-message-content">
                    {message.content}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="chatbot-message assistant">
                <div className="chatbot-message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-form" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about the textbook content..."
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
            >
              📤
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default Chatbot;