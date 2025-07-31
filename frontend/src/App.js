import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Add as AddIcon,
  Send as SendIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Chat as ChatIcon,
  Psychology as PsychologyIcon,
  Upload as UploadIcon,
  Description as DescriptionIcon,
  Business as BusinessIcon,
  Lightbulb as LightbulbIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  CloudUpload as CloudUploadIcon,
  Folder as FolderIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import ChatComponent from './ChatComponent';

// Set backend URL from Vercel or fallback to production Railway
const API_BASE = "https://ai-grant-writer-tool-production.up.railway.app";

// Debug logging for API URLs
console.log("🔧 API_BASE configured as:", API_BASE);
console.log("🔧 Environment check:", {
  NODE_ENV: process.env.NODE_ENV,
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  window_location: window.location.origin
});

// Test the backend connectivity immediately
fetch(`${API_BASE}/test`)
  .then(response => response.json())
  .then(data => console.log("✅ Backend connectivity test:", data))
  .catch(error => console.error("❌ Backend connectivity test failed:", error));

const App = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [showProjectDialog, setShowProjectDialog] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [editingProject, setEditingProject] = useState(null);
  
  // New state for enhanced UX
  const [projectContext, setProjectContext] = useState({
    organizationInfo: '',
    initiativeDescription: '',
    uploadedFiles: []
  });
  const [showContextDialog, setShowContextDialog] = useState(false);
  const [contextLoading, setContextLoading] = useState(false);
  const [fileUploadLoading, setFileUploadLoading] = useState(false);

  // Enhanced steps for better UX
  const steps = [
    'Create or Select Project',
    'Set Up Project Context',
    'Upload Documents',
    'Ask Questions & Get AI Responses',
    'Review & Manage Responses',
    'Interactive Chat & Brainstorming'
  ];

  // Load projects from localStorage on component mount
  useEffect(() => {
    const savedProjects = localStorage.getItem('grantProjects');
    if (savedProjects) {
      setProjects(JSON.parse(savedProjects));
    }
  }, []);

  // Save projects to localStorage whenever projects change
  const saveProjects = (updatedProjects) => {
    setProjects(updatedProjects);
    localStorage.setItem('grantProjects', JSON.stringify(updatedProjects));
  };

  // Load project context when project is selected
  useEffect(() => {
    if (selectedProject) {
      loadProjectContext(selectedProject.id);
    }
  }, [selectedProject]);

  const loadProjectContext = async (projectId) => {
    try {
      const response = await fetch(`${API_BASE}/context/${projectId}`);
      const context = await response.json();
      
      if (context.organization_info || context.initiative_description || context.files?.length > 0) {
        setProjectContext({
          organizationInfo: context.organization_info || '',
          initiativeDescription: context.initiative_description || '',
          uploadedFiles: context.files || []
        });
      }
    } catch (error) {
      console.error('Error loading project context:', error);
    }
  };

  const handleCreateProject = () => {
    if (!newProjectName.trim()) {
      alert('Please enter a project name');
      return;
    }

    const newProject = {
      id: Date.now(),
      name: newProjectName,
      questions: [],
      createdAt: new Date().toISOString()
    };

    const updatedProjects = [...projects, newProject];
    saveProjects(updatedProjects);
    setSelectedProject(newProject);
    setNewProjectName('');
    setShowProjectDialog(false);
    setActiveStep(1); // Move to context setup
  };

  const handleSelectProject = (project) => {
    setSelectedProject(project);
    setActiveStep(1); // Move to context setup
  };

  const handleDeleteProject = (projectId) => {
    const updatedProjects = projects.filter(p => p.id !== projectId);
    saveProjects(updatedProjects);
    if (selectedProject && selectedProject.id === projectId) {
      setSelectedProject(null);
      setActiveStep(0);
    }
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setNewProjectName(project.name);
    setShowProjectDialog(true);
  };

  const handleUpdateProject = () => {
    if (!newProjectName.trim()) {
      alert('Please enter a project name');
      return;
    }

    const updatedProjects = projects.map(p =>
      p.id === editingProject.id ? { ...p, name: newProjectName } : p
    );
    saveProjects(updatedProjects);
    
    if (selectedProject && selectedProject.id === editingProject.id) {
      setSelectedProject({ ...selectedProject, name: newProjectName });
    }
    
    setShowProjectDialog(false);
    setEditingProject(null);
    setNewProjectName('');
  };

  const handleTestConnection = async () => {
    try {
      console.log("🧪 Testing backend connection...");
      const response = await fetch(`${API_BASE}/test`);
      const data = await response.json();
      console.log("✅ Backend test successful:", data);
      alert("Backend connection successful!");
    } catch (error) {
      console.error("❌ Backend test failed:", error);
      alert("Backend connection failed: " + error.message);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      alert("Please enter a question");
      return;
    }

    if (!selectedProject) {
      alert("Please create or select a project first");
      return;
    }

    setLoading(true);

    try {
      console.log("🚀 Making API call to:", `${API_BASE}/generate`);
      const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          projectId: selectedProject?.id,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.warn("Backend Error:", errorText);
        throw new Error("Bad response from server");
      }

      const data = await response.json();
      console.log("✅ API response received:", data);

      const aiResponse = typeof data.result === "string"
        ? data.result
        : typeof data.answer === "string"
          ? data.answer
          : "No valid response returned.";

      const newQuestion = {
        id: Date.now(),
        question,
        answer: aiResponse,
        timestamp: new Date().toISOString(),
      };

      const updatedProject = {
        ...selectedProject,
        questions: [...selectedProject.questions, newQuestion],
      };

      const updatedProjects = projects.map((p) =>
        p.id === selectedProject.id ? updatedProject : p
      );

      saveProjects(updatedProjects);
      setSelectedProject(updatedProject);
      setQuestion("");
      setAnswer(aiResponse);
    } catch (err) {
      console.error("Error contacting backend:", err);
      alert("There was a problem contacting the AI backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = (chatData) => {
    if (!selectedProject) return;

    const newQuestion = {
      id: Date.now(),
      question: chatData.question,
      answer: chatData.answer,
      timestamp: new Date().toISOString(),
    };

    const updatedProject = {
      ...selectedProject,
      questions: [...selectedProject.questions, newQuestion],
    };

    const updatedProjects = projects.map((p) =>
      p.id === selectedProject.id ? updatedProject : p
    );

    saveProjects(updatedProjects);
    setSelectedProject(updatedProject);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Response copied to clipboard!");
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length || !selectedProject) return;

    setFileUploadLoading(true);
    
    for (let file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', selectedProject.id);

        const response = await fetch(`${API_BASE}/upload`, {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();
        
        if (result.success) {
          // Reload project context to get updated file list
          await loadProjectContext(selectedProject.id);
        } else {
          alert(`Failed to upload ${file.name}: ${result.error}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert(`Error uploading ${file.name}`);
      }
    }
    
    setFileUploadLoading(false);
    event.target.value = ''; // Reset file input
  };

  const handleSaveContext = async () => {
    if (!selectedProject) return;
    
    setContextLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/context/${selectedProject.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_info: projectContext.organizationInfo,
          initiative_description: projectContext.initiativeDescription,
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        setShowContextDialog(false);
        alert('Project context saved successfully!');
      } else {
        alert('Failed to save context: ' + result.error);
      }
    } catch (error) {
      console.error('Error saving context:', error);
      alert('Error saving context');
    } finally {
      setContextLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h4" gutterBottom align="center" color="primary">
              Welcome to AI Grant Writer Tool
            </Typography>
            <Typography variant="h6" paragraph align="center" color="text.secondary">
              Create a new project or select an existing one to get started with AI-powered grant writing assistance.
            </Typography>
            
            <Box sx={{ mb: 4, textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={() => setShowProjectDialog(true)}
                sx={{ mb: 2, mr: 2 }}
              >
                Create New Project
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={handleTestConnection}
                sx={{ mb: 2 }}
              >
                Test Backend Connection
              </Button>
            </Box>

            {projects.length > 0 && (
              <Box>
                <Typography variant="h5" gutterBottom>
                  Existing Projects:
                </Typography>
                <Grid container spacing={2}>
                  {projects.map((project) => (
                    <Grid item xs={12} md={6} key={project.id}>
                      <Card sx={{ 
                        '&:hover': { 
                          boxShadow: 4,
                          transform: 'translateY(-2px)',
                          transition: 'all 0.2s'
                        }
                      }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Box>
                              <Typography variant="h6" gutterBottom>
                                {project.name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {project.questions.length} questions • Created {new Date(project.createdAt).toLocaleDateString()}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Button
                                variant="contained"
                                size="small"
                                onClick={() => handleSelectProject(project)}
                              >
                                Select
                              </Button>
                              <IconButton
                                size="small"
                                onClick={() => handleEditProject(project)}
                              >
                                <EditIcon />
                              </IconButton>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteProject(project.id)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h4" gutterBottom>
              Set Up Project Context
            </Typography>
            <Typography variant="body1" paragraph color="text.secondary">
              Help the AI understand your organization and initiative for personalized grant writing advice.
            </Typography>
            
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Project: {selectedProject?.name}
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Organization Information"
                    value={projectContext.organizationInfo}
                    onChange={(e) => setProjectContext(prev => ({ ...prev, organizationInfo: e.target.value }))}
                    placeholder="Describe your organization, mission, history, key achievements, and current focus areas..."
                    helperText="This helps the AI provide more relevant and personalized grant writing advice."
                  />
                </Box>
                
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Initiative/Project Description"
                    value={projectContext.initiativeDescription}
                    onChange={(e) => setProjectContext(prev => ({ ...prev, initiativeDescription: e.target.value }))}
                    placeholder="Describe the specific initiative or project you're seeking funding for, including goals, timeline, and expected outcomes..."
                    helperText="This helps the AI understand what you're trying to accomplish and provide targeted advice."
                  />
                </Box>
                
                <Button
                  variant="contained"
                  onClick={handleSaveContext}
                  disabled={contextLoading}
                  startIcon={contextLoading ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                  {contextLoading ? 'Saving...' : 'Save Context'}
                </Button>
              </CardContent>
            </Card>
          </Box>
        );

      case 2:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h4" gutterBottom>
              Upload Documents
            </Typography>
            <Typography variant="body1" paragraph color="text.secondary">
              Upload relevant documents to provide the AI with additional context for more personalized responses.
            </Typography>
            
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Project: {selectedProject?.name}
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <input
                    accept=".pdf,.docx,.doc,.txt,.md"
                    style={{ display: 'none' }}
                    id="file-upload"
                    multiple
                    type="file"
                    onChange={handleFileUpload}
                  />
                  <label htmlFor="file-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<CloudUploadIcon />}
                      disabled={fileUploadLoading}
                      sx={{ mb: 2 }}
                    >
                      {fileUploadLoading ? 'Uploading...' : 'Upload Documents'}
                    </Button>
                  </label>
                  <Typography variant="body2" color="text.secondary">
                    Supported formats: PDF, DOCX, DOC, TXT, MD
                  </Typography>
                </Box>
                
                {projectContext.uploadedFiles.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Uploaded Documents:
                    </Typography>
                    <List>
                      {projectContext.uploadedFiles.map((file, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <DescriptionIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={file.filename}
                            secondary={`${file.extracted_text_length} characters • Uploaded ${new Date(file.uploaded_at).toLocaleDateString()}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        );

      case 3:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h4" gutterBottom>
              Ask Questions & Get AI Responses
            </Typography>
            <Typography variant="body1" paragraph color="text.secondary">
              Ask specific questions about grant writing and receive personalized advice based on your project context.
            </Typography>
            
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Project: {selectedProject?.name}
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Ask a question about grant writing"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., How do I write a compelling executive summary for my organization's mission?"
                    helperText="The AI will use your project context to provide personalized advice."
                  />
                </Box>
                
                <Button
                  variant="contained"
                  onClick={handleAskQuestion}
                  disabled={!question.trim() || loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                >
                  {loading ? 'Getting Response...' : 'Ask Question'}
                </Button>
              </CardContent>
            </Card>

            {answer && (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Response:
                  </Typography>
                  <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                    {answer}
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<CopyIcon />}
                    onClick={() => copyToClipboard(answer)}
                  >
                    Copy Response
                  </Button>
                </CardContent>
              </Card>
            )}
          </Box>
        );

      case 4:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h4" gutterBottom>
              Review & Manage Responses
            </Typography>
            <Typography variant="body1" paragraph color="text.secondary">
              Review all your previous questions and AI responses for this project.
            </Typography>
            
            {selectedProject && selectedProject.questions.length > 0 ? (
              <Grid container spacing={3}>
                {selectedProject.questions.map((q, index) => (
                  <Grid item xs={12} key={q.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                          <Typography variant="h6" color="primary">
                            Question {index + 1}
                          </Typography>
                          <Chip 
                            label={new Date(q.timestamp).toLocaleString()} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                        
                        <Accordion>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                              {q.question}
                            </Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                              {q.answer}
                            </Typography>
                            <Button
                              variant="outlined"
                              size="small"
                              startIcon={<CopyIcon />}
                              onClick={() => copyToClipboard(q.answer)}
                            >
                              Copy Response
                            </Button>
                          </AccordionDetails>
                        </Accordion>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Alert severity="info">
                No questions have been asked yet. Go back to step 4 to ask your first question.
              </Alert>
            )}
          </Box>
        );

      case 5:
        return (
          <Box sx={{ mt: 3, height: '600px' }}>
            <Typography variant="h4" gutterBottom>
              Interactive Chat & Brainstorming
            </Typography>
            <Typography variant="body1" paragraph color="text.secondary">
              Have a conversation with the AI assistant and brainstorm grant writing ideas.
            </Typography>
            <ChatComponent 
              selectedProject={selectedProject}
              onNewChat={handleNewChat}
            />
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" color="primary">
        AI Grant Writer Tool
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel 
              StepIconProps={{
                sx: {
                  color: activeStep >= index ? 'primary.main' : 'grey.400'
                }
              }}
            >
              {label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {renderStepContent(activeStep)}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          disabled={activeStep === 0}
          onClick={() => setActiveStep((prevActiveStep) => prevActiveStep - 1)}
          variant="outlined"
        >
          Back
        </Button>
        <Button
          variant="contained"
          onClick={() => setActiveStep((prevActiveStep) => prevActiveStep + 1)}
          disabled={activeStep === steps.length - 1}
        >
          Next
        </Button>
      </Box>

      {/* Project Dialog */}
      <Dialog open={showProjectDialog} onClose={() => setShowProjectDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingProject ? 'Edit Project' : 'Create New Project'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Project Name"
            fullWidth
            variant="outlined"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            sx={{ mt: 1 }}
            placeholder="e.g., Community Health Initiative Grant"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowProjectDialog(false);
            setEditingProject(null);
            setNewProjectName('');
          }}>
            Cancel
          </Button>
          <Button 
            onClick={editingProject ? handleUpdateProject : handleCreateProject}
            variant="contained"
          >
            {editingProject ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default App;