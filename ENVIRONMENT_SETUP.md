# Environment Variables Setup Guide

This guide explains how to configure the required environment variables for the AI Grant Writer Tool.

## Required Environment Variables

### Railway (Backend)
Add these environment variables in your Railway project settings:

```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key_here
USE_SUPABASE=true
```

### Vercel (Frontend)
Add these environment variables in your Vercel project settings:

```
REACT_APP_API_URL=https://ai-grant-writer-tool-production.up.railway.app
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
USE_SUPABASE=true
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
```

## How to Get These Keys

### 1. OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Supabase Keys
1. Go to [Supabase](https://supabase.com/)
2. Create a new project or use existing one
3. Go to Settings > API
4. Copy the "Project URL" (for SUPABASE_URL)
5. Copy the "service_role" key (for SUPABASE_KEY)

### 3. Vercel AI Key
1. Go to [Vercel AI Gateway](https://vercel.com/ai)
2. Sign in with your Vercel account
3. Go to "Integrations" tab
4. Add your OpenAI API key as an integration
5. Copy the generated Vercel AI key

## Deployment Platforms

### Railway (Recommended for Backend)
- Railway handles environment variables securely
- No need for .env files in production
- Variables are encrypted and secure

### Vercel (Frontend)
- Vercel automatically handles environment variables
- Variables prefixed with `REACT_APP_` are available to the frontend
- Secure and encrypted storage

### GitHub (Optional)
- Only needed if you want to use GitHub Actions for CI/CD
- Store secrets in GitHub repository settings
- Not required for basic deployment

## Troubleshooting

### "AI_GATEWAY_API_KEY not found" Error
1. Make sure you've added the Vercel AI Gateway key to Railway environment variables
2. Verify the key is correct in Vercel AI Gateway
3. Restart your Railway deployment after adding the variable

### Projects Not Saving
1. Check that SUPABASE_URL and SUPABASE_KEY are correct
2. Verify your Supabase project has the required tables
3. Check Railway logs for database connection errors

### RFP Analysis Errors
1. Ensure OPENAI_API_KEY is set correctly
2. Check that AI_GATEWAY_API_KEY is configured
3. Verify the API endpoints are working

## Security Notes

- Never commit API keys to your repository
- Use environment variables for all sensitive data
- Railway and Vercel provide secure storage for these variables
- Rotate keys regularly for security

## Quick Setup Checklist

- [ ] OpenAI API key added to Railway
- [ ] Supabase URL and key added to Railway  
- [ ] AI_GATEWAY_API_KEY added to Railway
- [ ] REACT_APP_API_URL added to Vercel
- [ ] Railway deployment restarted
- [ ] Test project creation
- [ ] Test RFP upload and analysis
- [ ] Test chat functionality 