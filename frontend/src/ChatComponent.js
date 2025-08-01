import React, { useState, useEffect, useRef } from 'react';
import './ChatComponent.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://ai-grant-writer-tool-production.up.railway.app';

const ChatComponent = ({ projectId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [privacyStatus, setPrivacyStatus] = useState('high');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChatHistory();
    checkPrivacyStatus();
  }, [projectId]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/chat/history/${projectId}`);

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.messages) {
          setMessages(data.messages);
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const checkPrivacyStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/privacy/audit/${projectId}`);

      if (response.ok) {
        const data = await response.json();
        // Set privacy status based on audit result
        if (data.audit_result && data.audit_result.overall_privacy_level) {
          setPrivacyStatus(data.audit_result.overall_privacy_level);
        }
      }
    } catch (error) {
      console.error('Error checking privacy status:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      message: inputMessage,
      timestamp: new Date().toISOString(),
      type: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/send_message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          message: inputMessage
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const aiMessage = {
            id: Date.now() + 1,
            message: data.response,
            timestamp: new Date().toISOString(),
            type: 'ai'
          };
          setMessages(prev => [...prev, aiMessage]);
        }
      } else {
        // Handle error
        const errorMessage = {
          id: Date.now() + 1,
          message: "Sorry, I couldn't process your message right now. Please try again!",
          timestamp: new Date().toISOString(),
          type: 'ai'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        message: "Sorry, I couldn't send your message right now. Please try again!",
        timestamp: new Date().toISOString(),
        type: 'ai'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-container">
      {/* Messages Container - Moved higher up */}
      <div className="messages-container">
        <div className="messages-list">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">
                  {message.message}
                </div>
                <div className="message-timestamp">
                  {formatTime(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message ai">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-container">
        <form onSubmit={sendMessage} className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me anything about your grant proposal..."
            disabled={isLoading}
            rows={1}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(e);
              }
            }}
          />
          <button 
            type="submit" 
            className="send-btn"
            disabled={isLoading || !inputMessage.trim()}
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatComponent;