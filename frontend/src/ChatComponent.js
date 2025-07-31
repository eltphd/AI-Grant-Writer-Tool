import React, { useState, useEffect, useRef } from 'react';
import './ChatComponent.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://ai-grant-writer-tool-production.up.railway.app';

const ChatComponent = ({ projectId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showBrainstorm, setShowBrainstorm] = useState(false);
  const [brainstormTopic, setBrainstormTopic] = useState('');
  const [privacyStatus, setPrivacyStatus] = useState('low');
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
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE}/chat/history/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

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
          message: "I'm sorry, I'm having trouble connecting right now. Please try again.",
          timestamp: new Date().toISOString(),
          type: 'ai'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        message: "I'm sorry, there was an error. Please try again.",
        timestamp: new Date().toISOString(),
        type: 'ai'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBrainstorm = async (e) => {
    e.preventDefault();
    if (!brainstormTopic.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/chat/brainstorm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          topic: brainstormTopic
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const brainstormMessage = {
          id: Date.now(),
          message: `Brainstorming ideas for: ${brainstormTopic}\n\n${data.suggestions}`,
          timestamp: new Date().toISOString(),
          type: 'ai'
        };
        setMessages(prev => [...prev, brainstormMessage]);
        setShowBrainstorm(false);
        setBrainstormTopic('');
      }
    } catch (error) {
      console.error('Error brainstorming:', error);
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
      {/* Chat Header */}
      <div className="chat-header">
        <h3>👋 Welcome to GWAT — Your Grant Writing Assisted Toolkit</h3>
        <p>Ready to co-write a funder-aligned proposal? Let's begin.</p>
        
        <div className="privacy-indicator">
          <span className={`privacy-badge ${privacyStatus}`}>
            Privacy: {privacyStatus.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Messages Container */}
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

        <div className="input-actions">
          <button
            className="action-btn"
            onClick={() => setShowBrainstorm(!showBrainstorm)}
            disabled={isLoading}
          >
            💡 Brainstorm
          </button>
          <button
            className="action-btn"
            onClick={() => window.open(`${API_BASE}/grant/sections/${projectId}/export/markdown`, '_blank')}
            disabled={isLoading}
          >
            📄 Export
          </button>
        </div>
      </div>

      {/* Brainstorming Section */}
      {showBrainstorm && (
        <div className="brainstorm-section">
          <div className="brainstorm-header">
            <h4>💡 Brainstorming Assistant</h4>
            <button 
              className="close-btn"
              onClick={() => setShowBrainstorm(false)}
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleBrainstorm} className="brainstorm-input">
            <textarea
              value={brainstormTopic}
              onChange={(e) => setBrainstormTopic(e.target.value)}
              placeholder="What would you like to brainstorm about? (e.g., 'funding sources for education projects', 'evaluation methods for community programs')"
              rows={3}
            />
            <button 
              type="submit" 
              className="btn btn-secondary"
              disabled={isLoading || !brainstormTopic.trim()}
            >
              {isLoading ? 'Generating...' : 'Generate Ideas'}
            </button>
          </form>
        </div>
      )}

      {/* Floating Action Button */}
      <button 
        className="fab"
        onClick={() => setShowBrainstorm(!showBrainstorm)}
        title="Brainstorming Assistant"
      >
        💡
      </button>
    </div>
  );
};

export default ChatComponent;