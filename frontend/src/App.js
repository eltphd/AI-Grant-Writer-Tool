import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  Upload as UploadIcon,
  QuestionAnswer as QuestionIcon,
  Description as DescriptionIcon,
  School as SchoolIcon,
  Lightbulb as LightbulbIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

function App() {
  const [clients, setClients] = useState([]);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [clientId, setClientId] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [fileName, setFileName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [showResources, setShowResources] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [showPromptDialog, setShowPromptDialog] = useState(false);

  // Grant writing resources and prompts
  const grantWritingPrompts = {
    'Enhance Text Clarity': [
      'As a non-native English speaker, kindly help me revise the following text for improved understanding and clarity. Please check for spelling and sentence structure errors and suggest alternatives.',
      'What suggestions do you have to enhance the clarity of my text?',
      'Please identify any parts of my writing that may be difficult for a lay audience to understand.'
    ],
    'Make Text More Compelling': [
      'Please provide feedback on my writing style and how I can make it more persuasive and compelling for the grant reviewer.',
      'I\'m trying to hook my reader with a strong introduction. Can you suggest a more captivating first sentence to draw them in from the start?'
    ],
    'Improve Structure and Flow': [
      'I want to improve the overall structure of my Specific Aims. What tips do you have to structure it more effectively?',
      'Can you recommend an effective way to organize my Significance section to highlight the innovative aspects of our approach?',
      'Please provide detailed feedback on the flow and sequence of my research strategy'
    ],
    'Align with Funding Agency': [
      'I\'m working on a postdoctoral fellowship application. Can you please review my closing paragraph and suggest ways to better align it with the American Heart Association\'s mission?',
      'How can I better align my proposal to specifically address the <insert specific criteria> outlined in this funding announcement for <insert name of funding opportunity>?'
    ],
    'Develop Strong Grant Title': [
      'Suggest five potential titles for a grant proposal that will attract readers while encompassing the research question and key elements from the provided abstract <insert abstract summary>'
    ],
    'Identify Challenges': [
      'Help identify potential challenges that may arise with my proposed aims and suggest strategies to address them <insert specific aims>',
      'What are some potential questions or concerns that <funding announcement name> reviewers may have regarding my specific aims? <insert specific aims>'
    ],
    'Develop Timeline': [
      'Assist in developing a detailed project timeline and milestones for my grant proposal to demonstrate feasibility using my project summary and specific aims <insert project summary>',
      'Please develop a feasible project timeline for my grant proposal relating to my career development plan using this list of activities <insert activities> for <XX number of months> starting in <XX month>'
    ]
  };

  const grantWritingResources = [
    {
      title: 'AI for Grant Writing',
      description: 'Curated resources for using AI to develop more competitive grant applications',
      url: 'https://www.lizseckel.com/ai-for-grant-writing/',
      features: ['Prompt Collections', 'Text Enhancement', 'Structure Improvement', 'Agency Alignment']
    },
    {
      title: 'Grant Writing Support Tool',
      description: 'AI-powered tool for enhanced user interaction and organization profiling',
      url: 'https://github.com/ekatraone/Grant-Writing-Support-Tool',
      features: ['Interactive Proposals', 'Voice Processing', 'Organization Profiling', 'Template Library']
    }
  ];

  // Fetch clients on component mount
  useEffect(() => {
    axios
      .get('/get_clients')
      .then((res) => setClients(res.data || []))
      .catch((err) => {
        console.error('Error fetching clients:', err);
        setClients([]);
      });
  }, []);

  // Create a new project
  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      alert('Please enter a project name');
      return;
    }
    
    setLoading(true);
    try {
      await axios.post('/create_project', null, {
        params: {
          project_name: projectName,
          project_description: projectDescription,
          client_id: clientId || null,
        },
      });
      alert('Project created successfully!');
      setProjectName('');
      setProjectDescription('');
      setClientId('');
      setActiveStep(1);
    } catch (err) {
      console.error('Error creating project:', err);
      alert('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  // Upload a file and split into chunks
  const handleFileUpload = async () => {
    if (!file || !fileName) {
      alert('Please provide a file name and select a file');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file_name', fileName);
      formData.append('file', file);
      await axios.post('/file_upload_chunks', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('File uploaded successfully!');
      setFile(null);
      setFileName('');
      const input = document.getElementById('fileInput');
      if (input) input.value = '';
      setActiveStep(2);
    } catch (err) {
      console.error('Error uploading file:', err);
      alert('File upload failed');
    } finally {
      setLoading(false);
    }
  };

  // Ask a question using the RAG agent
  const handleAskQuestion = async () => {
    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('question', question);
      const res = await axios.post('/ask_auto_gen_question', formData);
      setAnswer(JSON.stringify(res.data, null, 2));
    } catch (err) {
      console.error('Error asking question:', err);
      alert('Error asking question');
    } finally {
      setLoading(false);
    }
  };

  const handlePromptSelect = (prompt) => {
    setSelectedPrompt(prompt);
    setQuestion(prompt);
    setShowPromptDialog(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const steps = [
    {
      label: 'Create Project',
      description: 'Start by creating a new grant writing project',
      content: (
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Project Name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name"
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Select Client</InputLabel>
                <Select
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  label="Select Client"
                >
                  <MenuItem value="">
                    <em>No client selected</em>
                  </MenuItem>
                  {clients.map((c) => (
                    <MenuItem key={c.id} value={c.id}>
                      {c.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Project Description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="Describe your grant project"
                multiline
                rows={3}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleCreateProject}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
              >
                {loading ? 'Creating...' : 'Create Project'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      )
    },
    {
      label: 'Upload Documents',
      description: 'Upload relevant documents for AI analysis',
      content: (
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="File Name"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                placeholder="e.g., grant_proposal.pdf"
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                startIcon={<UploadIcon />}
                sx={{ mt: 2 }}
              >
                Choose File
                <input
                  id="fileInput"
                  type="file"
                  hidden
                  onChange={(e) => setFile(e.target.files[0])}
                />
              </Button>
              {file && (
                <Chip
                  label={file.name}
                  onDelete={() => setFile(null)}
                  sx={{ mt: 1 }}
                />
              )}
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleFileUpload}
                disabled={loading || !file}
                startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
              >
                {loading ? 'Uploading...' : 'Upload File'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      )
    },
    {
      label: 'Ask Questions',
      description: 'Get AI-powered assistance with your grant writing',
      content: (
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => setShowPromptDialog(true)}
                  startIcon={<LightbulbIcon />}
                >
                  Use Template Prompts
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setShowResources(true)}
                  startIcon={<SchoolIcon />}
                >
                  View Resources
                </Button>
              </Box>
              <TextField
                fullWidth
                label="Ask a question about your grant"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., How can I make my specific aims more compelling?"
                multiline
                rows={4}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleAskQuestion}
                disabled={loading || !question.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <QuestionIcon />}
              >
                {loading ? 'Processing...' : 'Ask Question'}
              </Button>
            </Grid>
            {answer && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">AI Response</Typography>
                      <Tooltip title="Copy to clipboard">
                        <IconButton onClick={() => copyToClipboard(answer)}>
                          <CopyIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    <Box sx={{ 
                      backgroundColor: '#f5f5f5', 
                      p: 2, 
                      borderRadius: 1,
                      maxHeight: '400px',
                      overflow: 'auto'
                    }}>
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{answer}</pre>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </Box>
      )
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          AI Grant Writer Tool
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Intelligent grant writing assistance powered by AI
        </Typography>
        <Alert severity="info" sx={{ mt: 2, maxWidth: 600, mx: 'auto' }}>
          <Typography variant="body2">
            This tool helps you create compelling grant proposals using AI-powered analysis and 
            industry best practices. Follow the steps below to get started.
          </Typography>
        </Alert>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel>
                <Typography variant="h6">{step.label}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
              <StepContent>
                {step.content}
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Resources Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Grant Writing Resources
        </Typography>
        <Grid container spacing={2}>
          {grantWritingResources.map((resource, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {resource.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {resource.description}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {resource.features.map((feature, idx) => (
                      <Chip key={idx} label={feature} size="small" variant="outlined" />
                    ))}
                  </Box>
                </CardContent>
                <CardActions>
                  <Button size="small" href={resource.url} target="_blank">
                    Learn More
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Prompt Templates Dialog */}
      <Dialog 
        open={showPromptDialog} 
        onClose={() => setShowPromptDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Grant Writing Prompt Templates</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Use these proven prompts to get better AI assistance with your grant writing:
          </Typography>
          <Accordion>
            {Object.entries(grantWritingPrompts).map(([category, prompts]) => (
              <Accordion key={category}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">{category}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {prompts.map((prompt, idx) => (
                      <ListItem key={idx} button onClick={() => handlePromptSelect(prompt)}>
                        <ListItemIcon>
                          <LightbulbIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={prompt.substring(0, 100) + '...'}
                          secondary="Click to use this prompt"
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            ))}
          </Accordion>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPromptDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Resources Dialog */}
      <Dialog 
        open={showResources} 
        onClose={() => setShowResources(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Grant Writing Resources & Best Practices</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            AI for Grant Writing
          </Typography>
          <Typography variant="body2" paragraph>
            A curated list of resources for using AI to develop more competitive grant applications.
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Text Enhancement"
                secondary="Improve clarity and readability of your grant proposals"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Structure Improvement"
                secondary="Organize your content for maximum impact"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Agency Alignment"
                secondary="Align your proposal with funding agency missions"
              />
            </ListItem>
          </List>
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom>
            Grant Writing Support Tool
          </Typography>
          <Typography variant="body2" paragraph>
            AI-powered tool for enhanced user interaction and organization profiling.
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Interactive Proposals"
                secondary="Generate proposals through AI-powered Q&A sessions"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Voice Processing"
                secondary="Convert voice notes to text for proposal generation"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <InfoIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Organization Profiling"
                secondary="Build detailed profiles based on your organization's data"
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowResources(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;