# AI Grant Writer Tool

A comprehensive AI-powered grant writing assistant that helps organizations create compelling grant proposals with cultural sensitivity and community engagement.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Supabase project
- Vercel AI Gateway key

### Environment Setup
See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed configuration instructions.

### Local Development
```bash
# Clone the repository
git clone https://github.com/eltphd/AI-Grant-Writer-Tool.git
cd AI-Grant-Writer-Tool

# Start the application
docker-compose up --build
```

### Production Deployment
The application is configured for deployment on Railway (backend) and Vercel (frontend).

## 🔧 Key Features

- **Project Management**: Create and manage multiple grant projects
- **RFP Analysis**: Upload and analyze Request for Proposal documents
- **AI-Powered Writing**: Generate grant sections with cultural sensitivity
- **Community Engagement**: Tailored content for diverse communities
- **Export Options**: Export proposals in multiple formats

## 📋 Environment Variables

### Railway (Backend)
```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key
```

### Vercel (Frontend)
```
REACT_APP_API_BASE=https://your-railway-app-name.up.railway.app
```

## 🏗️ Architecture

- **Backend**: FastAPI with PostgreSQL/pgvector for RAG
- **Frontend**: React with modern UI/UX
- **AI**: OpenAI GPT-4 with Vercel AI Gateway
- **Database**: Supabase with vector embeddings
- **Deployment**: Railway + Vercel

## 📚 Documentation

- [Environment Setup](ENVIRONMENT_SETUP.md)
- [Technical Design](TECHNICAL_DESIGN.md)
- [Requirements & Architecture](REQUIREMENTS_AND_ARCHITECTURE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 