// ✅ Define the API base URL (for Vercel or fallback)
const API_BASE = process.env.REACT_APP_API_URL || "https://ai-grant-writer-tool-production.up.railway.app";

// ✅ Update handleSendMessage
const handleSendMessage = async () => {
  if (!inputMessage.trim()) return;

  const userMessage = {
    id: Date.now(),
    text: inputMessage,
    sender: 'user',
    timestamp: new Date().toISOString(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInputMessage('');
  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/chat/send_message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: inputMessage,
        project_id: selectedProject?.id,
        message_type: 'user',
      }),
    });

    const data = await response.json();

    const aiMessage = {
      id: Date.now() + 1,
      text: data?.ai_response || 'No response returned.',
      sender: 'assistant',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, aiMessage]);

    if (onNewChat) {
      onNewChat({
        question: inputMessage,
        answer: aiMessage.text,
      });
    }
  } catch (error) {
    console.error('Error sending message:', error);
    const errorMessage = {
      id: Date.now() + 1,
      text: 'Sorry, I encountered an error. Please try again.',
      sender: 'assistant',
      timestamp: new Date().toISOString(),
      isError: true,
    };
    setMessages((prev) => [...prev, errorMessage]);
  } finally {
    setLoading(false);
  }
};

// ✅ Update handleBrainstorm
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
        project_id: selectedProject?.id,
        focus_areas: ['mission', 'vision', 'objectives', 'strategies'],
      }),
    });

    const data = await response.json();
    setBrainstormIdeas(data?.ideas || []);
    setShowBrainstormDialog(true);
  } catch (error) {
    console.error('Error brainstorming:', error);
    alert('Error generating brainstorming ideas. Please try again.');
  } finally {
    setBrainstormLoading(false);
  }
};