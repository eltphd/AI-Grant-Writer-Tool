// ✅ REPLACE THIS with your actual backend URL
const API_BASE = process.env.REACT_APP_API_URL || "https://ai-grant-writer-tool-production.up.railway.app";

// ...then inside your handleAskQuestion function, replace the simulated response with:

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

  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        projectId: selectedProject.id, // optional extra context
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to get AI response");
    }

    const data = await response.json();
    const aiResponse = data.result || data.answer || "No response returned.";

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

    const updatedProjects = projects.map(p =>
      p.id === selectedProject.id ? updatedProject : p
    );

    saveProjects(updatedProjects);
    setSelectedProject(updatedProject);
    setQuestion('');
    setAnswer(aiResponse);
  } catch (err) {
    console.error("Error contacting backend:", err);
    alert("There was a problem getting an AI response.");
  } finally {
    setLoading(false);
  }
};
