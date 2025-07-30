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
  Grid
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
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import ChatComponent from './ChatComponent';

// Set backend URL from Vercel or fallback to production Railway
const API_BASE = process.env.REACT_APP_API_URL || "https://ai-grant-writer-tool-production.up.railway.app";

// Optional: console log for debugging
if (!process.env.NODE_ENV || process.env.NODE_ENV !== "production") {
  console.log("Using API base:", API_BASE);
}

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
    setActiveStep(1);
  };

  const handleSelectProject = (project) => {
    setSelectedProject(project);
    setActiveStep(1);
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
    
    setEditingProject(null);
    setNewProjectName('');
    setShowProjectDialog(false);
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
        const text = await response.text();
        console.warn("Backend returned error response:", text);
        throw new Error("Backend error");
      }

      const data = await response.json();

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
    alert('Copied to clipboard!');
  };

  const steps = [
    'Create or Select Project',
    'Ask Questions & Get AI Responses',
    'Review & Manage Responses',
    'Interactive Chat & Brainstorming'
  ];

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h5" gutterBottom>
              Welcome to AI Grant Writer Tool
            </Typography>
            <Typography variant="body1" paragraph>
              Create a new project or select an existing one to get started with AI-powered grant writing assistance.
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowProjectDialog(true)}
                sx={{ mb: 2 }}
              >
                Create New Project
              </Button>
            </Box>

            {projects.length > 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Existing Projects:
                </Typography>
                <List>
                  {projects.map((project) => (
                    <ListItem
                      key={project.id}
                      sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1,
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                    >
                      <ListItemText
                        primary={project.name}
                        secondary={`${project.questions.length} questions • Created ${new Date(project.createdAt).toLocaleDateString()}`}
                      />
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="outlined"
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
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h5" gutterBottom>
              Ask Questions
            </Typography>
            <Typography variant="body1" paragraph>
              Selected Project: {typeof selectedProject === 'object' ? selectedProject.name : selectedProject}
            </Typography>
            
            <Paper sx={{ p: 2, mb: 2 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Ask a question about grant writing"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., How do I write a compelling executive summary?"
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={handleAskQuestion}
                disabled={!question.trim() || loading}
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              >
                {loading ? 'Getting Response...' : 'Ask Question'}
              </Button>
            </Paper>

            {answer && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  AI Response:
                </Typography>
                <Typography variant="body1" paragraph>
                  {answer}
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<CopyIcon />}
                  onClick={() => copyToClipboard(answer)}
                >
                  Copy Response
                </Button>
              </Paper>
            )}
          </Box>
        );

      case 2:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h5" gutterBottom>
              Review Responses
            </Typography>
            <Typography variant="body1" paragraph>
              Project: {typeof selectedProject === 'object' ? selectedProject.name : selectedProject}
            </Typography>
            
            {selectedProject && selectedProject.questions.length > 0 ? (
              <List>
                {selectedProject.questions.map((q, index) => (
                  <ListItem key={q.id} sx={{ mb: 2, flexDirection: 'column', alignItems: 'stretch' }}>
                    <Card sx={{ width: '100%' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Question {index + 1}:
                        </Typography>
                        <Typography variant="body1" paragraph>
                          {q.question}
                        </Typography>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="h6" gutterBottom>
                          AI Response:
                        </Typography>
                        <Typography variant="body1" paragraph>
                          {q.answer}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<CopyIcon />}
                            onClick={() => copyToClipboard(q.answer)}
                          >
                            Copy Response
                          </Button>
                          <Typography variant="caption" sx={{ alignSelf: 'center' }}>
                            {new Date(q.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="info">
                No questions have been asked yet. Go back to step 2 to ask your first question.
              </Alert>
            )}
          </Box>
        );

      case 3:
        return (
          <Box sx={{ mt: 3, height: '600px' }}>
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
      <Typography variant="h3" component="h1" gutterBottom align="center">
        AI Grant Writer Tool
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {renderStepContent(activeStep)}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          disabled={activeStep === 0}
          onClick={() => setActiveStep((prevActiveStep) => prevActiveStep - 1)}
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
      <Dialog open={showProjectDialog} onClose={() => setShowProjectDialog(false)}>
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