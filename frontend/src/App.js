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
      const newProject = {
        id: Date.now().toString(),
        name: `New Project ${projects.length + 1}`,
        description: 'A new grant writing project',
        created_at: new Date().toISOString()
      };
      
      setProjects([...projects, newProject]);
      setCurrentProject(newProject);
      setCurrentStep(2);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const selectProject = (project) => {
    setCurrentProject(project);
    setCurrentStep(2);
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

  const handleRFPUpload = async (file) => {
    if (!currentProject) return;

    try {
      setLoading(true);
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
          console.log(`RFP file ${file.name} uploaded successfully`);
        }
      }
    } catch (error) {
      console.error('Error uploading RFP file:', error);
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
        {currentStep === 2 && (
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
                    </div>
                  </label>
                </div>
                
                <div className="upload-specific">
                  <h4>📋 RFP Upload (Recommended)</h4>
                  <p>Upload the Request for Proposal (RFP) document to help AI align your response with grant requirements.</p>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={(e) => handleRFPUpload(e.target.files[0])}
                    className="file-input"
                    id="rfp-upload"
                  />
                  <label htmlFor="rfp-upload" className="upload-label rfp-upload">
                    <div className="upload-icon">📋</div>
                    <div className="upload-text">
                      <h4>Upload RFP Document</h4>
                      <p>Grant request with directions and requirements</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Chat */}
        {currentStep === 3 && (
          <div className="step-container">
            <div className="step-header">
              <h2>AI-Powered Grant Writing</h2>
              <p>Chat with AI to brainstorm ideas and get writing assistance</p>
            </div>
            
            <div className="chat-main">
              <ChatComponent />
            </div>
          </div>
        )}

        {/* Step 4: Grant Sections */}
        {currentStep === 4 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Grant Sections</h2>
              <p>View and edit structured grant sections</p>
            </div>
            
            <div className="grant-sections-main">
              <GrantSections />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;