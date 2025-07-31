import React, { useState, useEffect } from 'react';
import './App.css';
import ChatComponent from './ChatComponent';

const API_BASE = "https://ai-grant-writer-tool-production.up.railway.app";

function App() {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [projectContext, setProjectContext] = useState({});
  const [showContextDialog, setShowContextDialog] = useState(false);
  const [contextLoading, setContextLoading] = useState(false);
  const [fileUploadLoading, setFileUploadLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [organizationInfo, setOrganizationInfo] = useState('');
  const [initiativeDescription, setInitiativeDescription] = useState('');

  // Debug logging
  console.log('🔧 App.js: API_BASE configured as:', API_BASE);
  console.log('🔧 Environment check:', process.env);

  useEffect(() => {
    // Load projects from localStorage
    const savedProjects = localStorage.getItem('grantProjects');
    if (savedProjects) {
      setProjects(JSON.parse(savedProjects));
    }
  }, []);

  const saveProjects = (newProjects) => {
    setProjects(newProjects);
    localStorage.setItem('grantProjects', JSON.stringify(newProjects));
  };

  const createProject = () => {
    const projectName = prompt('Enter project name:');
    if (projectName) {
      const newProject = {
        id: Date.now().toString(),
        name: projectName,
        createdAt: new Date().toISOString()
      };
      const updatedProjects = [...projects, newProject];
      saveProjects(updatedProjects);
      setCurrentProject(newProject);
      setCurrentStep(2);
    }
  };

  const selectProject = (project) => {
    setCurrentProject(project);
    setCurrentStep(2);
    loadProjectContext(project.id);
  };

  const loadProjectContext = async (projectId) => {
    setContextLoading(true);
    try {
      const response = await fetch(`${API_BASE}/context/${projectId}`);
      const context = await response.json();
      setProjectContext(context);
      if (context.organization_info) setOrganizationInfo(context.organization_info);
      if (context.initiative_description) setInitiativeDescription(context.initiative_description);
    } catch (error) {
      console.error('Error loading context:', error);
    } finally {
      setContextLoading(false);
    }
  };

  const handleSaveContext = async () => {
    if (!currentProject) return;
    
    setContextLoading(true);
    try {
      const response = await fetch(`${API_BASE}/context/${currentProject.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_info: organizationInfo,
          initiative_description: initiativeDescription
        })
      });
      
      if (response.ok) {
        alert('Context saved successfully!');
        setShowContextDialog(false);
        setCurrentStep(3);
      } else {
        alert('Failed to save context');
      }
    } catch (error) {
      console.error('Error saving context:', error);
      alert('Error saving context');
    } finally {
      setContextLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    setFileUploadLoading(true);

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', currentProject.id);

      try {
        const response = await fetch(`${API_BASE}/upload`, {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        if (result.success) {
          console.log(`✅ File uploaded: ${file.name}`);
        } else {
          console.error(`❌ Upload failed for ${file.name}:`, result.error);
        }
      } catch (error) {
        console.error(`❌ Error uploading ${file.name}:`, error);
      }
    }

    setFileUploadLoading(false);
    setSelectedFiles([]);
    event.target.value = '';
    setCurrentStep(4);
  };

  const handleSubmit = async () => {
    if (!question.trim() || !currentProject) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          projectId: currentProject.id
        })
      });
      
      const data = await response.json();
      setResponse(data.result || data.error || 'No response received');
      setCurrentStep(5);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error connecting to the server');
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      const updatedProjects = projects.filter(p => p.id !== projectId);
      saveProjects(updatedProjects);
      if (currentProject && currentProject.id === projectId) {
        setCurrentProject(null);
        setCurrentStep(1);
      }
    }
  };

  const steps = [
    { id: 1, title: 'Create or Select Project', description: 'Start a new grant project or continue existing work' },
    { id: 2, title: 'Set Up Project Context', description: 'Describe your organization and initiative' },
    { id: 3, title: 'Upload Documents', description: 'Add relevant files for AI context' },
    { id: 4, title: 'Ask Questions & Get AI Responses', description: 'Generate grant content with AI assistance' },
    { id: 5, title: 'Review & Manage Responses', description: 'View and manage your AI-generated content' },
    { id: 6, title: 'Interactive Chat & Brainstorming', description: 'Engage in dynamic conversations and idea generation' }
  ];

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">🎯</span>
            AI Grant Writer
          </h1>
          <p className="app-subtitle">Professional grant writing with AI assistance</p>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="progress-container">
        <div className="progress-steps">
          {steps.map((step, index) => (
            <div 
              key={step.id} 
              className={`progress-step ${currentStep >= step.id ? 'active' : ''} ${currentStep === step.id ? 'current' : ''}`}
            >
              <div className="step-number">{step.id}</div>
              <div className="step-info">
                <div className="step-title">{step.title}</div>
                <div className="step-description">{step.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="app-main">
        {/* Step 1: Project Selection */}
        {currentStep === 1 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Create or Select Project</h2>
              <p>Start a new grant project or continue with an existing one</p>
            </div>
            
            <div className="project-grid">
              {projects.map(project => (
                <div key={project.id} className="project-card" onClick={() => selectProject(project)}>
                  <div className="project-icon">📋</div>
                  <div className="project-info">
                    <h3>{project.name}</h3>
                    <p>Created: {new Date(project.createdAt).toLocaleDateString()}</p>
                  </div>
                  <button 
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteProject(project.id);
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))}
              
              <div className="project-card new-project" onClick={createProject}>
                <div className="project-icon">➕</div>
                <div className="project-info">
                  <h3>Create New Project</h3>
                  <p>Start a new grant writing project</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Context Setup */}
        {currentStep === 2 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Set Up Project Context</h2>
              <p>Describe your organization and the initiative you're seeking funding for</p>
            </div>
            
            <div className="context-form">
              <div className="form-group">
                <label>Organization Information</label>
                <textarea
                  value={organizationInfo}
                  onChange={(e) => setOrganizationInfo(e.target.value)}
                  placeholder="Describe your organization, its mission, history, and key achievements..."
                  rows={4}
                />
              </div>
              
              <div className="form-group">
                <label>Initiative Description</label>
                <textarea
                  value={initiativeDescription}
                  onChange={(e) => setInitiativeDescription(e.target.value)}
                  placeholder="Describe the specific initiative or project you're seeking funding for..."
                  rows={4}
                />
              </div>
              
              <div className="form-actions">
                <button 
                  className="btn btn-primary"
                  onClick={handleSaveContext}
                  disabled={contextLoading}
                >
                  {contextLoading ? 'Saving...' : 'Save Context'}
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => setCurrentStep(3)}
                >
                  Skip to Upload
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: File Upload */}
        {currentStep === 3 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Upload Documents</h2>
              <p>Add relevant files to provide context for AI responses</p>
            </div>
            
            <div className="upload-section">
              <div className="upload-area">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.docx,.doc,.txt,.md"
                  onChange={handleFileUpload}
                  id="file-upload"
                  className="file-input"
                />
                <label htmlFor="file-upload" className="upload-label">
                  <div className="upload-icon">📁</div>
                  <div className="upload-text">
                    <h3>Drop files here or click to browse</h3>
                    <p>Supports PDF, DOCX, TXT, and MD files (max 10MB each)</p>
                  </div>
                </label>
              </div>
              
              {fileUploadLoading && (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Uploading files...</p>
                </div>
              )}
              
              <div className="upload-actions">
                <button 
                  className="btn btn-primary"
                  onClick={() => setCurrentStep(4)}
                >
                  Continue to Questions
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Q&A */}
        {currentStep === 4 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Ask Questions & Get AI Responses</h2>
              <p>Ask specific questions about your grant and receive AI-generated responses</p>
            </div>
            
            <div className="qa-section">
              <div className="question-input">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a specific question about your grant, e.g., 'Write an executive summary for our youth program grant'"
                  rows={4}
                />
                <button 
                  className="btn btn-primary"
                  onClick={handleSubmit}
                  disabled={loading || !question.trim()}
                >
                  {loading ? 'Generating...' : 'Get AI Response'}
                </button>
              </div>
              
              {response && (
                <div className="response-section">
                  <h3>AI Response:</h3>
                  <div className="response-content">
                    {response}
                  </div>
                </div>
              )}
              
              <div className="qa-actions">
                <button 
                  className="btn btn-secondary"
                  onClick={() => setCurrentStep(6)}
                >
                  Go to Chat
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Review Responses */}
        {currentStep === 5 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Review & Manage Responses</h2>
              <p>View and manage your AI-generated content</p>
            </div>
            
            <div className="review-section">
              {response && (
                <div className="response-card">
                  <h3>Latest Response</h3>
                  <div className="response-content">
                    {response}
                  </div>
                  <div className="response-actions">
                    <button className="btn btn-secondary">Copy</button>
                    <button className="btn btn-secondary">Edit</button>
                    <button className="btn btn-secondary">Save</button>
                  </div>
                </div>
              )}
              
              <div className="review-actions">
                <button 
                  className="btn btn-primary"
                  onClick={() => setCurrentStep(4)}
                >
                  Ask Another Question
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => setCurrentStep(6)}
                >
                  Go to Chat
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 6: Chat Component */}
        {currentStep === 6 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Interactive Chat & Brainstorming</h2>
              <p>Engage in dynamic conversations and generate ideas</p>
            </div>
            
            <ChatComponent projectId={currentProject.id} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>&copy; 2024 AI Grant Writer. Professional grant writing with AI assistance.</p>
      </footer>
    </div>
  );
}

export default App;