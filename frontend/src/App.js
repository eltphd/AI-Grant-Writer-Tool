import React, { useState, useEffect } from 'react';
import './App.css';
import ChatComponent from './ChatComponent';
import GrantSections from './GrantSections';
import NavigationComponent from './NavigationComponent';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://ai-grant-writer-tool-production.up.railway.app';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [organizationInfo, setOrganizationInfo] = useState('');
  const [initiativeDescription, setInitiativeDescription] = useState('');
  const [projectContext, setProjectContext] = useState({ files: [] });

  // Load projects on app load (no auth required)
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await fetch(`${API_BASE}/projects`);

      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects || []);
      } else {
        console.error('Failed to load projects:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const createProject = async () => {
    try {
      setLoading(true);
      const projectData = {
        name: `Grant Project ${Date.now()}`,
        description: 'New grant writing project'
      };

      const response = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData),
      });

      if (response.ok) {
        const data = await response.json();
        setProjects([...projects, data.project]);
        setCurrentProject(data.project);
        setCurrentStep(2);
      }
    } catch (error) {
      console.error('Error creating project:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectProject = (project) => {
    setCurrentProject(project);
    setCurrentStep(3); // Go straight to chat for existing projects
    loadProjectContext(project.id);
  };

  const loadProjectContext = async (projectId) => {
    try {
      const response = await fetch(`${API_BASE}/context/${projectId}`);
      if (response.ok) {
        const data = await response.json();
        setProjectContext(data.context || { files: [] });
      }
    } catch (error) {
      console.error('Error loading project context:', error);
    }
  };

  const handleFileUpload = async (files) => {
    if (!currentProject) return;

    try {
      setLoading(true);
      
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', currentProject.id);

        const response = await fetch(`${API_BASE}/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            console.log(`File ${file.name} uploaded successfully`);
          }
        }
      }

      setCurrentStep(3);
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProjectContext = async () => {
    if (!currentProject) return;

    try {
      const response = await fetch(`${API_BASE}/context/${currentProject.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_info: organizationInfo,
          initiative_description: initiativeDescription,
        }),
      });

      if (response.ok) {
        console.log('Project context updated successfully');
      }
    } catch (error) {
      console.error('Error updating project context:', error);
    }
  };

  const handleStepChange = (stepId) => {
    setCurrentStep(stepId);
  };

  return (
    <div className="app">
      <NavigationComponent 
        currentStep={currentStep} 
        onStepChange={handleStepChange}
      />

      <main className="app-main">
        
        {/* Step 1: Project Selection */}
        {currentStep === 1 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Your Grant Projects</h2>
              <p>Select an existing project or create a new one to get started</p>
            </div>
            
            <div className="project-grid">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="project-card"
                  onClick={() => selectProject(project)}
                >
                  <div className="project-icon">📁</div>
                  <div className="project-info">
                    <h3>{project.name}</h3>
                    <p>{project.description}</p>
                  </div>
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

        {/* Step 2: Upload & Context */}
        {currentStep === 2 && currentProject && (
          <div className="step-container">
            <div className="step-header">
              <h2>Upload Documents & Set Context</h2>
              <p>Add relevant documents and provide context for your grant project</p>
            </div>
            
            <div className="context-and-upload-section">
              <div className="context-form">
                <h3>📝 Project Context</h3>
                <div className="form-group">
                  <label htmlFor="organization">Organization Information</label>
                  <textarea
                    id="organization"
                    value={organizationInfo}
                    onChange={(e) => setOrganizationInfo(e.target.value)}
                    placeholder="Describe your organization, mission, and key accomplishments..."
                    rows={4}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="initiative">Initiative Description</label>
                  <textarea
                    id="initiative"
                    value={initiativeDescription}
                    onChange={(e) => setInitiativeDescription(e.target.value)}
                    placeholder="Describe the initiative or project you're seeking funding for..."
                    rows={4}
                  />
                </div>
                
                <button 
                  className="btn btn-primary"
                  onClick={updateProjectContext}
                >
                  Save Context
                </button>
              </div>
              
              <div className="upload-section">
                <h3>📄 Upload Documents</h3>
                <div className="upload-area">
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                    className="file-input"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="upload-label">
                    <div className="upload-icon">📤</div>
                    <div className="upload-text">
                      <h4>Drop files here or click to upload</h4>
                      <p>Supported formats: PDF, DOCX, DOC, TXT, MD</p>
                      <p className="upload-note">Max file size: 10MB</p>
                    </div>
                  </label>
                </div>
              </div>
              
              <div className="continue-section">
                <button 
                  className="btn btn-secondary btn-large"
                  onClick={() => setCurrentStep(3)}
                  disabled={loading}
                >
                  {loading ? 'Processing...' : 'Continue to Chat'}
                </button>
                <p className="continue-note">
                  You can always come back to add more context or documents later
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

        {/* Step 4: Grant Sections */}
        {currentStep === 4 && currentProject && (
          <div className="step-container">
            <GrantSections projectId={currentProject.id} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;