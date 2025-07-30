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
  DialogActions,
  Tabs,
  Tab,
  RadioGroup,
  Radio,
  FormControlLabel
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
  Info as InfoIcon,
  Folder as FolderIcon,
  Mic as MicIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

function App() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [fileName, setFileName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [showResources, setShowResources] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [showPromptDialog, setShowPromptDialog] = useState(false);
  const [projectMode, setProjectMode] = useState('new'); // 'new' or 'existing'
  const [showProjectSelector, setShowProjectSelector] = useState(false);

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

  // Integrated support tools content
  const supportTools = {
    'Text Enhancement': {
      title: 'AI Text Enhancement',
      description: 'Improve your grant writing with AI-powered text analysis and suggestions.',
      features: [
        'Grammar and spelling correction',
        'Clarity improvement suggestions',
        'Tone and style optimization',
        'Readability analysis'
      ],
      tips: [
        'Use specific, concrete language instead of vague terms',
        'Break down complex sentences into shorter, clearer ones',
        'Use active voice to make your writing more direct',
        'Include specific examples to illustrate your points'
      ]
    },
    'Structure Optimization': {
      title: 'Proposal Structure Guide',
      description: 'Organize your grant proposal for maximum impact and readability.',
      features: [
        'Logical flow recommendations',
        'Section organization tips',
        'Transition improvement',
        'Content hierarchy guidance'
      ],
      tips: [
        'Start with a compelling executive summary',
        'Use clear headings and subheadings',
        'Ensure each section builds on the previous one',
        'End with a strong conclusion that reinforces your main points'
      ]
    },
    'Agency Alignment': {
      title: 'Funding Agency Alignment',
      description: 'Align your proposal with specific funding agency missions and priorities.',
      features: [
        'Mission statement analysis',
        'Priority area identification',
        'Language adaptation',
        'Reviewer perspective insights'
      ],
      tips: [
        'Research the funding agency\'s mission and values',
        'Use language that resonates with their priorities',
        'Address their specific evaluation criteria',
        'Demonstrate alignment with their strategic goals'
      ]
    },
    'Voice-to-Text Processing': {
      title: 'Voice Note Processing',
      description: 'Convert your voice notes to text for easier proposal development.',
      features: [
        'Real-time voice transcription',
        'Note organization tools',
        'Text editing capabilities',
        'Integration with proposal drafts'
      ],
      tips: [
        'Speak clearly and at a moderate pace',
        'Use voice notes for brainstorming sessions',
        'Review and edit transcribed text',
        'Organize notes by topic or section'
      ]
    }
  };

  // Load existing projects from localStorage
  useEffect(() => {
    const savedProjects = localStorage.getItem('grantProjects');
    if (savedProjects) {
      setProjects(JSON.parse(savedProjects));
    }
  }, []);

  // Save projects to localStorage
  const saveProjects = (updatedProjects) => {
    localStorage.setItem('grantProjects', JSON.stringify(updatedProjects));
    setProjects(updatedProjects);
  };

  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      alert('Please enter a project name');
      return;
    }

    const newProject = {
      id: Date.now(),
      name: projectName,
      description: projectDescription,
      createdAt: new Date().toISOString(),
      files: [],
      notes: [],
      questions: []
    };

    const updatedProjects = [...projects, newProject];
    saveProjects(updatedProjects);
    setSelectedProject(newProject);
    setProjectName('');
    setProjectDescription('');
    setActiveStep(1);
  };

  const handleSelectExistingProject = (project) => {
    setSelectedProject(project);
    setShowProjectSelector(false);
    setActiveStep(1);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    if (!selectedProject) {
      alert('Please create or select a project first');
      return;
    }

    setLoading(true);
    
    // Simulate file upload
    setTimeout(() => {
      const newFile = {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString()
      };

      const updatedProject = {
        ...selectedProject,
        files: [...selectedProject.files, newFile]
      };

      const updatedProjects = projects.map(p => 
        p.id === selectedProject.id ? updatedProject : p
      );

      saveProjects(updatedProjects);
      setSelectedProject(updatedProject);
      setFile(null);
      setFileName('');
      setLoading(false);
    }, 2000);
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }

    if (!selectedProject) {
      alert('Please create or select a project first');
      return;
    }

    setLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = `Based on your question about "${question}", here's my analysis and recommendations:

1. **Key Considerations**: Your question touches on important aspects of grant writing that require careful attention.

2. **Best Practices**: 
   - Focus on clear, specific language
   - Provide concrete examples
   - Align with funding agency priorities
   - Demonstrate measurable outcomes

3. **Next Steps**: Consider how this advice applies to your specific project context and funding opportunity.

Would you like me to elaborate on any of these points or help you apply this to your specific grant proposal?`;

      const newQuestion = {
        id: Date.now(),
        question: question,
        answer: aiResponse,
        timestamp: new Date().toISOString()
      };

      const updatedProject = {
        ...selectedProject,
        questions: [...selectedProject.questions, newQuestion]
      };

      const updatedProjects = projects.map(p => 
        p.id === selectedProject.id ? updatedProject : p
      );

      saveProjects(updatedProjects);
      setSelectedProject(updatedProject);
      setQuestion('');
      setAnswer(aiResponse);
      setLoading(false);
    }, 2000);
  };

  const handlePromptSelect = (prompt) => {
    setQuestion(prompt);
    setShowPromptDialog(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const steps = [
    {
      label: 'Create or Select Project',
      description: 'Start a new project or continue working on an existing one',
      content: (
        <Box sx={{ mt: 2 }}>
          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <RadioGroup
              value={projectMode}
              onChange={(e) => setProjectMode(e.target.value)}
            >
              <FormControlLabel 
                value="new" 
                control={<Radio />} 
                label="Create New Project" 
              />
              <FormControlLabel 
                value="existing" 
                control={<Radio />} 
                label="Continue Existing Project" 
              />
            </RadioGroup>
          </FormControl>

          {projectMode === 'new' ? (
            <Box>
              <TextField
                fullWidth
                label="Project Name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                sx={{ mb: 2 }}
                placeholder="e.g., NIH R01 Application"
              />
              <TextField
                fullWidth
                label="Project Description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                multiline
                rows={3}
                sx={{ mb: 2 }}
                placeholder="Brief description of your grant proposal"
              />
              <Button
                variant="contained"
                onClick={handleCreateProject}
                startIcon={<AddIcon />}
              >
                Create Project
              </Button>
            </Box>
          ) : (
            <Box>
              {projects.length === 0 ? (
                <Alert severity="info">
                  No existing projects found. Create your first project above.
                </Alert>
              ) : (
                <Box>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Select a project to continue working on:
                  </Typography>
                  <Grid container spacing={2}>
                    {projects.map((project) => (
                      <Grid item xs={12} md={6} key={project.id}>
                        <Card 
                          sx={{ 
                            cursor: 'pointer',
                            '&:hover': { backgroundColor: 'action.hover' }
                          }}
                          onClick={() => handleSelectExistingProject(project)}
                        >
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {project.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                              {project.description}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              <Chip 
                                icon={<DescriptionIcon />} 
                                label={`${project.files.length} files`} 
                                size="small" 
                              />
                              <Chip 
                                icon={<QuestionIcon />} 
                                label={`${project.questions.length} Q&A`} 
                                size="small" 
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </Box>
          )}
        </Box>
      )
    },
    {
      label: 'Upload Documents & Add Notes',
      description: 'Upload relevant documents and add voice or text notes',
      content: (
        <Box sx={{ mt: 2 }}>
          {selectedProject ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                Project: {selectedProject.name}
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Upload Documents
                      </Typography>
                      <input
                        type="file"
                        onChange={(e) => setFile(e.target.files[0])}
                        style={{ marginBottom: '16px' }}
                      />
                      <Button
                        variant="contained"
                        onClick={handleFileUpload}
                        disabled={!file || loading}
                        startIcon={<UploadIcon />}
                        fullWidth
                      >
                        {loading ? <CircularProgress size={20} /> : 'Upload File'}
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Add Voice Notes
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Record voice notes that will be converted to text for your proposal
                      </Typography>
                      <Button
                        variant="outlined"
                        startIcon={<MicIcon />}
                        fullWidth
                      >
                        Record Voice Note
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {selectedProject.files.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Uploaded Files
                  </Typography>
                  <Grid container spacing={2}>
                    {selectedProject.files.map((file) => (
                      <Grid item xs={12} sm={6} md={4} key={file.id}>
                        <Card>
                          <CardContent>
                            <Typography variant="body2" noWrap>
                              {file.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(file.uploadedAt).toLocaleDateString()}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </Box>
          ) : (
            <Alert severity="warning">
              Please create or select a project first.
            </Alert>
          )}
        </Box>
      )
    },
    {
      label: 'Get AI Assistance',
      description: 'Ask questions and get AI-powered grant writing assistance',
      content: (
        <Box sx={{ mt: 2 }}>
          {selectedProject ? (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Ask AI Assistant
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        label="Your Question"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        sx={{ mb: 2 }}
                        placeholder="Ask about grant writing, structure, clarity, or any other aspect..."
                      />
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Button
                          variant="outlined"
                          onClick={() => setShowPromptDialog(true)}
                          startIcon={<LightbulbIcon />}
                        >
                          Use Template Prompts
                        </Button>
                        <Button
                          variant="contained"
                          onClick={handleAskQuestion}
                          disabled={!question.trim() || loading}
                          startIcon={<QuestionIcon />}
                        >
                          {loading ? <CircularProgress size={20} /> : 'Ask Question'}
                        </Button>
                      </Box>
                      
                      {answer && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="h6" gutterBottom>
                            AI Response:
                          </Typography>
                          <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                            <ReactMarkdown>{answer}</ReactMarkdown>
                            <Button
                              size="small"
                              onClick={() => copyToClipboard(answer)}
                              startIcon={<CopyIcon />}
                              sx={{ mt: 1 }}
                            >
                              Copy Response
                            </Button>
                          </Paper>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Project Summary
                      </Typography>
                      <Typography variant="body2" paragraph>
                        <strong>Name:</strong> {selectedProject.name}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        <strong>Description:</strong> {selectedProject.description}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        <strong>Files:</strong> {selectedProject.files.length}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        <strong>Questions:</strong> {selectedProject.questions.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {selectedProject.questions.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Previous Q&A
                  </Typography>
                  <Accordion>
                    {selectedProject.questions.map((qa) => (
                      <Accordion key={qa.id}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography variant="body2" noWrap>
                            {qa.question.substring(0, 100)}...
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <ReactMarkdown>{qa.answer}</ReactMarkdown>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Accordion>
                </Box>
              )}
            </Box>
          ) : (
            <Alert severity="warning">
              Please create or select a project first.
            </Alert>
          )}
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

      {/* Integrated Support Tools Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Grant Writing Support Tools
        </Typography>
        <Grid container spacing={3}>
          {Object.entries(supportTools).map(([key, tool]) => (
            <Grid item xs={12} md={6} key={key}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {tool.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {tool.description}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Features:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {tool.features.map((feature, idx) => (
                        <Chip key={idx} label={feature} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Tips:
                    </Typography>
                    <List dense>
                      {tool.tips.map((tip, idx) => (
                        <ListItem key={idx} sx={{ py: 0 }}>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <CheckCircleIcon color="primary" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={tip}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </CardContent>
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
    </Container>
  );
}

export default App;