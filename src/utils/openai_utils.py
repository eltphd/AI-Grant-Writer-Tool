"""OpenAI utilities for the AI Grant Writer tool with Cultural Competency.

This module provides functions for interacting with OpenAI's API to generate
grant writing assistance with cultural sensitivity and cognitive friendliness.
"""

import os
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime

# Configure OpenAI client (with fallback)
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        print(f"🔧 OpenAI API key status: configured ({len(api_key)} characters)")
    else:
        client = None
        print("⚠️ Warning: OPENAI_API_KEY not found in environment variables")
        print("⚠️ AI responses will be limited. Please set OPENAI_API_KEY for full functionality.")
except Exception as e:
    client = None
    print(f"⚠️ Error initializing OpenAI client: {e}")

def get_culturally_sensitive_response(prompt: str, community_context: str = "", max_tokens: int = 1000) -> str:
    """Get a culturally sensitive response from OpenAI's GPT model.
    
    Args:
        prompt: The user's question or prompt
        community_context: Optional community/cultural context
        max_tokens: Maximum tokens for the response
        
    Returns:
        The AI-generated response with cultural sensitivity
    """
    # Check if OpenAI client is available
    if client is None:
        return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
    
    # Check if OpenAI API key is configured (recheck at runtime)
    current_api_key = os.getenv("OPENAI_API_KEY")
    if not current_api_key:
        print("🔧 Runtime check: OPENAI_API_KEY not found in environment")
        return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
    
    try:
        # Specialized system message for cultural competency and cognitive friendliness
        system_message = """You are a culturally sensitive grant writing assistant with expertise in community-based organizations. 

CULTURAL COMPETENCY GUIDELINES:
- Use inclusive, respectful language that honors diverse communities
- Avoid jargon and technical terms that might exclude community members
- Provide clear, step-by-step guidance that's easy to understand
- Consider cultural context when giving advice
- Use encouraging, supportive tone that builds confidence
- Break down complex concepts into simple, actionable steps

COGNITIVE FRIENDLINESS:
- Use short, clear sentences
- Provide concrete examples and analogies
- Use bullet points and numbered lists for easy scanning
- Avoid overwhelming with too much information at once
- Use positive, encouraging language
- Provide specific, actionable next steps

RESPONSE FORMAT:
- Start with a brief, encouraging acknowledgment
- Use clear headings and bullet points
- Include specific examples when possible
- End with clear next steps or follow-up questions
- Keep language simple and accessible"""

        messages = []
        messages.append({"role": "system", "content": system_message})
        
        # Add community context if provided
        if community_context:
            messages.append({
                "role": "system", 
                "content": f"Community Context: {community_context}. Consider this cultural and community context in your response."
            })
            
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        if "authentication" in str(e).lower() or "api key" in str(e).lower():
            return "⚠️ OpenAI API key is invalid or not configured. Please check your OPENAI_API_KEY environment variable."
        elif "quota" in str(e).lower() or "billing" in str(e).lower():
            return "⚠️ OpenAI API quota exceeded or billing issue. Please check your OpenAI account."
        else:
            return f"⚠️ OpenAI API error: {str(e)}"

def get_openai_response(prompt: str, system_message: str = None, max_tokens: int = 1000) -> str:
    """Get a response from OpenAI's GPT model.
    
    Args:
        prompt: The user's question or prompt
        system_message: Optional system message to set context
        max_tokens: Maximum tokens for the response
        
    Returns:
        The AI-generated response
    """
    # Check if OpenAI client is available
    if client is None:
        return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
    
    # Check if OpenAI API key is configured (recheck at runtime)
    current_api_key = os.getenv("OPENAI_API_KEY")
    if not current_api_key:
        print("🔧 Runtime check: OPENAI_API_KEY not found in environment")
        return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
    
    try:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        if "authentication" in str(e).lower() or "api key" in str(e).lower():
            return "⚠️ OpenAI API key is invalid or not configured. Please check your OPENAI_API_KEY environment variable."
        elif "quota" in str(e).lower() or "billing" in str(e).lower():
            return "⚠️ OpenAI API quota exceeded or billing issue. Please check your OpenAI account."
        else:
            return f"⚠️ OpenAI API error: {str(e)}"

def generate_grant_response(question: str, project_context: str = "", community_context: str = "") -> str:
    """Generate a culturally sensitive grant writing response.
    
    Args:
        question: The user's question about grant writing
        project_context: Optional context about the project
        community_context: Optional community/cultural context
        
    Returns:
        AI-generated grant writing advice with cultural sensitivity
    """
    full_prompt = f"""
    Project Context: {project_context}
    
    Question: {question}
    
    Please provide helpful, culturally sensitive advice for this grant writing question. 
    Use simple, clear language and provide specific, actionable steps.
    Consider the community context and provide inclusive, supportive guidance.
    """
    
    return get_culturally_sensitive_response(full_prompt, community_context)

def brainstorm_grant_ideas(topic: str, project_context: str = "", community_context: str = "") -> Dict:
    """Generate culturally sensitive brainstorming ideas for grant writing.
    
    Args:
        topic: The topic to brainstorm about
        project_context: Optional context about the project
        community_context: Optional community/cultural context
        
    Returns:
        Dictionary with structured brainstorming ideas
    """
    prompt = f"""
    Project Context: {project_context}
    
    Topic for brainstorming: {topic}
    
    Please provide culturally sensitive brainstorming ideas organized into clear categories:
    
    💡 **Creative Ideas** - Fresh, innovative approaches
    📋 **Practical Steps** - Concrete actions you can take
    🤝 **Community Connections** - Ways to involve and support your community
    📊 **Success Stories** - Examples of similar successful projects
    ⚠️ **Important Considerations** - Things to keep in mind
    
    Make your suggestions specific, actionable, and culturally appropriate.
    Use simple language that's easy to understand.
    """
    
    response = get_culturally_sensitive_response(prompt, community_context, max_tokens=1500)
    
    # Parse the response into structured format
    ideas = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "suggestions": response,
        "categories": {
            "creative_ideas": [],
            "practical_steps": [],
            "community_connections": [],
            "success_stories": [],
            "considerations": []
        }
    }
    
    return ideas

def chat_grant_assistant(message: str, project_context: str = "", community_context: str = "", conversation_history: List = None) -> str:
    """Handle culturally sensitive chat-based grant writing assistance.
    
    Args:
        message: The user's message
        project_context: Optional context about the project
        community_context: Optional community/cultural context
        conversation_history: Previous conversation messages
        
    Returns:
        AI-generated response with cultural sensitivity
    """
    # Build conversation context
    messages = []
    
    # Add system message for cultural competency
    system_message = """You are a culturally sensitive grant writing assistant. You provide expert advice on grant writing 
    while being mindful of diverse communities and using accessible language. 
    
    GUIDELINES:
    - Use simple, clear language that's easy to understand
    - Provide specific, actionable advice
    - Be encouraging and supportive
    - Consider cultural context in your responses
    - Use bullet points and clear formatting
    - Avoid jargon and technical terms
    - Provide concrete examples when helpful"""
    
    messages.append({"role": "system", "content": system_message})
    
    if project_context:
        messages.append({
            "role": "system", 
            "content": f"Project Context: {project_context}"
        })
    
    if community_context:
        messages.append({
            "role": "system", 
            "content": f"Community Context: {community_context}. Consider this cultural context in your response."
        })
    
    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history[-6:]:  # Keep last 6 messages for context
            messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI chat error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def analyze_grant_requirements(organization_info: str, initiative_description: str, community_context: str = "") -> Dict:
    """Analyze organization and initiative with cultural sensitivity.
    
    Args:
        organization_info: Description of the organization
        initiative_description: Description of the initiative/project
        community_context: Optional community/cultural context
        
    Returns:
        Structured analysis with culturally sensitive grant writing recommendations
    """
    prompt = f"""
    Organization Information: {organization_info}
    
    Initiative Description: {initiative_description}
    
    Please provide a comprehensive, culturally sensitive analysis including:
    
    🎯 **Funding Opportunities** - Types of grants that might be a good fit
    💪 **Key Strengths** - What to emphasize in your proposal
    🤝 **Community Impact** - How this benefits your community
    📝 **Important Sections** - What to focus on in your grant
    ⏰ **Timeline Planning** - Realistic timeframes
    💰 **Budget Considerations** - Financial planning tips
    ✅ **Next Steps** - Specific actions to take
    
    Use simple, clear language and provide specific, actionable advice.
    Consider the community context in your recommendations.
    """
    
    response = get_culturally_sensitive_response(prompt, community_context, max_tokens=2000)
    
    return {
        "analysis": response,
        "organization_info": organization_info,
        "initiative_description": initiative_description,
        "community_context": community_context,
        "generated_at": datetime.now().isoformat()
    } 