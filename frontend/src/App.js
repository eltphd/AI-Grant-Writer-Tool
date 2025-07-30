// Set backend URL from Vercel or fallback to production Railway
const API_BASE =
  process.env.REACT_APP_API_URL || "https://ai-grant-writer-tool-production.up.railway.app";

// Optional: console log for debugging
if (!process.env.NODE_ENV || process.env.NODE_ENV !== "production") {
  console.log("Using API base:", API_BASE);
}

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