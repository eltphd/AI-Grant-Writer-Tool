import React, { useState, useEffect } from 'react';
import './GrantSections.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://ai-grant-writer-tool-production.up.railway.app';

const GrantSections = ({ projectId }) => {
  const [sections, setSections] = useState({});
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [chatSummary, setChatSummary] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');

  useEffect(() => {
    loadGrantSections();
  }, [projectId]);

  const loadGrantSections = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSections(data.sections || {});
          setStats(data.stats || {});
          setChatSummary(data.chat_summary || '');
          setLastUpdated(data.last_updated || '');
        }
      }
    } catch (error) {
      console.error('Error loading grant sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportDocument = async (format) => {
    try {
      setExporting(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}/export/${format}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `grant-application-${projectId}.${format === 'markdown' ? 'md' : 'docx'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error exporting document:', error);
    } finally {
      setExporting(false);
    }
  };

  const getSectionStatus = (content) => {
    if (!content || content.trim() === '') return 'empty';
    if (content.length < 100) return 'draft';
    if (content.length < 500) return 'developing';
    return 'complete';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'complete': return 'success';
      case 'developing': return 'warning';
      case 'draft': return 'info';
      default: return 'secondary';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'complete': return 'Complete';
      case 'developing': return 'In Progress';
      case 'draft': return 'Draft';
      default: return 'Empty';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="grant-sections-container">
        <div className="grant-sections-loading">
          <div className="spinner"></div>
          <p>Loading your grant application sections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grant-sections-container">
      {/* Header */}
      <div className="grant-sections-header">
        <h2>📋 Your Grant Application</h2>
        <p>AI-generated sections based on your chat conversations</p>
      </div>

      {/* Progress Overview */}
      <div className="progress-overview">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${stats.completion_percentage || 0}%` }}
          ></div>
        </div>
        <div className="progress-text">
          {stats.completion_percentage || 0}% Complete
        </div>
      </div>

      {/* Export Actions */}
      <div className="export-actions">
        <button 
          className="btn btn-primary"
          onClick={() => exportDocument('markdown')}
          disabled={exporting}
        >
          {exporting ? 'Exporting...' : '📝 Export Markdown'}
        </button>
        <button 
          className="btn btn-primary"
          onClick={() => exportDocument('docx')}
          disabled={exporting}
        >
          {exporting ? 'Exporting...' : '📄 Export DOCX'}
        </button>
      </div>

      {/* Chat Summary */}
      {chatSummary && (
        <div className="chat-summary-section">
          <h3>💬 Conversation Summary</h3>
          <p>{chatSummary}</p>
          <small>Last updated: {formatDate(lastUpdated)}</small>
        </div>
      )}

      {/* Sections List */}
      <div className="sections-list">
        {Object.entries(sections).map(([sectionId, section]) => {
          const status = getSectionStatus(section.content);
          const statusColor = getStatusColor(status);
          
          return (
            <div key={sectionId} className={`section-card ${status}`}>
              <div className="section-header">
                <div className="section-info">
                  <h3>{section.title}</h3>
                  <div className="section-meta">
                    <span className="word-count">
                      {section.content ? section.content.split(' ').length : 0} words
                    </span>
                    <span className="target-length">
                      Target: {section.target_length}
                    </span>
                    <span className={`status-badge ${statusColor}`}>
                      {getStatusText(status)}
                    </span>
                  </div>
                </div>
                
                <div className="section-actions">
                  <div className="progress-indicator">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${Math.min(100, (section.content ? section.content.split(' ').length : 0) / (parseInt(section.target_length) || 1) * 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="section-content">
                <div className="section-preview">
                  {section.content ? (
                    <div className="content-preview">
                      {section.content.length > 300 
                        ? `${section.content.substring(0, 300)}...` 
                        : section.content
                      }
                    </div>
                  ) : (
                    <div className="empty-section">
                      <p>This section will be populated as you chat with the AI assistant.</p>
                      <small>Continue your conversation to build this section</small>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Document Statistics */}
      <div className="document-stats">
        <h3>📊 Document Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Total Words</div>
            <div className="stat-value">{stats.total_words || 0}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Sections Complete</div>
            <div className="stat-value">{stats.complete_sections || 0}/6</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Completion</div>
            <div className="stat-value">{stats.completion_percentage || 0}%</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Last Updated</div>
            <div className="stat-value">{formatDate(lastUpdated)}</div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="cta-section">
        <h3>🚀 Continue Building Your Grant</h3>
        <p>
          Your grant application sections are automatically populated based on your conversations with the AI assistant. 
          Return to the chat to continue building your proposal.
        </p>
        <div className="cta-actions">
          <button 
            className="btn btn-primary"
            onClick={() => window.history.back()}
          >
            ← Back to Chat
          </button>
          <button 
            className="btn btn-secondary"
            onClick={() => window.open(`${API_BASE}/grant/sections/${projectId}/export/markdown`, '_blank')}
          >
            📄 Download Application
          </button>
        </div>
      </div>
    </div>
  );
};

export default GrantSections; 