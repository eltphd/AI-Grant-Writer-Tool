import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [clients, setClients] = useState([]);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [clientId, setClientId] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [fileName, setFileName] = useState('');
  const [file, setFile] = useState(null);

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
    try {
      await axios.post('/create_project', null, {
        params: {
          project_name: projectName,
          project_description: projectDescription,
          client_id: clientId || null,
        },
      });
      alert('Project created successfully');
      setProjectName('');
      setProjectDescription('');
    } catch (err) {
      console.error('Error creating project:', err);
      alert('Failed to create project');
    }
  };

  // Upload a file and split into chunks
  const handleFileUpload = async () => {
    if (!file || !fileName) {
      alert('Please provide a file name and select a file');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file_name', fileName);
      formData.append('file', file);
      await axios.post('/file_upload_chunks', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('File uploaded');
      setFile(null);
      setFileName('');
      // Reset file input value
      const input = document.getElementById('fileInput');
      if (input) input.value = '';
    } catch (err) {
      console.error('Error uploading file:', err);
      alert('File upload failed');
    }
  };

  // Ask a question using the RAG agent
  const handleAskQuestion = async () => {
    try {
      const formData = new FormData();
      formData.append('question', question);
      const res = await axios.post('/ask_auto_gen_question', formData);
      // The API returns a tuple of (answer, context).  For simplicity,
      // display the raw JSON for now.
      setAnswer(JSON.stringify(res.data));
    } catch (err) {
      console.error('Error asking question:', err);
      alert('Error asking question');
    }
  };

  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>AI Grant Writer</h1>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Create Project</h2>
        <div style={{ marginBottom: '0.5rem' }}>
          <input
            type="text"
            placeholder="Project name"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <input
            type="text"
            placeholder="Project description"
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <select
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          >
            <option value="">Select client</option>
            {clients &&
              clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
          </select>
          <button onClick={handleCreateProject}>Create Project</button>
        </div>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Upload File</h2>
        <div style={{ marginBottom: '0.5rem' }}>
          <input
            type="text"
            placeholder="File name (e.g., document.pdf)"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <input
            id="fileInput"
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ marginRight: '0.5rem' }}
          />
          <button onClick={handleFileUpload}>Upload</button>
        </div>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Ask Question</h2>
        <div style={{ marginBottom: '0.5rem' }}>
          <textarea
            rows={3}
            cols={50}
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <button onClick={handleAskQuestion}>Ask</button>
        </div>
        {answer && (
          <div>
            <h3>Answer</h3>
            <pre>{answer}</pre>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;