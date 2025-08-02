#!/bin/bash

# Vercel Deployment Debug Script
echo "🚀 Starting Vercel deployment debug..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check project structure
echo "📁 Checking project structure..."
if [ -f "frontend/package.json" ]; then
    echo "✅ frontend/package.json found"
else
    echo "❌ frontend/package.json not found"
    exit 1
fi

if [ -f "vercel.json" ]; then
    echo "✅ vercel.json found"
else
    echo "❌ vercel.json not found"
    exit 1
fi

# Check if we're in a git repository
if [ -d ".git" ]; then
    echo "✅ Git repository found"
else
    echo "❌ Not in a git repository"
    exit 1
fi

# Try to deploy
echo "🚀 Attempting Vercel deployment..."
vercel --prod

echo "✅ Deployment script completed" 