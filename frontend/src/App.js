import React, { useState, useEffect } from 'react';
import './App.css';
import ChatComponent from './ChatComponent';
import GrantSections from './GrantSections';
import NavigationComponent from './NavigationComponent';
import ApprovalComponent from './ApprovalComponent';

const API_BASE = process.env.REACT_APP_API_BASE || (window.location.hostname === 'localhost' ? 'http://localhost:8080' : '');

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
  const [uploadStatus, setUploadStatus] = useState({ message: '', type: '' });

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
    if (!currentProject) {
      setUploadStatus({
        message: '❌ Please select or create a project before uploading.',
        type: 'error'
      });
      return;
    }

    try {
      setLoading(true);
      setUploadStatus({ message: '', type: '' });
      
      let successCount = 0;
      let errorCount = 0;
      
      for (const file of files) {
        try {
          // Read file content
          const { content, is_base64 } = await readFileContent(file);
          
          // Upload file as JSON (matching backend expectation)
          const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              project_id: currentProject.id,
              file: {
                filename: file.name,
                content,
                is_base64
              }
            }),
          });

          if (response.ok) {
            const result = await response.json();
            if (result.success) {
              successCount++;
              console.log(`File ${file.name} uploaded successfully`);
            } else {
              errorCount++;
              console.error(`Failed to upload ${file.name}:`, result.error);
            }
          } else {
            errorCount++;
            console.error(`HTTP error uploading ${file.name}:`, response.status);
          }
        } catch (error) {
          errorCount++;
          console.error(`Error uploading ${file.name}:`, error);
        }
      }

      // Show upload status
      if (successCount > 0 && errorCount === 0) {
        setUploadStatus({ 
          message: `✅ Successfully uploaded ${successCount} file(s)`, 
          type: 'success' 
        });
      } else if (successCount > 0 && errorCount > 0) {
        setUploadStatus({ 
          message: `⚠️ Uploaded ${successCount} file(s), ${errorCount} failed`, 
          type: 'warning' 
        });
      } else {
        setUploadStatus({ 
          message: `❌ Failed to upload ${errorCount} file(s)`, 
          type: 'error' 
        });
      }

      // Clear status after 5 seconds
      setTimeout(() => setUploadStatus({ message: '', type: '' }), 5000);

      // Reload project context to show uploaded files
      await loadProjectContext(currentProject.id);
    } catch (error) {
      console.error('Error uploading files:', error);
      setUploadStatus({ 
        message: `❌ Error uploading files: ${error.message}`, 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRFPUpload = async (file) => {
    if (!currentProject) {
      setUploadStatus({
        message: '❌ Please select or create a project before uploading.',
        type: 'error'
      });
      return;
    }

    try {
      setLoading(true);
      setUploadStatus({ message: '', type: '' });
      
      // Read file content
      const { content, is_base64 } = await readFileContent(file);
      
      // Upload RFP for analysis
      const response = await fetch(`${API_BASE}/rfp/upload/${currentProject.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          is_base64,

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
          setUploadStatus({ 
            message: `✅ RFP uploaded successfully! Analysis complete.`, 
            type: 'success' 
          });
          
          // Clear status after 5 seconds
          setTimeout(() => setUploadStatus({ message: '', type: '' }), 5000);
        } else {
          setUploadStatus({ 
            message: `❌ RFP upload failed: ${result.error}`, 
            type: 'error' 
          });
        }
      } else {
        setUploadStatus({ 
          message: `❌ RFP upload failed: HTTP ${response.status}`, 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error('Error uploading RFP file:', error);
      setUploadStatus({ 
        message: `❌ Error uploading RFP file: ${error.message}`, 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onerror = reject;
      // For binary files (PDF, DOCX) we read as ArrayBuffer and convert to base64 string
      if (file.type === "application/pdf" || file.name.endsWith(".pdf") || file.name.endsWith(".doc") || file.name.endsWith(".docx")) {
        reader.readAsArrayBuffer(file);
        reader.onload = (e) => {
          const buffer = e.target.result;
          const binary = new Uint8Array(buffer).reduce((acc, byte) => acc + String.fromCharCode(byte), "");
          const base64String = btoa(binary);
          resolve({ content: base64String, is_base64: true });
        };
      } else {
        reader.readAsText(file);
        reader.onload = (e) => {
          resolve({ content: e.target.result, is_base64: false });
        };
      }

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

  const handleEditSection = async (sectionKey) => {
    try {
      setLoading(true);
      
      // Create a more specific prompt for section generation
      const sectionPrompts = {
        'executive_summary': 'Generate a comprehensive executive summary for our grant proposal. Include our organization background, project goals, funding request, and expected impact.',
        'organization_profile': 'Write a detailed organization profile section. Include our mission, history, key accomplishments, leadership team, and capacity to deliver this project.',
        'project_approach': 'Create a detailed project description and approach section. Include SMART objectives, activities, timeline, staffing plan, and key partnerships.',
        'timeline': 'Develop a comprehensive timeline and implementation plan. Include milestones, deliverables, and project phases.',
        'budget': 'Create a detailed budget and financial plan section. Include cost breakdown, justifications, and sustainability plan.',
        'evaluation': 'Write an evaluation and impact measurement section. Include KPIs, data collection methods, and reporting schedule.'
      };
      
      const prompt = sectionPrompts[sectionKey] || `Generate content for the ${sectionKey.replace('_', ' ')} section of our grant proposal.`;
      
      // Call the AI to generate content for this section
      const response = await fetch(`${API_BASE}/chat/send_message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: currentProject?.id || 'test-project',
          message: prompt
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Update the section with AI-generated content
          setSections(prev => ({
            ...prev,
            [sectionKey]: data.response
          }));
          
          // Show success message
          setUploadStatus({ 
            message: `✅ ${sectionKey.replace('_', ' ')} section generated successfully!`, 
            type: 'success' 
          });
          
          // Clear status after 3 seconds
          setTimeout(() => setUploadStatus({ message: '', type: '' }), 3000);
        } else {
          setUploadStatus({ 
            message: `❌ Failed to generate ${sectionKey.replace('_', ' ')} section: ${data.error}`, 
            type: 'error' 
          });
        }
      } else {
        console.error('Failed to generate section content:', response.status);
        setUploadStatus({ 
          message: `❌ Failed to generate ${sectionKey.replace('_', ' ')} section. Please try again.`, 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error('Error generating section content:', error);
      setUploadStatus({ 
        message: `❌ Error generating ${sectionKey.replace('_', ' ')} section: ${error.message}`, 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStepChange = (stepId) => {
    setCurrentStep(stepId);
  };

  const handleExportMarkdown = async () => {
    try {
      const response = await fetch(`${API_BASE}/export/markdown`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: currentProject?.id || 'test-project',
          sections: sections
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'grant-proposal.md';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Export failed:', response.status);
        alert('Export failed. Please try again.');
      }
    } catch (error) {
      console.error('Error exporting:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleExportDocx = async () => {
    try {
      const response = await fetch(`${API_BASE}/export/txt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: currentProject?.id || 'test-project',
          sections: sections
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'grant-proposal.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Export failed:', response.status);
        alert('Export failed. Please try again.');
      }
    } catch (error) {
      console.error('Error exporting:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleReviewSections = () => {
    setCurrentStep(2); // Go back to the grant creation page
  };

  return (
    <div className="app">
      <NavigationComponent 
        currentStep={currentStep} 
        onStepChange={handleStepChange}
      />

      <div style={{ 
        padding: '1rem', 
        backgroundColor: '#0070f3', 
        color: 'white', 
        textAlign: 'center', 
        fontWeight: 'bold' 
      }}>
        Friday, August 1, 2025
      </div>

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
                <h3>📄 Document Upload</h3>
                
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
                  
                  {/* Upload Status Display */}
                  {uploadStatus.message && uploadStatus.type && (
                    <div className={`upload-status ${uploadStatus.type}`}>
                      {uploadStatus.message}
                    </div>
                  )}
                  
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
                          disabled={loading}
                        >
                          {loading ? 'Generating...' : 'Auto-Generate'}
                        </button>
                      </div>
                      
                      <div className="section-content">
                        {sections[sectionKey] || `No content yet. Click 'Auto-Generate' to create your ${sectionTitle.toLowerCase()} using AI.`}
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
              <ChatComponent projectId={currentProject?.id || 'test-project'} />
            </div>
          </div>
        )}

        {/* Step 4: Content Approval */}
        {currentStep === 4 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Content Approval Workflow</h2>
              <p>Review and approve AI-generated content that contains sensitive information</p>
            </div>
            
            <div className="approval-panel">
              <ApprovalComponent 
                projectId={currentProject?.id || 'test-project'} 
                onApprovalUpdate={() => {
                  // Refresh any necessary data after approval updates
                  console.log('Approval workflow updated');
                }}
              />
            </div>
          </div>
        )}

        {/* Step 5: Export & Review */}
        {currentStep === 5 && (
          <div className="step-container">
            <div className="step-header">
              <h2>Review & Export</h2>
              <p>Review your complete grant proposal and export it</p>
            </div>
            
            <div className="export-panel">
              <h3>📄 Your Grant Proposal</h3>
              <p>Review your completed grant proposal before exporting.</p>
              
              <div className="export-actions">
                <button className="btn btn-primary" onClick={handleExportMarkdown}>
                  📝 Export as Markdown
                </button>
                <button className="btn btn-primary" onClick={handleExportDocx}>
                  📄 Export as TXT
                </button>
                <button className="btn btn-secondary" onClick={handleReviewSections}>
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