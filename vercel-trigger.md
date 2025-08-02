# Vercel Deployment Trigger

This file is used to trigger Vercel deployments.

Last updated: $(date)

## Deployment Status
- Frontend: React app with API integration
- Backend: Railway deployment at https://ai-grant-writer-tool-production.up.railway.app
- Environment: Production

## Environment Variables Required
- REACT_APP_API_URL=https://ai-grant-writer-tool-production.up.railway.app
- AI_GATEWAY_API_KEY=@ai_gateway_api_key

## Build Configuration
- Framework: Create React App
- Build Command: cd frontend && npm install && npm run build
- Output Directory: frontend/build 