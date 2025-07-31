import React, { useState, useEffect, useRef } from 'react';
import './ChatComponent.css';

const API_BASE = "https://ai-grant-writer-tool-production.up.railway.app";

function ChatComponent({ projectId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [brainstormTopic, setBrainstormTopic] = useState('');
  const [showBrainstorm, setShowBrainstorm] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          type: 'ai',
          content: `👋 Welcome to AI Grant Writer! I'm here to help you with grant writing, brainstorming, and answering questions about your project.

💡 **What I can help with:**
• Writing grant sections (executive summary, objectives, methodology)
• Brainstorming funding ideas and strategies
• Reviewing and improving grant content
• Answering questions about grant requirements
• Providing cultural competence guidance

🎯 **Just ask me anything about your grant project!**`,
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/send_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          project_id: projectId
        })
      });

      const data = await response.json();
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.ai_response || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, I encountered an error connecting to the server. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBrainstorm = async () => {
    if (!brainstormTopic.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/chat/brainstorm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: brainstormTopic,
          project_id: projectId
        })
      });

      const data = await response.json();
      
      const brainstormMessage = {
        id: Date.now(),
        type: 'ai',
        content: `💡 **Brainstorming Ideas for: "${brainstormTopic}"**

${data.suggestions || 'Sorry, I encountered an error. Please try again.'}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, brainstormMessage]);
      setBrainstormTopic('');
      setShowBrainstorm(false);
    } catch (error) {
      console.error('Error brainstorming:', error);
      const errorMessage = {
        id: Date.now(),
        type: 'ai',
        content: 'Sorry, I encountered an error while brainstorming. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/•/g, '• ')
      .split('\n').map((line, i) => 
        line.trim() ? `<div key="${i}">${line}</div>` : '<div key="${i}"><br></div>'
      ).join('');
  };

  return (
    <div className="chat-container">
      {/* Chat Header */}
      <div className="chat-header">
        <h3>💬 Interactive Chat & Brainstorming</h3>
        <p>Ask questions, get advice, and brainstorm grant ideas</p>
      </div>

      {/* Messages Area */}
      <div className="messages-container">
        <div className="messages-list">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div 
                  className="message-text"
                  dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                />
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message ai">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Brainstorming Section */}
      {showBrainstorm && (
        <div className="brainstorm-section">
          <div className="brainstorm-header">
            <h4>💡 Brainstorm Ideas</h4>
            <button 
              className="close-btn"
              onClick={() => setShowBrainstorm(false)}
            >
              ✕
            </button>
          </div>
          <div className="brainstorm-input">
            <textarea
              value={brainstormTopic}
              onChange={(e) => setBrainstormTopic(e.target.value)}
              placeholder="Enter a topic to brainstorm about, e.g., 'funding strategies for youth programs'"
              rows={3}
            />
            <button 
              className="btn btn-primary"
              onClick={handleBrainstorm}
              disabled={!brainstormTopic.trim() || isLoading}
            >
              {isLoading ? 'Generating Ideas...' : 'Brainstorm'}
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your grant project..."
            rows={1}
            disabled={isLoading}
          />
          <button 
            className="send-btn"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        
        <div className="input-actions">
          <button 
            className="action-btn"
            onClick={() => setShowBrainstorm(!showBrainstorm)}
            disabled={isLoading}
          >
            💡 Brainstorm
          </button>
        </div>
      </div>

      {/* Floating Action Button */}
      <button 
        className="fab"
        onClick={() => setShowBrainstorm(!showBrainstorm)}
        title="Brainstorm Ideas"
      >
        💡
      </button>
    </div>
  );
}

export default ChatComponent;