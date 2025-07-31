import React, { useState, useEffect } from 'react';
import './GrantSections.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://ai-grant-writer-tool-production.up.railway.app';

const GrantSections = () => {
  const [sections, setSections] = useState({});
  const [loading, setLoading] = useState(true);
  const [editingSection, setEditingSection] = useState(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadSections();
  }, []);

  const loadSections = async () => {
    try {
      const response = await fetch(`${API_BASE}/grant/sections/test-project`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSections(data.sections);
        }
      }
    } catch (error) {
      console.error('Error loading sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (sectionKey, content) => {
    setEditingSection(sectionKey);
    setEditContent(content);
  };

  const handleSave = (sectionKey) => {
    setSections(prev => ({
      ...prev,
      [sectionKey]: editContent
    }));
    setEditingSection(null);
    setEditContent('');
  };

  const handleCancel = () => {
    setEditingSection(null);
    setEditContent('');
  };

  const sectionDescriptions = {
    executive_summary: {
      title: "Executive Summary",
      description: "A compelling 1-2 page overview that hooks the reader and summarizes your entire proposal. This is often the first thing funders read!",
      tips: [
        "Start with a powerful opening sentence",
        "Include key statistics and impact numbers",
        "Mention the funding amount you're requesting",
        "End with a clear call to action"
      ]
    },
    organization_profile: {
      title: "Organization Profile",
      description: "Tell your organization's story and build credibility. Show why you're the right organization for this project.",
      tips: [
        "Highlight your mission and values",
        "Showcase past achievements with specific metrics",
        "Emphasize your expertise in the target area",
        "Include testimonials from partners or beneficiaries"
      ]
    },
    project_approach: {
      title: "Project Description & Approach",
      description: "Detail what you want to do, how you'll do it, and why your approach will work. This is the heart of your proposal.",
      tips: [
        "Describe your innovative methodology",
        "Explain how you'll address RFP requirements",
        "Include risk mitigation strategies",
        "Show how you'll measure and report progress"
      ]
    },
    timeline: {
      title: "Timeline & Implementation",
      description: "Provide a clear schedule showing when you'll accomplish key milestones and deliverables.",
      tips: [
        "Create realistic milestones",
        "Include buffer time for challenges",
        "Show how you'll maintain momentum",
        "Demonstrate sustainability planning"
      ]
    },
    budget: {
      title: "Budget & Financial Plan",
      description: "Detail how you'll use the requested funds and show cost-effectiveness. Align with RFP funding requirements.",
      tips: [
        "Align every line item with RFP requirements",
        "Show cost-effectiveness through detailed breakdowns",
        "Include matching funds if required",
        "Demonstrate sustainability beyond the grant period"
      ]
    },
    evaluation: {
      title: "Evaluation & Impact Measurement",
      description: "Show how you'll measure success and demonstrate impact. Funders want to see measurable outcomes.",
      tips: [
        "Design measurable outcomes that align with RFP goals",
        "Include both quantitative and qualitative measures",
        "Plan for ongoing monitoring and reporting",
        "Show how you'll use data to improve programs"
      ]
    }
  };

  if (loading) {
    return (
      <div className="sections-container">
        <div className="loading">Loading your grant sections...</div>
      </div>
    );
  }

  return (
    <div className="sections-container">
      <div className="sections-header">
        <h2>📋 Grant Sections</h2>
        <p>Here are the key sections of your grant proposal. Click on any section to edit and improve your content.</p>
      </div>

      <div className="sections-grid">
        {Object.entries(sections).map(([sectionKey, content]) => {
          const sectionInfo = sectionDescriptions[sectionKey] || {
            title: sectionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            description: "Grant section content",
            tips: []
          };

          return (
            <div key={sectionKey} className="section-card">
              <div className="section-header">
                <h3>{sectionInfo.title}</h3>
                <p className="section-description">{sectionInfo.description}</p>
              </div>

              <div className="section-content">
                {editingSection === sectionKey ? (
                  <div className="edit-mode">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      placeholder={`Write your ${sectionInfo.title.toLowerCase()} here...`}
                      rows={8}
                    />
                    <div className="edit-actions">
                      <button 
                        className="btn btn-primary"
                        onClick={() => handleSave(sectionKey)}
                      >
                        Save
                      </button>
                      <button 
                        className="btn btn-secondary"
                        onClick={handleCancel}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="view-mode">
                    <div className="content-preview">
                      {content || `No content yet. Click 'Edit' to start writing your ${sectionInfo.title.toLowerCase()}.`}
                    </div>
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleEdit(sectionKey, content)}
                    >
                      Edit Section
                    </button>
                  </div>
                )}
              </div>

              {sectionInfo.tips.length > 0 && (
                <div className="section-tips">
                  <h4>💡 Writing Tips:</h4>
                  <ul>
                    {sectionInfo.tips.map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="sections-help">
        <h3>🎯 Need Help Writing?</h3>
        <p>Go to the Chat section and ask me to help you write any specific section. I can provide guidance, examples, and suggestions tailored to your project!</p>
        <div className="help-actions">
          <button className="btn btn-secondary">
            Go to Chat
          </button>
          <button className="btn btn-primary">
            Export Grant
          </button>
        </div>
      </div>
    </div>
  );
};

export default GrantSections; 