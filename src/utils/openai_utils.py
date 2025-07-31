"""OpenAI utilities for the AI Grant Writer tool.

This module provides functions for interacting with OpenAI's API to generate
grant writing assistance, brainstorming ideas, and answering questions.
"""

import os
import openai
from typing import Dict, List, Optional
from datetime import datetime

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(prompt: str, system_message: str = None, max_tokens: int = 1000) -> str:
    """Get a response from OpenAI's GPT model.
    
    Args:
        prompt: The user's question or prompt
        system_message: Optional system message to set context
        max_tokens: Maximum tokens for the response
        
    Returns:
        The AI-generated response
    """
    try:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def generate_grant_response(question: str, project_context: str = "") -> str:
    """Generate a grant writing response based on the user's question.
    
    Args:
        question: The user's question about grant writing
        project_context: Optional context about the project
        
    Returns:
        AI-generated grant writing advice
    """
    system_message = """You are an expert grant writer with years of experience helping organizations secure funding. 
    You provide practical, actionable advice for grant writing. Be specific, helpful, and encouraging. 
    Focus on best practices, common pitfalls to avoid, and step-by-step guidance."""
    
    full_prompt = f"""
    Project Context: {project_context}
    
    Question: {question}
    
    Please provide detailed, helpful advice for this grant writing question. Include specific examples and actionable steps where appropriate.
    """
    
    return get_openai_response(full_prompt, system_message)

def brainstorm_grant_ideas(topic: str, project_context: str = "") -> Dict:
    """Generate brainstorming ideas for grant writing.
    
    Args:
        topic: The topic to brainstorm about
        project_context: Optional context about the project
        
    Returns:
        Dictionary with structured brainstorming ideas
    """
    system_message = """You are a creative grant writing consultant. Generate specific, actionable ideas for grant writing.
    Organize your response into clear categories with practical suggestions and examples."""
    
    prompt = f"""
    Project Context: {project_context}
    
    Topic for brainstorming: {topic}
    
    Please provide structured brainstorming ideas organized into categories like:
    - Strategy suggestions
    - Implementation ideas  
    - Key considerations
    - Examples and case studies
    
    Make your suggestions specific and actionable.
    """
    
    response = get_openai_response(prompt, system_message, max_tokens=1500)
    
    # Parse the response into structured format
    ideas = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "suggestions": response,
        "categories": {
            "strategy": [],
            "implementation": [],
            "considerations": [],
            "examples": []
        }
    }
    
    return ideas

def chat_grant_assistant(message: str, project_context: str = "", conversation_history: List = None) -> str:
    """Handle chat-based grant writing assistance.
    
    Args:
        message: The user's message
        project_context: Optional context about the project
        conversation_history: Previous conversation messages
        
    Returns:
        AI-generated response
    """
    system_message = """You are a helpful grant writing assistant. You provide expert advice on grant writing, 
    help users brainstorm ideas, answer questions about grant requirements, and guide them through the grant writing process. 
    Be encouraging, practical, and specific in your advice."""
    
    # Build conversation context
    messages = [{"role": "system", "content": system_message}]
    
    if project_context:
        messages.append({
            "role": "system", 
            "content": f"Project Context: {project_context}"
        })
    
    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history[-6:]:  # Keep last 6 messages for context
            messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI chat error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def analyze_grant_requirements(organization_info: str, initiative_description: str) -> Dict:
    """Analyze organization and initiative to provide grant writing guidance.
    
    Args:
        organization_info: Description of the organization
        initiative_description: Description of the initiative/project
        
    Returns:
        Structured analysis with grant writing recommendations
    """
    system_message = """You are an expert grant consultant. Analyze the organization and initiative information 
    to provide specific grant writing recommendations. Focus on funding opportunities, key sections to emphasize, 
    and strategic advice."""
    
    prompt = f"""
    Organization Information: {organization_info}
    
    Initiative Description: {initiative_description}
    
    Please provide a comprehensive analysis including:
    1. Recommended grant types and funding sources
    2. Key strengths to emphasize in the proposal
    3. Potential challenges and how to address them
    4. Specific sections to focus on (mission, goals, methodology, etc.)
    5. Timeline and budget considerations
    6. Next steps and action items
    
    Be specific and actionable in your recommendations.
    """
    
    response = get_openai_response(prompt, system_message, max_tokens=2000)
    
    return {
        "analysis": response,
        "organization_info": organization_info,
        "initiative_description": initiative_description,
        "generated_at": datetime.now().isoformat()
    } 