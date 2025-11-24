# What This Repository Is

## Overview

The **AI Grant Writer Tool** is a comprehensive, AI-powered grant writing assistant designed to help organizations create compelling, culturally sensitive grant proposals. The tool combines advanced Retrieval-Augmented Generation (RAG) capabilities with specialized Large Language Models (LLMs) to provide context-aware, culturally competent grant writing assistance.

## Purpose

Grant writing is time-consuming and highly competitive. This tool addresses these challenges by:

- **Accelerating the grant writing process** through AI-powered content generation
- **Ensuring cultural sensitivity** and community relevance in proposals
- **Improving proposal quality** with cognitive friendliness and accessibility features
- **Streamlining workflow** from RFP analysis to final proposal export
- **Providing expert-level guidance** through RAG-powered knowledge retrieval

## Core Features

### 1. **Project Management**
- Create and manage multiple grant writing projects
- Organize projects by funding opportunity, organization, or community
- Track project history and versions

### 2. **RFP Analysis**
- Upload and analyze Request for Proposal (RFP) documents
- Extract key requirements, eligibility criteria, deadlines, and funding amounts
- Analyze organization-RFP alignment with scoring metrics
- Generate actionable recommendations

### 3. **AI-Powered Content Generation**
- Generate grant proposal sections:
  - Executive Summary
  - Organization Profile
  - Project Description & Approach
  - Timeline & Implementation
  - Budget & Financial Plan
  - Evaluation & Impact Measurement
- Context-aware content using uploaded documents and project context
- Cultural competency integration

### 4. **Intelligent Chat Assistant**
- Natural language interaction with AI assistant
- Context-aware responses using RAG (Retrieval-Augmented Generation)
- Cultural sensitivity in all responses
- Real-time quality assessment and improvement suggestions

### 5. **Document Management**
- Upload and store RFP documents, organization profiles, and supporting materials
- Automatic document analysis and categorization
- Secure document storage with Supabase
- Vector embeddings for semantic search

### 6. **Cultural Competency**
- Cultural sensitivity assessment
- Community-specific content generation
- Cultural context extraction from documents
- Respect for traditional knowledge and community protocols

### 7. **Quality Assessment**
- Cognitive friendliness evaluation (readability, clarity, accessibility)
- Cultural competency scoring
- Real-time quality feedback
- Improvement recommendations

### 8. **Export & Review**
- Export proposals in multiple formats (Markdown, TXT)
- Review and approve AI-generated content
- Version control and change tracking

## Architecture

### Technology Stack

**Frontend:**
- React 18.2.0
- Modern UI/UX with responsive design
- Deployed on Vercel

**Backend:**
- FastAPI (Python web framework)
- Async/await for high performance
- Deployed on Railway

**AI & ML:**
- OpenAI GPT-3.5/GPT-4 via Vercel AI Gateway
- RAG system using ChromaDB and sentence transformers
- Advanced prompt engineering for cultural competency

**Database & Storage:**
- Supabase (PostgreSQL) for metadata and project data
- ChromaDB for vector embeddings and semantic search
- File storage for documents

**Deployment:**
- Railway (backend API)
- Vercel (frontend)
- Environment-based configuration

### System Architecture Flow

```
User Interface (React/Vercel)
    ↓
API Gateway (FastAPI/Railway)
    ↓
Core Services:
  - RAG System (ChromaDB + Sentence Transformers)
  - LLM Integration (OpenAI via Vercel AI Gateway)
  - Evaluation System (Quality & Cultural Assessment)
    ↓
Data Storage:
  - Supabase (PostgreSQL) - Metadata & Projects
  - ChromaDB - Vector Embeddings
  - File Storage - Documents
```

## Repository Structure

```
AI-Grant-Writer-Tool/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── App.js              # Main application component
│   │   ├── ChatComponent.js    # AI chat interface
│   │   ├── GrantSections.js    # Grant section management
│   │   ├── NavigationComponent.js
│   │   └── ApprovalComponent.js
│   ├── public/
│   ├── package.json
│   └── build/                  # Production build
│
├── src/                        # Backend Python source code
│   ├── main.py                 # FastAPI application entry point
│   ├── middleware.py           # Request middleware
│   └── utils/                  # Utility modules
│       ├── rag_utils.py        # Basic RAG functionality
│       ├── advanced_rag_utils.py  # Advanced RAG with cultural knowledge
│       ├── openai_utils.py     # OpenAI API integration
│       ├── vercel_ai_utils.py  # Vercel AI Gateway integration
│       ├── supabase_utils.py   # Supabase database operations
│       ├── storage_utils.py    # Data models and storage
│       ├── rfp_analysis.py     # RFP document analysis
│       ├── evaluation_utils.py # Quality assessment
│       ├── file_utils.py       # File handling utilities
│       └── embedding_utils.py  # Vector embedding generation
│
├── data/                       # Sample data and knowledge base
│   ├── organizations/          # Organization profiles
│   ├── communities/            # Community profiles
│   ├── cultural/               # Cultural engagement guidelines
│   └── knowledge/              # Best practices and examples
│
├── pgvector/                   # Database schema and migrations
│   ├── init.sql                # Database initialization
│   ├── secure_storage.sql      # Secure storage schema
│   └── rag_context_retrieval.sql
│
├── supabase/                   # Supabase Edge Functions
│   └── functions/
│       └── rag_context/         # RAG context retrieval function
│
├── config/                     # Configuration files
│
├── requirements.txt            # Python dependencies
├── nixpacks.toml              # Railway deployment config
├── railway.json               # Railway configuration
│
└── Documentation files:
    ├── README.md               # Quick start guide
    ├── ENVIRONMENT_SETUP.md    # Environment configuration
    ├── REQUIREMENTS_AND_ARCHITECTURE.md  # Detailed architecture
    ├── TECHNICAL_DESIGN.md     # Technical specifications
    ├── LAUNCH_GUIDE.md         # How to launch the application
    └── ... (other documentation)
```

## How to Use This Repository

### Prerequisites

1. **Python 3.8+** for backend
2. **Node.js 16+** for frontend
3. **API Keys:**
   - OpenAI API key
   - Supabase project URL and service key
   - Vercel AI Gateway key (optional but recommended)

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/eltphd/AI-Grant-Writer-Tool.git
cd AI-Grant-Writer-Tool
```

#### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (see ENVIRONMENT_SETUP.md)
export OPENAI_API_KEY=your_key
export SUPABASE_URL=your_url
export SUPABASE_KEY=your_key
export AI_GATEWAY_API_KEY=your_key

# Run the backend server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

#### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

### User Workflow

1. **Onboarding**
   - Sign in/out (if authentication is enabled)
   - Create or select a project

2. **Project Setup**
   - Upload RFP documents
   - Upload organization profiles and supporting documents
   - Set project context and initiative description

3. **RFP Analysis**
   - Upload RFP document
   - Review extracted requirements and eligibility criteria
   - Analyze organization-RFP alignment

4. **Content Generation**
   - Use chat to brainstorm ideas
   - Auto-generate grant sections
   - Review and refine generated content

5. **Quality Assessment**
   - Review cultural competency scores
   - Check cognitive friendliness metrics
   - Apply improvement recommendations

6. **Export**
   - Review complete proposal
   - Export in desired format (Markdown, TXT)
   - Save for final submission

### Deployment

#### Railway (Backend)

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (or `SUPABASE_SERVICE_KEY`)
   - `AI_GATEWAY_API_KEY`
3. Railway will auto-deploy on push to main branch

#### Vercel (Frontend)

1. Connect your GitHub repository to Vercel
2. Set build directory to `frontend`
3. Set environment variables:
   - `REACT_APP_API_URL` (your Railway backend URL)
4. Deploy

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed configuration.

## Key Technologies & Dependencies

### Backend Dependencies

- **FastAPI**: Modern Python web framework
- **OpenAI**: GPT models for content generation
- **ChromaDB**: Vector database for RAG
- **Sentence Transformers**: Embedding generation
- **LangChain**: LLM orchestration (optional)
- **Supabase**: Database and storage
- **PyPDF2**: PDF document processing
- **python-docx**: Word document processing

### Frontend Dependencies

- **React**: UI framework
- **React Scripts**: Build tooling
- **AI SDK**: Vercel AI integration

## Data Organization

### Knowledge Base Structure

The repository includes sample data and knowledge bases:

- **Organizations**: Sample organization profiles with mission, accomplishments, partnerships
- **Communities**: Community profiles with cultural context and engagement guidelines
- **Cultural Guidelines**: Best practices for culturally sensitive grant writing
- **Grant Examples**: Sample grant narratives and best practices

### Database Schema

- **Projects**: Grant writing projects
- **Organizations**: Organization profiles
- **RFPs**: RFP documents and analysis results
- **Files**: Uploaded documents with embeddings
- **Project Responses**: Generated grant content

## Key Features Explained

### RAG (Retrieval-Augmented Generation)

The tool uses RAG to provide context-aware responses:
1. Documents are converted to vector embeddings
2. User queries are matched against document embeddings
3. Relevant context is retrieved
4. LLM generates responses using retrieved context

This ensures responses are grounded in your actual documents and project context.

### Cultural Competency

The system includes:
- Cultural knowledge base with community-specific guidelines
- Cultural sensitivity assessment
- Community voice integration
- Respect for traditional knowledge protocols

### Cognitive Friendliness

Content is evaluated for:
- Readability (Flesch Reading Ease, Gunning Fog, SMOG)
- Clarity (sentence length, jargon detection)
- Accessibility (structure, examples, positive language)
- Cultural accessibility

## Development

### Running Tests

```bash
# Backend tests
python test_integration.py
python test_approval_workflow.py
python test_railway.py
```

### Code Structure

- **Modular design**: Utilities separated by functionality
- **Error handling**: Graceful fallbacks when dependencies unavailable
- **Type hints**: Python type annotations for better code quality
- **Documentation**: Comprehensive docstrings and comments

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Documentation

- **[README.md](README.md)**: Quick start and overview
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)**: Environment configuration
- **[REQUIREMENTS_AND_ARCHITECTURE.md](REQUIREMENTS_AND_ARCHITECTURE.md)**: Detailed architecture
- **[TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md)**: Technical specifications
- **[LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)**: How to launch the application
- **[ABOUT.md](ABOUT.md)**: Project overview and philosophy

## Support & Resources

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See the `/docs` directory for detailed guides
- **API Docs**: Available at `/docs` endpoint when backend is running

## License

This project is licensed under the MIT License.

---

**Built with ❤️ for the grant-writing community.**

