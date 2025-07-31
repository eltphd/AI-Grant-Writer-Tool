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
  Alert,
  Avatar,
  Grid,
  Fab,
  Tooltip
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
  EmojiObjects as EmojiObjectsIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon
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

  // Add welcome message when component mounts
  useEffect(() => {
    if (selectedProject && messages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        text: `Hello! I'm your AI grant writing assistant. I'm here to help you with grant writing questions, brainstorming ideas, and providing personalized advice based on your project: "${selectedProject.name}". 

What would you like to know about grant writing?`,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        isWelcome: true
      };
      setMessages([welcomeMessage]);
    }
  }, [selectedProject]);

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
      const response = await fetch(`${API_BASE}/chat/brainstorm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: brainstormTopic,
          project_id: selectedProject?.id
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate ideas");
      }

      const data = await response.json();
      setBrainstormIdeas(data);
      setBrainstormTopic('');
    } catch (error) {
      console.error('Error brainstorming:', error);
      alert('Failed to generate brainstorming ideas');
    } finally {
      setBrainstormLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.sender === 'user';
    const isWelcome = message.isWelcome;
    const isError = message.isError;

    return (
      <Box
        key={message.id}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          animation: isWelcome ? 'fadeIn 0.5s ease-in' : 'none',
          '@keyframes fadeIn': {
            '0%': { opacity: 0, transform: 'translateY(10px)' },
            '100%': { opacity: 1, transform: 'translateY(0)' }
          }
        }}
      >
        <Card
          sx={{
            maxWidth: '70%',
            backgroundColor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            border: isError ? '2px solid #f44336' : 'none',
            boxShadow: isWelcome ? 4 : 1,
            position: 'relative'
          }}
        >
          <CardContent sx={{ p: 2, pb: '16px !important' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: isUser ? 'primary.dark' : 'secondary.main'
                }}
              >
                {isUser ? <PersonIcon /> : <SmartToyIcon />}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  {isUser ? 'You' : 'AI Assistant'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </Box>
              {!isUser && (
                <IconButton
                  size="small"
                  onClick={() => copyToClipboard(message.text)}
                  sx={{ color: 'text.secondary' }}
                >
                  <CopyIcon fontSize="small" />
                </IconButton>
              )}
            </Box>
            
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                lineHeight: 1.6,
                '& p': { margin: 0 },
                '& ul, & ol': { margin: '8px 0', paddingLeft: '20px' }
              }}
            >
              <ReactMarkdown>{message.text}</ReactMarkdown>
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ mb: 2, p: 2, backgroundColor: 'background.paper', borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          AI Grant Writing Assistant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Project: {selectedProject?.name}
        </Typography>
      </Box>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          backgroundColor: 'grey.50',
          borderRadius: 1,
          mb: 2,
          minHeight: '400px',
          maxHeight: '500px'
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <ChatIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Start a conversation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ask questions about grant writing or use the brainstorm feature
            </Typography>
          </Box>
        ) : (
          messages.map(renderMessage)
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ p: 2, backgroundColor: 'background.paper', borderRadius: 1 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about grant writing, get feedback, or brainstorm ideas..."
              disabled={loading}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            >
              {loading ? 'Sending...' : 'Send'}
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Brainstorming Dialog */}
      <Dialog 
        open={showBrainstormDialog} 
        onClose={() => setShowBrainstormDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LightbulbIcon color="primary" />
            Brainstorming Ideas
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Topic for brainstorming"
            value={brainstormTopic}
            onChange={(e) => setBrainstormTopic(e.target.value)}
            placeholder="e.g., mission statement, budget planning, evaluation methods..."
            sx={{ mb: 3, mt: 1 }}
          />
          
          <Button
            variant="contained"
            onClick={handleBrainstorm}
            disabled={!brainstormTopic.trim() || brainstormLoading}
            startIcon={brainstormLoading ? <CircularProgress size={20} /> : <LightbulbIcon />}
            sx={{ mb: 3 }}
          >
            {brainstormLoading ? 'Generating Ideas...' : 'Generate Ideas'}
          </Button>

          {brainstormIdeas.suggestions && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Ideas for: {brainstormIdeas.topic}
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                <ReactMarkdown>{brainstormIdeas.suggestions}</ReactMarkdown>
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBrainstormDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Brainstorming */}
      <Tooltip title="Brainstorm Ideas" placement="left">
        <Fab
          color="secondary"
          aria-label="brainstorm"
          onClick={() => setShowBrainstormDialog(true)}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            zIndex: 1000
          }}
        >
          <LightbulbIcon />
        </Fab>
      </Tooltip>
    </Box>
  );
};

export default ChatComponent;