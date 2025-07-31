import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Send as SendIcon,
  Lightbulb as LightbulbIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  Chat as ChatIcon,
  Psychology as PsychologyIcon,
  School as SchoolIcon,
  Business as BusinessIcon,
  EmojiObjects as EmojiObjectsIcon
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

// Set backend URL from Vercel or fallback to production Railway
const API_BASE = "https://ai-grant-writer-tool-production.up.railway.app";

// Debug logging for API URLs
console.log("🔧 ChatComponent API_BASE:", API_BASE);

const ChatComponent = ({ selectedProject, onNewChat }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showBrainstormDialog, setShowBrainstormDialog] = useState(false);
  const [brainstormTopic, setBrainstormTopic] = useState('');
  const [brainstormIdeas, setBrainstormIdeas] = useState([]);
  const [brainstormLoading, setBrainstormLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      console.log("🚀 Making chat API call to:", `${API_BASE}/chat/send_message`);
      const response = await fetch(`${API_BASE}/chat/send_message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          project_id: selectedProject?.id,
          message_type: 'user'
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.warn("Backend Error:", errorText);
        throw new Error("Bad response from server");
      }

      const data = await response.json();
      console.log("✅ Chat API response received:", data);

      const aiMessage = {
        id: Date.now() + 1,
        text: data.ai_response,
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Notify parent component about new chat
      if (onNewChat) {
        onNewChat({
          question: inputMessage,
          answer: data.ai_response
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleBrainstorm = async () => {
    if (!brainstormTopic.trim()) return;

    setBrainstormLoading(true);
    try {
      console.log("🚀 Making brainstorm API call to:", `${API_BASE}/chat/brainstorm`);
      const response = await fetch(`${API_BASE}/chat/brainstorm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: brainstormTopic,
          project_id: selectedProject?.id,
          focus_areas: ['mission', 'vision', 'objectives', 'strategies']
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.warn("Backend Error:", errorText);
        throw new Error("Bad response from server");
      }

      const data = await response.json();
      console.log("✅ Brainstorm API response received:", data);
      setBrainstormIdeas(data.ideas);
      setShowBrainstormDialog(true);
    } catch (error) {
      console.error('Error brainstorming:', error);
      alert('Error generating brainstorming ideas. Please try again.');
    } finally {
      setBrainstormLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const quickPrompts = [
    {
      title: "Mission & Vision",
      prompts: [
        "Help me develop a compelling mission statement for my organization",
        "What should I include in my vision statement?",
        "How can I make my mission align with the funding agency's priorities?"
      ]
    },
    {
      title: "Grant Structure",
      prompts: [
        "What's the best way to structure my specific aims section?",
        "How should I organize my methodology section?",
        "What makes a strong executive summary?"
      ]
    },
    {
      title: "Writing Quality",
      prompts: [
        "How can I make my writing more compelling and persuasive?",
        "What are common mistakes to avoid in grant writing?",
        "How can I improve the clarity of my proposal?"
      ]
    },
    {
      title: "Strategy & Planning",
      prompts: [
        "Help me develop a realistic timeline for my project",
        "What should I include in my evaluation plan?",
        "How can I demonstrate the feasibility of my approach?"
      ]
    }
  ];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ChatIcon color="primary" />
            AI Grant Writing Assistant
          </Typography>
          <Button
            variant="outlined"
            startIcon={<LightbulbIcon />}
            onClick={() => setShowBrainstormDialog(true)}
          >
            Brainstorm Ideas
          </Button>
        </Box>
        {selectedProject && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Project: {typeof selectedProject === 'object' ? selectedProject.name : selectedProject}
          </Typography>
        )}
      </Paper>

      {/* Messages Area */}
      <Paper sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ChatIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Start a conversation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask questions about grant writing, get feedback on your proposals, or brainstorm ideas.
              </Typography>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {messages.map((message) => (
                <Box
                  key={message.id}
                  sx={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                      color: message.sender === 'user' ? 'white' : 'text.primary',
                      position: 'relative'
                    }}
                  >
                    {/* ✅ Fix: Check if message.text is a string before rendering */}
                    <ReactMarkdown>
                      {typeof message.text === "string" ? message.text : JSON.stringify(message.text)}
                    </ReactMarkdown>
                    {message.sender === 'assistant' && !message.isError && (
                      <IconButton
                        size="small"
                        onClick={() => copyToClipboard(message.text)}
                        sx={{ position: 'absolute', top: 4, right: 4 }}
                      >
                        <CopyIcon fontSize="small" />
                      </IconButton>
                    )}
                    <Typography variant="caption" sx={{ mt: 1, opacity: 0.7 }}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Paper>
                </Box>
              ))}
              {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} />
                      <Typography variant="body2">AI is thinking...</Typography>
                    </Box>
                  </Paper>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>
          )}
        </Box>

        {/* Quick Prompts */}
        {messages.length === 0 && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              Quick Prompts:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {quickPrompts.map((category, idx) => (
                <Accordion key={idx} sx={{ width: '100%' }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="body2">{category.title}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {category.prompts.map((prompt, promptIdx) => (
                        <ListItem 
                          key={promptIdx} 
                          button 
                          onClick={() => setInputMessage(prompt)}
                          sx={{ py: 0.5 }}
                        >
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <PsychologyIcon fontSize="small" color="primary" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={prompt}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          </Box>
        )}

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about grant writing, get feedback, or brainstorm ideas..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || loading}
              sx={{ minWidth: 56 }}
            >
              {loading ? <CircularProgress size={20} /> : <SendIcon />}
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Brainstorming Dialog */}
      <Dialog 
        open={showBrainstormDialog} 
        onClose={() => setShowBrainstormDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <EmojiObjectsIcon color="primary" />
            Brainstorming Ideas
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Topic for brainstorming"
            value={brainstormTopic}
            onChange={(e) => setBrainstormTopic(e.target.value)}
            sx={{ mb: 2 }}
            placeholder="e.g., Mission statement, Project objectives, Implementation strategy"
          />
          <Button
            variant="contained"
            onClick={handleBrainstorm}
            disabled={!brainstormTopic.trim() || brainstormLoading}
            startIcon={brainstormLoading ? <CircularProgress size={20} /> : <LightbulbIcon />}
            sx={{ mb: 2 }}
          >
            {brainstormLoading ? 'Generating Ideas...' : 'Generate Ideas'}
          </Button>

          {brainstormIdeas.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Ideas for: {brainstormTopic}
              </Typography>
              {brainstormIdeas.map((idea, idx) => (
                <Card key={idx} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {idea.area}
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Suggestions:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {idea.suggestions.map((suggestion, sIdx) => (
                          <Chip 
                            key={sIdx} 
                            label={suggestion} 
                            size="small" 
                            variant="outlined"
                            color="primary"
                          />
                        ))}
                      </Box>
                    </Box>

                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Examples:
                      </Typography>
                      <List dense>
                        {idea.examples.map((example, eIdx) => (
                          <ListItem key={eIdx} sx={{ py: 0 }}>
                            <ListItemIcon sx={{ minWidth: 24 }}>
                              <SchoolIcon color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={example}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBrainstormDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatComponent;