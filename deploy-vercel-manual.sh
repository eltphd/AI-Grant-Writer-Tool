#!/bin/bash

echo "🚀 Manual Vercel Deployment Script"
echo "=================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if we're logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please run: vercel login"
    exit 1
fi

echo "✅ Vercel CLI ready"

# Build the frontend locally first
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build completed"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment completed!"
echo "📋 Check your Vercel dashboard for the deployment status" 