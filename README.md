# AI Grant Writer Tool

AI Grant Writer Tool is an end-to-end, container-native platform that lets researchers, non-profits and consultants draft, iterate and polish competitive grant proposals in minutes. It combines cutting-edge Large-Language-Model agents (Microsoft AutoGen + LangChain) with Retrieval-Augmented Generation, backed by PostgreSQL/pgvector for lightning-fast semantic search. A FastAPI micro-service and a Streamlit analytics dashboard power the API layer, while a modern React/Material-UI front-end delivers a seamless experience — all orchestrated by a single Docker Compose file.

## 🚀 Features

### Core Functionality
- **AI-Powered Grant Writing**: Get intelligent assistance for creating compelling grant proposals
- **Interactive Chat**: Real-time conversations with AI for grant writing assistance and brainstorming
- **Document Analysis**: Upload and analyze grant documents using RAG technology
- **Interactive Q&A**: Ask questions about your grant proposals and get AI-powered responses
- **Project Management**: Create and manage multiple grant writing projects
- **Client Management**: Associate projects with specific clients

### Enhanced User Experience
- **Step-by-Step Workflow**: Intuitive guided process for grant writing
- **Modern UI**: Beautiful, responsive interface built with Material-UI
- **Template Prompts**: Pre-built prompts for common grant writing tasks
- **Resource Integration**: Built-in access to grant writing best practices
- **Real-time Feedback**: Loading states and progress indicators

### AI Integration
- **Microsoft AutoGen**: Advanced AI agent for grant writing assistance
- **RAG Technology**: Retrieval-Augmented Generation for context-aware responses
- **Vector Database**: PostgreSQL with pgvector for efficient document storage and retrieval
- **LangChain**: Framework for building AI applications

## 🛠️ Technology Stack

### Frontend
- **React.js**: Modern UI framework
- **Material-UI**: Professional design system
- **Axios**: HTTP client for API communication

### Backend
- **FastAPI**: High-performance Python web framework
- **Streamlit**: Data science web app framework
- **PostgreSQL**: Primary database with pgvector extension

### AI & ML
- **Microsoft AutoGen**: AI agent framework
- **LangChain**: LLM application framework
- **pgvector**: Vector similarity search

### Infrastructure
- **Docker**: Containerization for easy deployment
- **Docker Compose**: Multi-container orchestration

## ⚙️ Build & Deployment

The entire platform is **container-native** — no local Python or Node setup required.

```bash
# Spin up PostgreSQL/pgvector, FastAPI, Streamlit & React dev server
docker compose up --build
```

Hot-reloading is enabled by default for both Python and React services, so every code change is reflected instantly.

### Production

Deploy to any container host (Railway, Render, Azure Container Apps, ECS, etc.) by simply pushing this repository and running the same Compose file. An example Railway service is provided via `railway.json`.

### CI/CD

Ready for GitHub Actions — add your secrets (`OPENAI_API_KEY`, `DATABASE_URL`) and trigger on `main` to automatically build and publish an image to GHCR or Docker Hub.

## 📦 Installation

### Prerequisites
- Docker and Docker Compose
- Node.js (for frontend development)
- Python 3.8+ (for backend development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/eltphd/AI-Grant-Writer-Tool.git
   cd AI-Grant-Writer-Tool
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Start the application with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - FastAPI: http://localhost:8000
   - Streamlit: http://localhost:8501

## 🎯 Usage Guide

### Getting Started

1. **Create a Project**
   - Enter a project name and description
   - Optionally select a client
   - Click "Create Project" to begin

2. **Upload Documents**
   - Upload relevant grant documents (PDF, DOC, TXT)
   - The system will process and index your documents
   - Documents are stored in the vector database for AI analysis

3. **Ask Questions**
   - Use the AI assistant to get help with your grant writing
   - Try template prompts for common tasks
   - Get personalized recommendations based on your documents

4. **Interactive Chat & Brainstorming**
   - Engage in real-time conversations with the AI assistant
   - Brainstorm ideas for mission statements, vision statements, and project objectives
   - Get feedback on your grant writing in a conversational format
   - Use quick prompts for common grant writing scenarios

### Template Prompts

The application includes pre-built prompts for common grant writing tasks:

- **Enhance Text Clarity**: Improve readability and understanding
- **Make Text More Compelling**: Create persuasive content
- **Improve Structure and Flow**: Organize content effectively
- **Align with Funding Agency**: Match agency requirements
- **Develop Strong Grant Title**: Create attention-grabbing titles
- **Identify Challenges**: Anticipate reviewer concerns
- **Develop Timeline**: Create realistic project timelines

### Resources Integration

The tool integrates with leading grant writing resources:

- **[AI for Grant Writing](https://www.lizseckel.com/ai-for-grant-writing/)**: Curated resources for AI-assisted grant writing
- **[Grant Writing Support Tool](https://github.com/ekatraone/Grant-Writing-Support-Tool)**: AI-powered organization profiling

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm start
```

### Backend Development
```bash
# FastAPI
cd fastapi
pip install -r requirements.txt
uvicorn src.main:app --reload

# Streamlit
cd streamlit
streamlit run src/main.py
```

### Database Setup
```bash
# Initialize PostgreSQL with pgvector
docker-compose up pgvector
```

## 📁 Project Structure

```
AI-Grant-Writer-Tool/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── App.js           # Main application component
│   │   └── index.js         # Application entry point
│   ├── public/
│   └── package.json         # Frontend dependencies
├── fastapi/                  # FastAPI backend
│   └── src/
│       ├── main.py          # FastAPI application
│       └── utils/           # Utility modules
├── streamlit/               # Streamlit interface
│   └── src/
│       ├── main.py          # Streamlit application
│       └── utils/           # Utility modules
├── pgvector/               # Database setup
│   ├── init.sql            # Database initialization
│   └── output/             # Database output directory
├── docker-compose.yaml     # Docker orchestration
├── Dockerfile              # Docker configuration
└── requirements.txt        # Python dependencies
```

## 🎨 UI/UX Improvements

### Modern Design
- **Material-UI Components**: Professional, accessible design system
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark/Light Theme Support**: Built-in theme switching
- **Loading States**: Clear feedback during operations
- **Error Handling**: User-friendly error messages

### User Experience
- **Step-by-Step Workflow**: Guided process reduces confusion
- **Template Prompts**: Quick access to proven prompts
- **Resource Integration**: Built-in access to best practices
- **Copy-to-Clipboard**: Easy sharing of AI responses
- **File Upload Progress**: Visual feedback for uploads

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast**: Accessible color schemes
- **Focus Management**: Clear focus indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AI for Grant Writing](https://www.lizseckel.com/ai-for-grant-writing/) for comprehensive grant writing resources
- [Grant Writing Support Tool](https://github.com/ekatraone/Grant-Writing-Support-Tool) for inspiration and best practices
- Microsoft AutoGen team for the AI agent framework
- LangChain team for the LLM application framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the troubleshooting guide

---

**Built with ❤️ for the grant writing community** 