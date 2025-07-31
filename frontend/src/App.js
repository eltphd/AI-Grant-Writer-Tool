import React, { useState, useEffect } from 'react';
import './App.css';
import ChatComponent from './ChatComponent';
import GrantSections from './GrantSections';

const API_BASE = "https://ai-grant-writer-tool-production.up.railway.app";

function App() {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
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
    setCurrentStep(3); // Go straight to chat for existing projects
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
          // Reload project context to show new files
          loadProjectContext(currentProject.id);
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
    
    // Automatically proceed to chat after successful upload
    setTimeout(() => {
      setCurrentStep(3);
    }, 1000);
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
    { id: 2, title: 'Upload Documents & Set Context', description: 'Add files and describe your organization and initiative' },
    { id: 3, title: 'Interactive Chat & AI Assistant', description: 'Everything you need in one powerful chat interface' },
    { id: 4, title: 'Grant Application Sections', description: 'Build your complete grant application with structured sections' }
  ];

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">📋</span>
            GWAT
          </h1>
          <p className="app-subtitle">Grant Writing Assisted Toolkit</p>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="progress-container">
        <div className="progress-steps">
          {steps.map((step, index) => (
            <div 
              key={step.id} 
              className={`progress-step ${currentStep >= step.id ? 'active' : ''} ${currentStep === step.id ? 'current' : ''}`}
              onClick={() => {
                // Allow navigation to any step if a project is selected
                if (currentProject || step.id === 1) {
                  setCurrentStep(step.id);
                }
              }}
              style={{ cursor: (currentProject || step.id === 1) ? 'pointer' : 'default' }}
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

        {/* Step 2: Document Upload & Context Setup */}
        {currentStep === 2 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Upload Documents & Set Context</h2>
              <p>Add files and describe your organization and initiative for better AI assistance</p>
            </div>
            
            <div className="context-and-upload-section">
              {/* Context Form */}
              <div className="context-form">
                <h3>📝 Project Information</h3>
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
                </div>
              </div>
              
              {/* File Upload */}
              <div className="upload-section">
                <h3>📁 Upload Documents</h3>
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
                      <h4>Drop files here or click to browse</h4>
                      <p>Supports PDF, DOCX, TXT, and MD files (max 10MB each)</p>
                      <p className="upload-note">Files are automatically processed for privacy protection</p>
                    </div>
                  </label>
                </div>
                
                {fileUploadLoading && (
                  <div className="loading-indicator">
                    <div className="spinner"></div>
                    <p>Uploading and processing files...</p>
                  </div>
                )}
              </div>
              
              {/* Continue to Chat */}
              <div className="continue-section">
                <button 
                  className="btn btn-primary btn-large"
                  onClick={() => setCurrentStep(3)}
                >
                  🚀 Start Chat & AI Assistant
                </button>
                <p className="continue-note">
                  You can always come back to add more documents or update context
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Main Chat Interface */}
        {currentStep === 3 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Interactive Chat & AI Assistant</h2>
              <p>Everything you need in one powerful chat interface</p>
            </div>
            
            <div className="chat-and-export-section">
              {/* Export Panel */}
              <div className="export-panel">
                <h3>📋 Export Options</h3>
                <div className="export-actions">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => setCurrentStep(4)}
                  >
                    📄 Grant Sections
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => window.open(`${API_BASE}/grant/sections/${currentProject.id}/export/markdown`, '_blank')}
                  >
                    📝 Export Markdown
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => window.open(`${API_BASE}/grant/sections/${currentProject.id}/export/docx`, '_blank')}
                  >
                    📄 Export DOCX
                  </button>
                </div>
                
                <div className="export-info">
                  <p>Quick access to your grant application sections and export options.</p>
                </div>
              </div>
              
              {/* Chat Component */}
              <div className="chat-main">
                <ChatComponent projectId={currentProject.id} />
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Grant Application Sections */}
        {currentStep === 4 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Grant Application Sections</h2>
              <p>Build your complete grant application with structured sections</p>
            </div>
            
            <GrantSections projectId={currentProject.id} />
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