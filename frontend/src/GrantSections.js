import React, { useState, useEffect } from 'react';
import './GrantSections.css';

const GrantSections = ({ projectId }) => {
  const [sections, setSections] = useState({});
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState(new Set());
  const [updatingSection, setUpdatingSection] = useState(null);
  const [exporting, setExporting] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (projectId) {
      loadGrantSections();
    }
  }, [projectId]);

  const loadGrantSections = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}`);
      const data = await response.json();
      
      if (data.success) {
        setSections(data.doc_state || {});
        setStats(data.stats || {});
        
        // Expand first section by default
        if (Object.keys(data.doc_state || {}).length > 0) {
          setExpandedSections(new Set([Object.keys(data.doc_state)[0]]));
        }
      }
    } catch (error) {
      console.error('Error loading grant sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSection = async (sectionId, content) => {
    try {
      setUpdatingSection(sectionId);
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}/${sectionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      
      const data = await response.json();
      if (data.success) {
        setSections(data.doc_state);
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error updating section:', error);
    } finally {
      setUpdatingSection(null);
    }
  };

  const regenerateSection = async (sectionId) => {
    try {
      setUpdatingSection(sectionId);
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}/${sectionId}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: "Please regenerate this section with comprehensive content." })
      });
      
      const data = await response.json();
      if (data.success) {
        setSections(data.doc_state);
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error regenerating section:', error);
    } finally {
      setUpdatingSection(null);
    }
  };

  const toggleSection = (sectionId) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const exportDocument = async (format) => {
    try {
      setExporting(true);
      const response = await fetch(`${API_BASE}/grant/sections/${projectId}/export/${format}`);
      const data = await response.json();
      
      if (data.success) {
        // Create and download file
        const blob = new Blob([data.content], { 
          type: format === 'markdown' ? 'text/markdown' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
        });
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

  const getSectionStatus = (sectionId) => {
    const sectionStats = stats.sections?.[sectionId];
    if (!sectionStats) return 'draft';
    return sectionStats.status;
  };

  const getSectionProgress = (sectionId) => {
    const sectionStats = stats.sections?.[sectionId];
    if (!sectionStats) return 0;
    
    const targetWords = parseInt(sectionStats.target_length.match(/\d+/)[0]);
    return Math.min((sectionStats.word_count / targetWords) * 100, 100);
  };

  if (loading) {
    return (
      <div className="grant-sections-loading">
        <div className="spinner"></div>
        <p>Loading grant sections...</p>
      </div>
    );
  }

  return (
    <div className="grant-sections-container">
      {/* Header */}
      <div className="grant-sections-header">
        <h2>📋 Grant Application Sections</h2>
        <p>Build your complete, funder-aligned proposal with structured sections</p>
        
        {/* Progress Overview */}
        <div className="progress-overview">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${stats.completion_percentage || 0}%` }}
            ></div>
          </div>
          <span className="progress-text">
            {Math.round(stats.completion_percentage || 0)}% Complete
          </span>
        </div>
        
        {/* Export Buttons */}
        <div className="export-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => exportDocument('markdown')}
            disabled={exporting}
          >
            📄 Export Markdown
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => exportDocument('docx')}
            disabled={exporting}
          >
            📝 Export DOCX
          </button>
        </div>
      </div>

      {/* Sections List */}
      <div className="sections-list">
        {Object.entries(sections).map(([sectionId, content]) => {
          const isExpanded = expandedSections.has(sectionId);
          const status = getSectionStatus(sectionId);
          const progress = getSectionProgress(sectionId);
          const sectionStats = stats.sections?.[sectionId];
          
          return (
            <div key={sectionId} className={`section-card ${status}`}>
              {/* Section Header */}
              <div 
                className="section-header"
                onClick={() => toggleSection(sectionId)}
              >
                <div className="section-info">
                  <h3>{sectionStats?.title || sectionId}</h3>
                  <div className="section-meta">
                    <span className="word-count">
                      {sectionStats?.word_count || 0} words
                    </span>
                    <span className="target-length">
                      Target: {sectionStats?.target_length}
                    </span>
                    <span className={`status-badge ${status}`}>
                      {status}
                    </span>
                  </div>
                </div>
                
                <div className="section-actions">
                  <div className="progress-indicator">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <button className="expand-btn">
                    {isExpanded ? '−' : '+'}
                  </button>
                </div>
              </div>

              {/* Section Content */}
              {isExpanded && (
                <div className="section-content">
                  <div className="section-editor">
                    <textarea
                      value={content}
                      onChange={(e) => updateSection(sectionId, e.target.value)}
                      placeholder="Start writing your grant section content..."
                      disabled={updatingSection === sectionId}
                    />
                    
                    <div className="editor-actions">
                      <button 
                        className="btn btn-secondary"
                        onClick={() => regenerateSection(sectionId)}
                        disabled={updatingSection === sectionId}
                      >
                        🔄 Regenerate with AI
                      </button>
                      
                      {updatingSection === sectionId && (
                        <span className="updating-indicator">
                          <div className="spinner"></div>
                          Updating...
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Document Stats */}
      <div className="document-stats">
        <h3>📊 Document Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Total Words</span>
            <span className="stat-value">{stats.total_word_count || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Completion</span>
            <span className="stat-value">{Math.round(stats.completion_percentage || 0)}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Last Updated</span>
            <span className="stat-value">
              {stats.last_updated ? new Date(stats.last_updated).toLocaleDateString() : 'Never'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GrantSections; 