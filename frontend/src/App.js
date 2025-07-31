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
  const [sections, setSections] = useState({
    executive_summary: '',
    organization_profile: '',
    project_approach: '',
    timeline: '',
    budget: '',
    evaluation: ''
  });

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
      
      // Read file content
      const content = await readFileContent(file);
      
      // Upload RFP for analysis
      const response = await fetch(`${API_BASE}/rfp/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: currentProject.id,
          filename: file.name,
          content: content
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log(`RFP file ${file.name} uploaded and analyzed successfully`);
          
          // Store RFP analysis result
          setCurrentProject(prev => ({
            ...prev,
            rfpAnalysis: result.rfp
          }));
          
          // Show success message
          alert(`RFP uploaded successfully! Analysis complete.`);
        }
      }
    } catch (error) {
      console.error('Error uploading RFP file:', error);
      alert('Error uploading RFP file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const analyzeRFPAlignment = async () => {
    if (!currentProject || !currentProject.rfpAnalysis) {
      alert('Please upload an RFP document first.');
      return;
    }

    try {
      setLoading(true);
      
      // Create organization profile from context
      const orgResponse = await fetch(`${API_BASE}/organization/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'My Organization',
          mission: 'To serve our community through innovative programs',
          description: organizationInfo,
          key_accomplishments: ['Program A success', 'Partnership B established'],
          partnerships: ['Local government', 'Community organizations'],
          impact_metrics: {
            'people_served': 1000,
            'programs_delivered': 5
          }
        }),
      });

      if (orgResponse.ok) {
        const orgData = await orgResponse.json();
        
        // Analyze RFP alignment
        const analysisResponse = await fetch(`${API_BASE}/rfp/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            project_id: currentProject.id,
            org_id: orgData.organization.id,
            rfp_id: currentProject.rfpAnalysis.id
          }),
        });

        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json();
          if (analysisData.success) {
            console.log('RFP analysis complete:', analysisData.analysis);
            
            // Store analysis results
            setCurrentProject(prev => ({
              ...prev,
              rfpAlignment: analysisData.analysis,
              projectResponse: analysisData.response
            }));
            
            alert(`Analysis complete! Alignment score: ${analysisData.analysis.org_fit_score}%`);
          }
        }
      }
    } catch (error) {
      console.error('Error analyzing RFP alignment:', error);
      alert('Error analyzing RFP alignment. Please try again.');
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

  const handleEditSection = (sectionKey) => {
    setCurrentStep(2); // Go back to the creation step
    // In a real app, you'd pass the sectionKey to a modal or a dedicated editing component
    // For now, we'll just show a placeholder message
    alert(`Editing section: ${sectionKey}`);
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
                    <small>Created: {new Date(project.created_at).toLocaleDateString()}</small>
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

        {/* Step 2: Grant Creation (Merged Upload & Sections) */}
        {currentStep === 2 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Create Your Grant Proposal</h2>
              <p>Upload documents, set context, and write your grant sections all in one place</p>
            </div>
            
            <div className="grant-creation-layout">
              {/* Left Side - Context & Upload */}
              <div className="context-upload-panel">
                <h3>📄 Documents & Context</h3>
                
                <div className="context-form">
                  <h4>🏢 Organization Information</h4>
                  <textarea
                    value={organizationInfo}
                    onChange={(e) => setOrganizationInfo(e.target.value)}
                    placeholder="Tell me about your organization, mission, and key accomplishments..."
                    rows={4}
                  />
                </div>
                
                <div className="context-form">
                  <h4>🎯 Initiative Description</h4>
                  <textarea
                    value={initiativeDescription}
                    onChange={(e) => setInitiativeDescription(e.target.value)}
                    placeholder="Describe the project or initiative you're seeking funding for..."
                    rows={4}
                  />
                </div>
                
                <div className="upload-section">
                  <h4>📋 RFP Upload (Recommended)</h4>
                  <p>Upload the Request for Proposal document to help me align your response with grant requirements.</p>
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
                  
                  {currentProject && currentProject.rfpAnalysis && (
                    <div className="rfp-analysis-section">
                      <h4>🎯 RFP Analysis Complete</h4>
                      <p>Requirements found: {currentProject.rfpAnalysis.requirements?.length || 0}</p>
                      <p>Eligibility criteria: {currentProject.rfpAnalysis.eligibility_criteria?.length || 0}</p>
                      {currentProject.rfpAnalysis.funding_amount && (
                        <p>Funding amount: {currentProject.rfpAnalysis.funding_amount}</p>
                      )}
                      {currentProject.rfpAnalysis.deadline && (
                        <p>Deadline: {currentProject.rfpAnalysis.deadline}</p>
                      )}
                      
                      <button 
                        className="btn btn-primary"
                        onClick={analyzeRFPAlignment}
                        disabled={loading}
                      >
                        {loading ? 'Analyzing...' : 'Analyze Organization Alignment'}
                      </button>
                    </div>
                  )}
                  
                  {currentProject && currentProject.rfpAlignment && (
                    <div className="alignment-results">
                      <h4>📊 Alignment Results</h4>
                      <p><strong>Organization Fit Score:</strong> {currentProject.rfpAlignment.org_fit_score}%</p>
                      <p><strong>Overall Score:</strong> {currentProject.rfpAlignment.overall_score}%</p>
                    </div>
                  )}
                </div>
                
                <div className="upload-section">
                  <h4>📄 Additional Documents</h4>
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
              </div>
              
              {/* Right Side - Grant Sections */}
              <div className="grant-sections-panel">
                <h3>📋 Grant Sections</h3>
                <p>Write your grant proposal sections. I'll help you with guidance and suggestions!</p>
                
                <div className="sections-grid">
                  {Object.entries({
                    executive_summary: "Executive Summary",
                    organization_profile: "Organization Profile", 
                    project_approach: "Project Description & Approach",
                    timeline: "Timeline & Implementation",
                    budget: "Budget & Financial Plan",
                    evaluation: "Evaluation & Impact Measurement"
                  }).map(([sectionKey, sectionTitle]) => (
                    <div key={sectionKey} className="section-card">
                      <div className="section-header">
                        <h4>{sectionTitle}</h4>
                        <button 
                          className="btn btn-primary btn-small"
                          onClick={() => handleEditSection(sectionKey)}
                        >
                          Edit
                        </button>
                      </div>
                      
                      <div className="section-content">
                        {sections[sectionKey] || `No content yet. Click 'Edit' to start writing your ${sectionTitle.toLowerCase()}.`}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="section-help">
                  <h4>💡 Need Help Writing?</h4>
                  <p>Go to the Chat section and ask me to help you write any specific section. I can provide guidance, examples, and suggestions tailored to your project!</p>
                  <button className="btn btn-secondary" onClick={() => setCurrentStep(3)}>
                    Go to Chat
                  </button>
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

        {/* Step 4: Export & Review */}
        {currentStep === 4 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Review & Export</h2>
              <p>Review your complete grant proposal and export it</p>
            </div>
            
            <div className="export-panel">
              <h3>📄 Your Grant Proposal</h3>
              <p>Review your completed grant proposal before exporting.</p>
              
              <div className="export-actions">
                <button className="btn btn-primary">
                  📝 Export as Markdown
                </button>
                <button className="btn btn-primary">
                  📄 Export as DOCX
                </button>
                <button className="btn btn-secondary">
                  📋 Review Sections
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;