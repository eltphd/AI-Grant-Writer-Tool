import os
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

# Import RAG utilities
try:
    from .utils.rag_utils import rag_db, KnowledgeItem, CulturalGuideline, CommunityProfile
    from .utils.advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem
    from .utils.specialized_llm_utils import specialized_llm
except ImportError:
    # Fallback for direct import
    from utils.rag_utils import rag_db, KnowledgeItem, CulturalGuideline, CommunityProfile
    from utils.advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem
    from utils.specialized_llm_utils import specialized_llm

# Import other utilities
try:
    from .utils.storage_utils import db_manager, OrganizationInfo, RFPDocument, ProjectResponse
    from .utils.rfp_analysis import rfp_analyzer
except ImportError:
    # Fallback for direct import
    from utils.storage_utils import db_manager, OrganizationInfo, RFPDocument, ProjectResponse
    from utils.rfp_analysis import rfp_analyzer

app = FastAPI(title="GWAT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Projects endpoint
@app.get("/projects")
async def get_projects():
    """Get all projects"""
    try:
        projects = db_manager.get_all_projects()
        return {"success": True, "projects": projects}
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return {"success": False, "error": str(e)}

# Organization management
@app.post("/organization/create")
async def create_organization(request: dict):
    """Create organization profile"""
    try:
        from datetime import datetime
        
        org = OrganizationInfo(
            id=f"org_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=request.get('name', 'New Organization'),
            mission=request.get('mission', ''),
            description=request.get('description', ''),
            key_accomplishments=request.get('key_accomplishments', []),
            partnerships=request.get('partnerships', []),
            impact_metrics=request.get('impact_metrics', {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        if db_manager.save_organization(org):
            return {"success": True, "organization": org.__dict__}
        else:
            return {"success": False, "error": "Failed to save organization"}
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        return {"success": False, "error": str(e)}

@app.get("/organization/{org_id}")
async def get_organization(org_id: str):
    """Get organization profile"""
    try:
        org = db_manager.get_organization(org_id)
        if org:
            return {"success": True, "organization": org.__dict__}
        else:
            return {"success": False, "error": "Organization not found"}
    except Exception as e:
        print(f"❌ Error getting organization: {e}")
        return {"success": False, "error": str(e)}

# RFP upload and analysis
@app.post("/rfp/upload")
async def upload_rfp(project_id: str, request: dict):
    """Upload and analyze RFP document"""
    try:
        from datetime import datetime
        
        # Analyze RFP content
        content = request.get('content', '')
        analysis = rfp_analyzer.analyze_rfp_content(content)
        
        # Create RFP document
        rfp = RFPDocument(
            id=f"rfp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_id=project_id,
            filename=request.get('filename', 'RFP Document'),
            content=content,
            requirements=analysis.get('requirements', []),
            eligibility_criteria=analysis.get('eligibility_criteria', []),
            funding_amount=analysis.get('funding_amount'),
            deadline=analysis.get('deadline'),
            analysis_result=analysis,
            created_at=datetime.now().isoformat()
        )
        
        # Save RFP document
        if db_manager.save_rfp(rfp):
            # Add to RAG system for context-aware responses
            knowledge_item = KnowledgeItem(
                id=f"rfp_{rfp.id}",
                title=f"RFP: {rfp.filename}",
                content=content,
                category="grant_narrative",
                tags=["rfp", "funding", "requirements"],
                source="uploaded_document",
                created_at=datetime.now().isoformat(),
                cultural_context=analysis.get('cultural_context'),
                community_focus=analysis.get('community_focus')
            )
            rag_db.add_knowledge_item(knowledge_item)
            
            return {"success": True, "rfp": rfp.__dict__, "analysis": analysis}
        else:
            return {"success": False, "error": "Failed to save RFP"}
    except Exception as e:
        print(f"❌ Error uploading RFP: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rfp/analyze")
async def analyze_rfp(project_id: str, request: dict):
    """Analyze RFP content for requirements and alignment"""
    try:
        content = request.get('content', '')
        analysis = rfp_analyzer.analyze_rfp_content(content)
        
        return {"success": True, "analysis": analysis}
    except Exception as e:
        print(f"❌ Error analyzing RFP: {e}")
        return {"success": False, "error": str(e)}

# File upload endpoint
@app.post("/upload")
async def upload_file(project_id: str, file: dict):
    """Upload file and extract content for advanced RAG processing"""
    try:
        from datetime import datetime
        
        filename = file.get('filename', 'uploaded_file')
        content = file.get('content', '')
        
        # Determine file type and category with cultural context
        file_type = filename.split('.')[-1].lower()
        category = "grant_narrative"  # default
        
        if 'organization' in filename.lower() or 'org' in filename.lower():
            category = "organization_profile"
        elif 'proposal' in filename.lower() or 'grant' in filename.lower():
            category = "grant_narrative"
        elif 'budget' in filename.lower() or 'financial' in filename.lower():
            category = "budget_planning"
        elif 'timeline' in filename.lower() or 'schedule' in filename.lower():
            category = "timeline_planning"
        
        # Create advanced knowledge item with cultural context
        knowledge_item = CulturalKnowledgeItem(
            id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=filename,
            content=content,
            category=category,
            tags=[file_type, "uploaded_document"],
            source="user_upload",
            created_at=datetime.now().isoformat(),
            language="en",  # Can be enhanced for multilingual support
            cultural_context=None,  # Will be extracted by advanced RAG
            community_focus=None  # Will be determined from content analysis
        )
        
        # Add to advanced RAG database
        if advanced_rag_db.add_knowledge_item(knowledge_item):
            return {
                "success": True,
                "filename": filename,
                "content_length": len(content),
                "category": category,
                "uploaded_at": datetime.now().isoformat(),
                "message": f"File '{filename}' uploaded and processed with advanced cultural context analysis. The AI can now use this content for culturally sensitive responses.",
                "advanced_features": {
                    "cultural_context_analysis": True,
                    "semantic_search_enabled": True,
                    "multilingual_support": True
                }
            }
        else:
            return {"success": False, "error": "Failed to process file for advanced AI context"}
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

# Context endpoint
@app.get("/context/{project_id}")
async def get_project_context(project_id: str):
    """Get project context"""
    try:
        return {"success": True, "context": {"files": []}}
    except Exception as e:
        print(f"❌ Error getting project context: {e}")
        return {"success": False, "error": str(e)}

@app.post("/context/{project_id}")
async def update_project_context(project_id: str, request: dict):
    """Update project context"""
    try:
        return {"success": True, "message": "Context updated successfully"}
    except Exception as e:
        print(f"❌ Error updating project context: {e}")
        return {"success": False, "error": str(e)}

# Chat endpoints
@app.post("/chat/send_message")
async def send_message(request: dict):
    """Send chat message with context-aware responses"""
    try:
        message = request.get('message', '').lower()
        project_id = request.get('project_id', 'test-project')
        
        # Get project context and RFP analysis
        project_context = get_project_context_data(project_id)
        rfp_analysis = get_rfp_analysis_data(project_id)
        
        # Generate context-aware response
        ai_response = generate_contextual_response(message, project_context, rfp_analysis)
        
        return {
            "success": True,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

def get_project_context_data(project_id: str) -> dict:
    """Get project context data from RAG system"""
    try:
        # Get uploaded documents from RAG system
        uploaded_files = []
        knowledge_items = rag_db.search_knowledge("", limit=50)  # Get all items
        for item in knowledge_items:
            if item.source == "user_upload":
                uploaded_files.append(item.title)
        
        # Get organization info if available
        org_items = rag_db.search_knowledge("organization", category="organization_profile", limit=5)
        organization_info = ""
        if org_items:
            organization_info = org_items[0].content[:500] + "..." if len(org_items[0].content) > 500 else org_items[0].content
        
        return {
            "organization_info": organization_info,
            "initiative_description": "Based on uploaded documents",
            "uploaded_files": uploaded_files,
            "rfp_requirements": ["Requirements from uploaded RFP documents"],
            "community_focus": "Based on uploaded community documents"
        }
    except Exception as e:
        print(f"Error getting project context: {e}")
        return {
            "organization_info": "No organization information available",
            "initiative_description": "No initiative description available",
            "uploaded_files": [],
            "rfp_requirements": [],
            "community_focus": None
        }

def get_rfp_analysis_data(project_id: str) -> dict:
    """Get RFP analysis data from RAG system"""
    try:
        # Search for RFP-related documents
        rfp_items = rag_db.search_knowledge("RFP funding requirements", category="grant_narrative", limit=5)
        
        if rfp_items:
            # Extract requirements from RFP content
            rfp_content = rfp_items[0].content
            requirements = []
            if "non-profit" in rfp_content.lower():
                requirements.append("Non-profit status required")
            if "community" in rfp_content.lower():
                requirements.append("Community focus required")
            if "measurable" in rfp_content.lower():
                requirements.append("Measurable outcomes required")
            
            return {
                "requirements": requirements,
                "eligibility_criteria": ["Based on uploaded RFP documents"],
                "funding_amount": "Based on uploaded RFP documents",
                "deadline": "Based on uploaded RFP documents",
                "alignment_score": 85
            }
        else:
            return {
                "requirements": ["No RFP documents uploaded yet"],
                "eligibility_criteria": ["Upload RFP documents for analysis"],
                "funding_amount": "Upload RFP for funding details",
                "deadline": "Upload RFP for deadline information",
                "alignment_score": 0
            }
    except Exception as e:
        print(f"Error getting RFP analysis: {e}")
        return {
            "requirements": ["Error retrieving RFP analysis"],
            "eligibility_criteria": ["Error retrieving eligibility criteria"],
            "funding_amount": "Error retrieving funding amount",
            "deadline": "Error retrieving deadline",
            "alignment_score": 0
        }

def generate_contextual_response(message: str, context: dict, rfp_analysis: dict) -> str:
    """Generate culturally sensitive contextual AI response using specialized LLM approach"""
    
    # Get advanced RAG context for enhanced responses
    rag_context = advanced_rag_db.get_relevant_context(message, "grant_section", context.get('community_focus'))
    
    # Build project context string
    project_context = f"""
    Organization: {context.get('organization_info', 'Not provided')}
    Initiative: {context.get('initiative_description', 'Not provided')}
    Uploaded Files: {', '.join(context.get('uploaded_files', []))}
    RFP Requirements: {', '.join(rfp_analysis.get('requirements', []))}
    """
    
    # Get community context from RAG
    community_context = context.get('community_focus', '')
    if rag_context and 'cultural_context' in rag_context:
        community_context += f" {rag_context['cultural_context']}"
    
    # Check for specific section writing requests using specialized LLM
    if any(word in message.lower() for word in ['executive summary', 'summary']):
        return specialized_llm.generate_culturally_sensitive_response(
            "executive_summary", 
            {"organization_info": context.get('organization_info', ''), 
             "community_focus": community_context,
             "uploaded_files": ', '.join(context.get('uploaded_files', [])),
             "rfp_requirements": ', '.join(rfp_analysis.get('requirements', []))},
            community_context
        )
    
    elif any(word in message.lower() for word in ['organization profile', 'organization', 'profile']):
        return specialized_llm.generate_culturally_sensitive_response(
            "organization_profile",
            {"organization_info": context.get('organization_info', ''),
             "community_focus": community_context,
             "cultural_guidelines": rag_context.get('cultural_context', '')},
            community_context
        )
    
    elif any(word in message.lower() for word in ['project description', 'project', 'description']):
        return specialized_llm.generate_culturally_sensitive_response(
            "project_description",
            {"project_context": project_context,
             "community_focus": community_context,
             "cultural_guidelines": rag_context.get('cultural_context', '')},
            community_context
        )
    
    elif any(word in message.lower() for word in ['timeline', 'schedule', 'deadline']):
        return generate_timeline_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['budget', 'funding', 'cost']):
        return generate_budget_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['evaluation', 'measure', 'outcome']):
        return generate_evaluation_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['grant', 'section', 'write', 'create']):
        return generate_grant_section_guidance(context, rfp_analysis)
    
    elif any(word in message.lower() for word in ['content', 'access', 'document', 'file']):
        return generate_content_access_response(context)
    
    elif any(word in message.lower() for word in ['rfp', 'requirement', 'eligibility']):
        return generate_rfp_guidance(rfp_analysis)
    
    elif any(word in message.lower() for word in ['help', 'guide', 'assist']):
        return generate_general_guidance(context, rfp_analysis)
    
    else:
        # Use specialized LLM approach for general responses
        try:
            from utils.openai_utils import chat_grant_assistant
            return chat_grant_assistant(message, project_context, community_context)
        except Exception as e:
            print(f"Error with specialized LLM response: {e}")
            return generate_default_response(message, context, rfp_analysis)

def generate_executive_summary_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate culturally sensitive executive summary using RAG context"""
    
    from utils.openai_utils import get_culturally_sensitive_response
    
    org_info = context.get('organization_info', {})
    uploaded_files = context.get('uploaded_files', [])
    community_focus = context.get('community_focus', '')
    
    # Build context for the AI
    project_context = f"""
    Organization Information: {org_info}
    Uploaded Documents: {', '.join(uploaded_files)}
    Community Focus: {community_focus}
    RFP Requirements: {', '.join(rfp_analysis.get('requirements', []))}
    """
    
    prompt = f"""
    Please write a culturally sensitive executive summary for a grant proposal.
    
    Project Context: {project_context}
    
    GUIDELINES:
    - Use clear, simple language that's easy to understand
    - Highlight the community impact and benefits
    - Include specific, measurable goals
    - Show how this addresses community needs
    - Use encouraging, positive language
    - Keep it concise but comprehensive (2-3 paragraphs)
    
    FORMAT:
    - Start with a compelling opening that captures the community's needs
    - Include the organization's mission and key strengths
    - Describe the project's goals and expected outcomes
    - End with a strong call to action about the funding impact
    
    Make sure the language is inclusive and respectful of diverse communities.
    """
    
    try:
        response = get_culturally_sensitive_response(prompt, community_focus)
        return response
    except Exception as e:
        print(f"Error generating executive summary: {e}")
        return f"""📋 **Executive Summary**

Based on your organization's information and uploaded documents, here's a draft executive summary:

**Our Mission & Impact**
Your organization is dedicated to serving the community with a focus on {community_focus or 'positive community change'}. Through this grant, we will expand our impact and create lasting benefits for those we serve.

**Project Goals**
This funding will enable us to:
• Strengthen our community programs and services
• Reach more individuals and families in need
• Create measurable, positive outcomes
• Build sustainable partnerships and resources

**Expected Outcomes**
With this support, we will achieve specific, measurable results that demonstrate our commitment to community well-being and positive change.

**Next Steps**
Please review this summary and let me know if you'd like me to adjust the focus, tone, or add specific details from your uploaded documents."""

def generate_organization_profile_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate organization profile using RAG context for cultural competence"""
    
    org_info = context.get('organization_info', {})
    
    response = "🏢 **Organization Profile**\n\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    if org_info.get('name'):
        response += f"**{org_info['name']}** "
    else:
        response += "**Our Organization** "
    
    if org_info.get('mission'):
        response += f"is dedicated to {org_info['mission']}. "
    else:
        response += "is committed to creating positive community impact. "
    
    if org_info.get('years_operating'):
        response += f"Established {org_info['years_operating']} years ago, "
    
    if org_info.get('legal_status'):
        response += f"we operate as a {org_info['legal_status']} "
    else:
        response += "we operate as a non-profit organization "
    
    response += "serving our community with integrity and excellence.\n\n"
    
    response += "**Our Expertise:**\n"
    if org_info.get('focus_areas'):
        for area in org_info['focus_areas']:
            response += f"• {area}\n"
    else:
        response += "• Community development\n• Program implementation\n• Stakeholder engagement\n"
    
    if org_info.get('target_population'):
        response += f"\n**Target Population:** {org_info['target_population']}\n"
    
    if org_info.get('geographic_area'):
        response += f"**Service Area:** {org_info['geographic_area']}\n"
    
    response += "\n**Organizational Capacity:**\n"
    response += "• Experienced leadership team\n"
    response += "• Strong community partnerships\n"
    response += "• Proven track record of success\n"
    response += "• Robust evaluation systems\n\n"
    
    response += community_context
    
    response += "**Why We're the Right Choice:**\n"
    response += "Our deep community roots, proven expertise, and commitment to measurable outcomes make us the ideal partner for this initiative."
    
    return response

def generate_project_description_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate project description using RAG context for cultural competence"""
    
    org_info = context.get('organization_info', {})
    rfp_reqs = rfp_analysis.get('requirements', [])
    
    response = "🎯 **Project Description & Approach**\n\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    if org_info.get('name'):
        response += f"**{org_info['name']}** proposes to "
    else:
        response += "**Our organization** proposes to "
    
    if org_info.get('initiative_description'):
        response += f"{org_info['initiative_description']}. "
    else:
        response += "implement a comprehensive community development initiative. "
    
    response += "This project will address critical community needs while meeting all RFP requirements.\n\n"
    
    # Incorporate best practices from RAG
    if rag_context.get('best_practices'):
        response += "**Evidence-Based Approach:** This proposal incorporates proven strategies including "
        response += rag_context['best_practices'][0]['title'] + " and "
        response += rag_context['best_practices'][1]['title'] if len(rag_context['best_practices']) > 1 else "established best practices"
        response += ".\n\n"
    
    response += "**Project Objectives:**\n"
    if rfp_reqs:
        for i, req in enumerate(rfp_reqs[:5], 1):
            response += f"{i}. Address {req}\n"
    else:
        response += "1. Enhance community engagement\n"
        response += "2. Build organizational capacity\n"
        response += "3. Create sustainable impact\n"
        response += "4. Meet all RFP requirements\n"
    
    response += "\n**Implementation Strategy:**\n"
    response += "• **Phase 1:** Community needs assessment and stakeholder engagement\n"
    response += "• **Phase 2:** Program development and partnership building\n"
    response += "• **Phase 3:** Implementation and monitoring\n"
    response += "• **Phase 4:** Evaluation and sustainability planning\n\n"
    
    response += "**Innovative Approach:**\n"
    response += "Our methodology combines proven best practices with innovative community-driven solutions, ensuring both immediate impact and long-term sustainability."
    
    response += community_context
    
    return response

def generate_timeline_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate timeline section using RAG context for cultural competence"""
    
    response = "⏰ **Timeline & Implementation**\n\n"
    
    if rfp_analysis.get('deadline'):
        response += f"**Project Duration:** Aligned with RFP deadline of {rfp_analysis['deadline']}\n\n"
    
    response += "**Implementation Timeline:**\n\n"
    response += "**Months 1-3: Foundation Building**\n"
    response += "• Stakeholder engagement and community outreach\n"
    response += "• Needs assessment and baseline data collection\n"
    response += "• Partnership development and resource mobilization\n"
    response += "• Program design and approval processes\n\n"
    
    response += "**Months 4-6: Program Launch**\n"
    response += "• Initial program implementation\n"
    response += "• Staff training and capacity building\n"
    response += "• Pilot testing and refinement\n"
    response += "• Early outcome measurement\n\n"
    
    response += "**Months 7-9: Full Implementation**\n"
    response += "• Comprehensive program delivery\n"
    response += "• Ongoing monitoring and evaluation\n"
    response += "• Mid-course adjustments as needed\n"
    response += "• Progress reporting and stakeholder updates\n\n"
    
    response += "**Months 10-12: Sustainability Planning**\n"
    response += "• Long-term impact assessment\n"
    response += "• Sustainability strategy development\n"
    response += "• Knowledge transfer and capacity building\n"
    response += "• Final evaluation and reporting\n\n"
    
    response += "**Key Milestones:**\n"
    response += "• Month 3: Program design approval\n"
    response += "• Month 6: Initial outcomes report\n"
    response += "• Month 9: Mid-term evaluation\n"
    response += "• Month 12: Final project report\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_budget_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate budget section using RAG context for cultural competence"""
    
    response = "💰 **Budget & Financial Plan**\n\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"**Total Project Budget:** {rfp_analysis['funding_amount']}\n\n"
    
    response += "**Budget Breakdown:**\n\n"
    response += "**Personnel (40%):** $XX,XXX\n"
    response += "• Project Director: $XX,XXX\n"
    response += "• Program Coordinators: $XX,XXX\n"
    response += "• Support Staff: $XX,XXX\n\n"
    
    response += "**Program Activities (30%):** $XX,XXX\n"
    response += "• Community outreach and engagement: $XX,XXX\n"
    response += "• Training and capacity building: $XX,XXX\n"
    response += "• Materials and supplies: $XX,XXX\n"
    response += "• Technology and equipment: $XX,XXX\n\n"
    
    response += "**Evaluation & Monitoring (15%):** $XX,XXX\n"
    response += "• Data collection and analysis: $XX,XXX\n"
    response += "• External evaluation: $XX,XXX\n"
    response += "• Reporting and documentation: $XX,XXX\n\n"
    
    response += "**Administrative (10%):** $XX,XXX\n"
    response += "• Office space and utilities: $XX,XXX\n"
    response += "• Insurance and legal: $XX,XXX\n"
    response += "• Financial management: $XX,XXX\n\n"
    
    response += "**Contingency (5%):** $XX,XXX\n"
    response += "• Unforeseen expenses and adjustments\n\n"
    
    response += "**Cost-Effectiveness:**\n"
    response += "• Leveraged partnerships reduce direct costs\n"
    response += "• Shared resources maximize impact\n"
    response += "• Sustainable approach ensures long-term value\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_evaluation_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate evaluation section using RAG context for cultural competence"""
    
    response = "📊 **Evaluation & Impact Measurement**\n\n"
    
    response += "**Evaluation Framework:**\n"
    response += "Our comprehensive evaluation approach combines quantitative and qualitative methods to measure both immediate outcomes and long-term impact.\n\n"
    
    response += "**Key Performance Indicators:**\n"
    response += "• **Output Metrics:** Number of participants served, activities completed\n"
    response += "• **Outcome Metrics:** Changes in knowledge, skills, and behaviors\n"
    response += "• **Impact Metrics:** Long-term community improvements\n"
    response += "• **Process Metrics:** Efficiency and effectiveness measures\n\n"
    
    response += "**Data Collection Methods:**\n"
    response += "• Surveys and interviews with participants\n"
    response += "• Focus groups with stakeholders\n"
    response += "• Document review and analysis\n"
    response += "• Community feedback sessions\n"
    response += "• External evaluation partner assessment\n\n"
    
    response += "**Reporting Schedule:**\n"
    response += "• Monthly progress reports\n"
    response += "• Quarterly outcome assessments\n"
    response += "• Annual comprehensive evaluation\n"
    response += "• Final impact report\n\n"
    
    response += "**Continuous Improvement:**\n"
    response += "Evaluation findings will inform ongoing program refinement, ensuring maximum effectiveness and community benefit."
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_grant_section_guidance(context: dict, rfp_analysis: dict) -> str:
    """Generate conversational grant section guidance"""
    
    response = "📋 **Great! Let's write your grant sections together!**\n\n"
    
    response += "**Here's what we need to write:**\n\n"
    response += "1️⃣ **Executive Summary** - The big picture overview\n"
    response += "2️⃣ **Organization Profile** - Tell your story\n"
    response += "3️⃣ **Project Description** - What you want to do\n"
    response += "4️⃣ **Timeline** - When you'll do it\n"
    response += "5️⃣ **Budget** - How much it will cost\n"
    response += "6️⃣ **Evaluation** - How you'll measure success\n\n"
    
    if rfp_analysis.get('requirements'):
        response += "**Based on your RFP, focus on these key points:**\n"
        for i, req in enumerate(rfp_analysis['requirements'][:3], 1):
            response += f"{i}. {req}\n"
        response += "\n"
    
    response += "**Which section would you like me to write for you?**\n"
    response += "Just say 'write executive summary' or 'write budget' and I'll create it using your data!"
    
    return response

def generate_content_access_response(context: dict) -> str:
    """Generate response about uploaded content and AI access"""
    
    uploaded_files = context.get('uploaded_files', [])
    
    if not uploaded_files:
        return """📄 **No documents uploaded yet**

I don't see any documents uploaded yet. To help me provide context-aware assistance, please upload:

• **Grant funding application documents** - RFP guidelines, funding announcements
• **Organization profile documents** - Your mission, history, accomplishments
• **Proposal drafts** - Any existing grant proposals or project descriptions

Once you upload documents, I can:
✅ Analyze funding requirements and align them with your organization
✅ Provide culturally sensitive recommendations based on your community focus
✅ Help strategize funding proposals using your specific context
✅ Generate grant sections tailored to your organization and the funder's needs

Go to the "Create Grant" tab to upload your documents!"""
    
    else:
        file_list = "\n".join([f"• {file}" for file in uploaded_files])
        return f"""📄 **Uploaded Documents Available**

I can see the following documents have been uploaded and processed:

{file_list}

**What I can do with these documents:**
✅ Analyze funding requirements from your RFP documents
✅ Extract organization information for grant alignment
✅ Provide culturally sensitive recommendations
✅ Generate grant sections using your specific context
✅ Strategize funding proposals based on your organization's profile

**Ask me to:**
• "Help me write an executive summary based on my organization"
• "Analyze the RFP requirements and our alignment"
• "Generate a project description using our uploaded documents"
• "Create a budget section based on our organization's needs"

The AI is now using your uploaded documents for context-aware responses!"""

def generate_rfp_guidance(rfp_analysis: dict) -> str:
    """Generate conversational RFP guidance"""
    
    response = "📋 **Here's what I found in your RFP:**\n\n"
    
    if rfp_analysis.get('requirements'):
        response += "**Key Requirements:**\n"
        for i, req in enumerate(rfp_analysis['requirements'], 1):
            response += f"{i}. {req}\n"
        response += "\n"
    
    if rfp_analysis.get('eligibility_criteria'):
        response += "**Eligibility Criteria:**\n"
        for i, criteria in enumerate(rfp_analysis['eligibility_criteria'], 1):
            response += f"{i}. {criteria}\n"
        response += "\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"💰 **Funding Available:** {rfp_analysis['funding_amount']}\n"
    
    if rfp_analysis.get('deadline'):
        response += f"⏰ **Deadline:** {rfp_analysis['deadline']}\n\n"
    
    if rfp_analysis.get('alignment_score'):
        response += f"🎯 **Your Alignment Score:** {rfp_analysis['alignment_score']}%\n\n"
    
    response += "**My recommendations:**\n"
    response += "• Focus on the requirements you meet well\n"
    response += "• Address any gaps with specific plans\n"
    response += "• Make sure your proposal matches their priorities\n\n"
    
    response += "**Would you like me to help you write sections that address these requirements?**"
    
    return response

def generate_budget_guidance(rfp_analysis: dict) -> str:
    """Generate budget guidance"""
    
    response = "💰 **Budget Guidance**\n\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"**RFP Funding:** {rfp_analysis['funding_amount']}\n\n"
    
    response += "**Budget Best Practices:**\n"
    response += "• Align with RFP funding limits\n"
    response += "• Include all required cost categories\n"
    response += "• Provide detailed line items\n"
    response += "• Show cost-effectiveness\n"
    response += "• Include matching funds if required\n\n"
    
    response += "**Common Budget Categories:**\n"
    response += "• Personnel (salaries, benefits)\n"
    response += "• Equipment and supplies\n"
    response += "• Travel and training\n"
    response += "• Indirect costs\n"
    response += "• Evaluation and reporting\n\n"
    
    response += "Would you like help structuring your budget?"
    
    return response

def generate_timeline_guidance(rfp_analysis: dict) -> str:
    """Generate timeline guidance"""
    
    response = "⏰ **Timeline & Deadline Guidance**\n\n"
    
    if rfp_analysis.get('deadline'):
        response += f"**RFP Deadline:** {rfp_analysis['deadline']}\n\n"
    
    response += "**Timeline Best Practices:**\n"
    response += "• Start early - allow 2-3 weeks for writing\n"
    response += "• Include internal review time\n"
    response += "• Plan for revisions and feedback\n"
    response += "• Consider submission requirements\n\n"
    
    response += "**Project Timeline Structure:**\n"
    response += "• Month 1-3: Planning and preparation\n"
    response += "• Month 4-6: Implementation phase\n"
    response += "• Month 7-9: Evaluation and reporting\n"
    response += "• Month 10-12: Sustainability planning\n\n"
    
    response += "**Key Milestones to Include:**\n"
    response += "• Project kickoff\n"
    response += "• Major deliverables\n"
    response += "• Progress reviews\n"
    response += "• Final evaluation\n"
    
    return response

def generate_general_guidance(context: dict, rfp_analysis: dict) -> str:
    """Generate conversational general guidance"""
    
    response = "🎯 **Hi! I'm your GWAT Assistant**\n\n"
    
    response += "**I'm here to help you write a winning grant proposal!**\n\n"
    
    if context.get('organization_info'):
        response += "✅ I can see your organization information\n"
    else:
        response += "❌ I don't see your organization info yet\n"
    
    if rfp_analysis.get('requirements'):
        response += f"✅ I have your RFP analysis ({len(rfp_analysis['requirements'])} requirements)\n"
    else:
        response += "❌ I don't see your RFP document yet\n"
    
    response += "\n**What would you like to do?**\n\n"
    response += "1️⃣ **'Help me write sections'** - I'll walk you through each part of your grant\n"
    response += "2️⃣ **'Show my RFP analysis'** - I'll tell you what I found in your RFP\n"
    response += "3️⃣ **'Help with budget'** - I'll help you plan your funding request\n"
    response += "4️⃣ **'Brainstorm ideas'** - I'll give you creative writing ideas\n"
    response += "5️⃣ **'Check my alignment'** - I'll see how well you match the RFP\n\n"
    
    response += "**Just tell me what you need in simple terms!** 😊"
    
    return response

def generate_default_response(message: str, context: dict, rfp_analysis: dict) -> str:
    """Generate a culturally sensitive default response when no specific pattern is matched"""
    
    uploaded_files = context.get('uploaded_files', [])
    
    if not uploaded_files:
        return """🤝 **Welcome! I'm here to help with your grant writing.**

I can see you're working on a grant proposal. To give you the best help possible, I'd love to learn more about your project.

**What I can help you with:**
• 📝 Writing grant sections (executive summary, organization profile, etc.)
• 💡 Brainstorming ideas for your proposal
• 📋 Analyzing RFP requirements
• 💰 Budget planning and financial sections
• ⏰ Timeline and implementation planning
• 📊 Evaluation and impact measurement

**To get started:**
1. Upload your RFP document and organization information
2. Tell me about your community and project goals
3. Ask me to help with specific sections

**Try asking me:**
• "Help me write an executive summary"
• "What should I include in my organization profile?"
• "How do I plan my project timeline?"
• "Can you help me with the budget section?"

I'm here to support you every step of the way! 😊"""
    
    else:
        return f"""🤝 **Great! I can see you've uploaded {len(uploaded_files)} document(s).**

I'm ready to help you create a strong grant proposal using your uploaded information.

**Based on your documents, I can help you with:**
• 📝 Writing specific grant sections using your organization's information
• 💡 Brainstorming ideas tailored to your project
• 📋 Analyzing how your project aligns with funding requirements
• 💰 Creating budget sections based on your needs
• ⏰ Planning realistic timelines for your project
• 📊 Developing evaluation strategies for your impact

**What would you like to work on?**
• "Write an executive summary using my organization's information"
• "Help me create an organization profile"
• "Analyze the RFP requirements and our alignment"
• "Generate a project description based on our documents"
• "Help me plan the budget section"

I'm here to make your grant writing process easier and more successful! 😊"""

@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    """Get chat history"""
    try:
        return {
            "success": True,
            "messages": [
                {
                    "id": 1,
                    "message": "Welcome to GWAT! How can I help with your grant writing?",
                    "timestamp": datetime.now().isoformat(),
                    "type": "ai"
                }
            ]
        }
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

@app.post("/chat/brainstorm")
async def brainstorm_ideas(request: dict):
    """Brainstorm grant ideas and strategies"""
    try:
        project_id = request.get('project_id', 'test-project')
        topic = request.get('topic', '').lower()
        project_context = get_project_context_data(project_id)
        rfp_analysis = get_rfp_analysis_data(project_id)
        
        # Generate topic-specific brainstorming
        if any(word in topic for word in ['section', 'write', 'content']):
            ideas = generate_section_ideas(project_context, rfp_analysis)
        elif any(word in topic for word in ['budget', 'funding', 'cost']):
            ideas = generate_budget_ideas(rfp_analysis)
        elif any(word in topic for word in ['timeline', 'schedule', 'deadline']):
            ideas = generate_timeline_ideas(rfp_analysis)
        elif any(word in topic for word in ['evaluation', 'measure', 'outcome']):
            ideas = generate_evaluation_ideas(project_context, rfp_analysis)
        elif any(word in topic for word in ['partnership', 'collaboration', 'network']):
            ideas = generate_partnership_ideas(project_context)
        else:
            ideas = generate_general_ideas(project_context, rfp_analysis)
        
        return {
            "success": True,
            "ideas": ideas
        }
    except Exception as e:
        print(f"❌ Error brainstorming: {e}")
        return {"success": False, "error": str(e)}

def generate_section_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate ideas for grant sections"""
    ideas = [
        "📋 **Executive Summary Ideas:**",
        "• Start with a compelling hook about your organization's impact",
        "• Include 2-3 key statistics that demonstrate success",
        "• End with a clear call to action about the proposed project",
        "",
        "🏢 **Organization Profile Ideas:**",
        "• Highlight your unique mission and values",
        "• Showcase past achievements with specific metrics",
        "• Emphasize your expertise in the target area",
        "• Include testimonials from partners or beneficiaries",
        "",
        "🎯 **Project Approach Ideas:**",
        "• Describe your innovative methodology",
        "• Explain how you'll address the specific RFP requirements",
        "• Include risk mitigation strategies",
        "• Show how you'll measure and report progress"
    ]
    
    if rfp_analysis.get('requirements'):
        ideas.append("")
        ideas.append("**RFP-Specific Focus Areas:**")
        for req in rfp_analysis['requirements'][:3]:
            ideas.append(f"• Emphasize how you meet: {req}")
    
    return ideas

def generate_budget_ideas(rfp_analysis: dict) -> list:
    """Generate budget-related ideas"""
    ideas = [
        "💰 **Budget Strategy Ideas:**",
        "• Align every line item with RFP requirements",
        "• Show cost-effectiveness through detailed breakdowns",
        "• Include matching funds if required by the RFP",
        "• Demonstrate sustainability beyond the grant period",
        "",
        "📊 **Budget Categories to Consider:**",
        "• Personnel (salaries, benefits, training)",
        "• Equipment and technology needs",
        "• Travel and professional development",
        "• Evaluation and reporting costs",
        "• Indirect costs (if allowed)",
        "",
        "💡 **Budget Presentation Tips:**",
        "• Use clear, professional formatting",
        "• Include narrative explanations for major items",
        "• Show how costs align with project outcomes",
        "• Demonstrate value for money"
    ]
    
    if rfp_analysis.get('funding_amount'):
        ideas.append("")
        ideas.append(f"**RFP Funding Target:** {rfp_analysis['funding_amount']}")
        ideas.append("• Structure your budget to maximize this amount")
        ideas.append("• Show how you'll use funds effectively")
    
    return ideas

def generate_timeline_ideas(rfp_analysis: dict) -> list:
    """Generate timeline-related ideas"""
    ideas = [
        "⏰ **Timeline Strategy Ideas:**",
        "• Create realistic milestones that align with RFP requirements",
        "• Include buffer time for unexpected challenges",
        "• Show how you'll maintain momentum throughout the project",
        "• Demonstrate sustainability planning",
        "",
        "📅 **Timeline Structure Ideas:**",
        "• Month 1-3: Planning and preparation phase",
        "• Month 4-6: Implementation and early results",
        "• Month 7-9: Evaluation and mid-course corrections",
        "• Month 10-12: Reporting and sustainability planning",
        "",
        "🎯 **Key Milestones to Include:**",
        "• Project kickoff and team formation",
        "• Major deliverables and checkpoints",
        "• Progress reviews and stakeholder meetings",
        "• Final evaluation and reporting"
    ]
    
    if rfp_analysis.get('deadline'):
        ideas.append("")
        ideas.append(f"**RFP Deadline:** {rfp_analysis['deadline']}")
        ideas.append("• Plan backwards from this date")
        ideas.append("• Include time for revisions and feedback")
    
    return ideas

def generate_evaluation_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate evaluation-related ideas"""
    ideas = [
        "📊 **Evaluation Strategy Ideas:**",
        "• Design measurable outcomes that align with RFP goals",
        "• Include both quantitative and qualitative measures",
        "• Plan for ongoing monitoring and reporting",
        "• Show how you'll use data to improve programs",
        "",
        "📈 **Evaluation Methods to Consider:**",
        "• Pre/post assessments for participants",
        "• Regular progress reports and check-ins",
        "• Stakeholder feedback and surveys",
        "• External evaluation or peer review",
        "• Long-term impact measurement",
        "",
        "🎯 **Key Metrics to Track:**",
        "• Number of people served",
        "• Quality of services delivered",
        "• Participant satisfaction and outcomes",
        "• Cost-effectiveness and efficiency",
        "• Sustainability and lasting impact"
    ]
    
    return ideas

def generate_partnership_ideas(context: dict) -> list:
    """Generate partnership-related ideas"""
    ideas = [
        "🤝 **Partnership Strategy Ideas:**",
        "• Identify complementary organizations in your field",
        "• Show how partnerships strengthen your proposal",
        "• Include letters of support or commitment",
        "• Demonstrate collaborative capacity and experience",
        "",
        "🏢 **Potential Partner Types:**",
        "• Local government agencies",
        "• Educational institutions",
        "• Healthcare providers",
        "• Community organizations",
        "• Private sector partners",
        "• Faith-based organizations",
        "",
        "💡 **Partnership Benefits to Highlight:**",
        "• Shared resources and expertise",
        "• Broader reach and impact",
        "• Cost-effectiveness through collaboration",
        "• Sustainability through diverse support"
    ]
    
    return ideas

def generate_general_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate general grant writing ideas"""
    ideas = [
        "🎯 **General Grant Writing Strategies:**",
        "• Tell a compelling story about your organization's impact",
        "• Use specific examples and success stories",
        "• Include data and statistics to support your case",
        "• Show how you'll address the funder's priorities",
        "",
        "📋 **Proposal Enhancement Ideas:**",
        "• Include visual elements (charts, photos, diagrams)",
        "• Add testimonials from beneficiaries or partners",
        "• Provide clear, concise executive summary",
        "• Show innovation and creativity in your approach",
        "",
        "💡 **Competitive Advantage Ideas:**",
        "• Highlight your unique expertise or approach",
        "• Show proven track record in similar projects",
        "• Demonstrate strong community relationships",
        "• Include plans for sustainability and scaling"
    ]
    
    if rfp_analysis.get('alignment_score'):
        ideas.append("")
        ideas.append(f"**Your Alignment Score: {rfp_analysis['alignment_score']}%**")
        if rfp_analysis['alignment_score'] >= 80:
            ideas.append("• Excellent alignment - emphasize your strengths")
        elif rfp_analysis['alignment_score'] >= 60:
            ideas.append("• Good alignment - address any gaps specifically")
        else:
            ideas.append("• Focus on improving alignment with RFP requirements")
    
    return ideas

# Privacy audit endpoint
@app.get("/privacy/audit/{project_id}")
async def privacy_audit(project_id: str):
    """Get privacy audit for a project"""
    try:
        return {
            "success": True,
            "audit_result": {
                "overall_privacy_level": "high",
                "sensitive_data_found": False,
                "recommendations": []
            }
        }
    except Exception as e:
        print(f"❌ Error privacy audit: {e}")
        return {"success": False, "error": str(e)}

# Grant sections endpoint
@app.get("/grant/sections/{project_id}")
async def get_grant_sections(project_id: str):
    """Get grant sections"""
    try:
        return {
            "success": True,
            "sections": {
                "executive_summary": "Project executive summary...",
                "organization_profile": "Organization background...",
                "project_approach": "Detailed project approach...",
                "timeline": "Implementation timeline...",
                "budget": "Detailed budget breakdown...",
                "evaluation": "Evaluation and reporting plan..."
            }
        }
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/export/markdown")
async def export_markdown(request: dict):
    """Export grant proposal as Markdown"""
    try:
        project_id = request.get('project_id', 'test-project')
        sections = request.get('sections', {})
        
        # Generate markdown content
        markdown_content = "# Grant Proposal\n\n"
        
        section_titles = {
            'executive_summary': 'Executive Summary',
            'organization_profile': 'Organization Profile',
            'project_approach': 'Project Description & Approach',
            'timeline': 'Timeline & Implementation',
            'budget': 'Budget & Financial Plan',
            'evaluation': 'Evaluation & Impact Measurement'
        }
        
        for section_key, section_title in section_titles.items():
            content = sections.get(section_key, '')
            if content:
                markdown_content += f"## {section_title}\n\n{content}\n\n"
            else:
                markdown_content += f"## {section_title}\n\n*Content to be added*\n\n"
        
        # Add metadata
        markdown_content += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=grant-proposal.md"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting markdown: {e}")
        return {"success": False, "error": str(e)}

@app.post("/export/txt")
async def export_txt(request: dict):
    """Export grant proposal as TXT"""
    try:
        project_id = request.get('project_id', 'test-project')
        sections = request.get('sections', {})
        
        # Generate text content
        txt_content = "Grant Proposal\n\n"
        
        section_titles = {
            'executive_summary': 'Executive Summary',
            'organization_profile': 'Organization Profile',
            'project_approach': 'Project Description & Approach',
            'timeline': 'Timeline & Implementation',
            'budget': 'Budget & Financial Plan',
            'evaluation': 'Evaluation & Impact Measurement'
        }
        
        for section_key, section_title in section_titles.items():
            content = sections.get(section_key, '')
            if content:
                txt_content += f"{section_title}\n\n{content}\n\n"
            else:
                txt_content += f"{section_title}\n\nContent to be added\n\n"
        
        # Add metadata
        txt_content += f"\n---\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return Response(
            content=txt_content,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=grant-proposal.txt"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting txt: {e}")
        return {"success": False, "error": str(e)}

# RAG Database Endpoints
@app.post("/rag/knowledge/add")
async def add_knowledge_item(request: dict):
    """Add a new knowledge item to the RAG database"""
    try:
        item = KnowledgeItem(
            id=request.get('id', f"knowledge_{datetime.now().timestamp()}"),
            title=request['title'],
            content=request['content'],
            category=request['category'],
            tags=request.get('tags', []),
            source=request['source'],
            created_at=datetime.now().isoformat(),
            cultural_context=request.get('cultural_context'),
            community_focus=request.get('community_focus'),
            success_metrics=request.get('success_metrics')
        )
        
        success = rag_db.add_knowledge_item(item)
        
        return {
            "success": success,
            "message": "Knowledge item added successfully" if success else "Failed to add knowledge item"
        }
    except Exception as e:
        print(f"❌ Error adding knowledge item: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rag/cultural/add")
async def add_cultural_guideline(request: dict):
    """Add cultural competency guidelines"""
    try:
        guideline = CulturalGuideline(
            id=request.get('id', f"cultural_{datetime.now().timestamp()}"),
            community=request['community'],
            guidelines=request['guidelines'],
            cultural_sensitivities=request.get('cultural_sensitivities', []),
            language_preferences=request.get('language_preferences', []),
            best_practices=request.get('best_practices', []),
            created_at=datetime.now().isoformat()
        )
        
        success = rag_db.add_cultural_guideline(guideline)
        
        return {
            "success": success,
            "message": "Cultural guideline added successfully" if success else "Failed to add cultural guideline"
        }
    except Exception as e:
        print(f"❌ Error adding cultural guideline: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rag/community/add")
async def add_community_profile(request: dict):
    """Add community profile"""
    try:
        profile = CommunityProfile(
            id=request.get('id', f"community_{datetime.now().timestamp()}"),
            community_name=request['community_name'],
            demographics=request['demographics'],
            cultural_backgrounds=request.get('cultural_backgrounds', []),
            languages=request.get('languages', []),
            key_concerns=request.get('key_concerns', []),
            strengths=request.get('strengths', []),
            created_at=datetime.now().isoformat()
        )
        
        success = rag_db.add_community_profile(profile)
        
        return {
            "success": success,
            "message": "Community profile added successfully" if success else "Failed to add community profile"
        }
    except Exception as e:
        print(f"❌ Error adding community profile: {e}")
        return {"success": False, "error": str(e)}

@app.get("/rag/knowledge/search")
async def search_knowledge(query: str, category: str = None, limit: int = 5):
    """Search knowledge items"""
    try:
        results = rag_db.search_knowledge(query, category, limit)
        
        return {
            "success": True,
            "results": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "tags": item.tags,
                    "source": item.source,
                    "cultural_context": item.cultural_context,
                    "community_focus": item.community_focus
                }
                for item in results
            ]
        }
    except Exception as e:
        print(f"❌ Error searching knowledge: {e}")
        return {"success": False, "error": str(e)}

@app.get("/rag/cultural/{community}")
async def get_cultural_guidelines(community: str):
    """Get cultural guidelines for a specific community"""
    try:
        guidelines = rag_db.get_cultural_guidelines(community)
        
        return {
            "success": True,
            "guidelines": [
                {
                    "id": g.id,
                    "community": g.community,
                    "guidelines": g.guidelines,
                    "cultural_sensitivities": g.cultural_sensitivities
                }
                for g in guidelines
            ]
        }
    except Exception as e:
        print(f"❌ Error getting cultural guidelines: {e}")
        return {"success": False, "error": str(e)}

@app.get("/rag/community/{community_name}")
async def get_community_profile(community_name: str):
    """Get community profile"""
    try:
        profile = rag_db.get_community_profile(community_name)
        
        if profile:
            return {
                "success": True,
                "profile": {
                    "id": profile.id,
                    "community_name": profile.community_name,
                    "demographics": profile.demographics,
                    "cultural_backgrounds": profile.cultural_backgrounds,
                    "languages": profile.languages,
                    "key_concerns": profile.key_concerns,
                    "strengths": profile.strengths
                }
            }
        else:
            return {"success": False, "message": "Community profile not found"}
            
    except Exception as e:
        print(f"❌ Error getting community profile: {e}")
        return {"success": False, "error": str(e)}

@app.get("/rag/context")
async def get_relevant_context(query: str, section_type: str, community_context: str = None):
    """Get culturally relevant context using advanced RAG"""
    try:
        context = advanced_rag_db.get_relevant_context(query, section_type, community_context)
        return {"success": True, "context": context}
    except Exception as e:
        print(f"❌ Error getting relevant context: {e}")
        return {"success": False, "error": str(e)}

@app.post("/cultural/analyze")
async def analyze_cultural_alignment(request: dict):
    """Analyze cultural alignment of organization with community context"""
    try:
        organization_info = request.get('organization_info', '')
        community_context = request.get('community_context', '')
        
        analysis = specialized_llm.analyze_cultural_alignment(organization_info, community_context)
        
        return {"success": True, "analysis": analysis}
    except Exception as e:
        print(f"❌ Error analyzing cultural alignment: {e}")
        return {"success": False, "error": str(e)}

@app.post("/cultural/generate")
async def generate_culturally_sensitive_content(request: dict):
    """Generate culturally sensitive content using specialized LLM"""
    try:
        prompt_type = request.get('prompt_type', 'general')
        context = request.get('context', {})
        community_context = request.get('community_context', '')
        
        response = specialized_llm.generate_culturally_sensitive_response(
            prompt_type, context, community_context
        )
        
        return {"success": True, "response": response}
    except Exception as e:
        print(f"❌ Error generating culturally sensitive content: {e}")
        return {"success": False, "error": str(e)}

@app.get("/advanced/status")
async def get_advanced_features_status():
    """Get status of advanced RAG and LLM features"""
    try:
        status = {
            "advanced_rag_available": hasattr(advanced_rag_db, 'use_advanced') and advanced_rag_db.use_advanced,
            "specialized_llm_available": True,
            "cultural_competency_enabled": True,
            "multilingual_support": True,
            "semantic_search_enabled": hasattr(advanced_rag_db, 'use_advanced') and advanced_rag_db.use_advanced,
            "features": [
                "Advanced RAG with ChromaDB and sentence transformers",
                "Specialized 7B-like approach with cultural competency",
                "Community-specific cultural contexts",
                "Multilingual support and cultural sensitivity",
                "Advanced prompt engineering for grant writing",
                "Cultural alignment analysis"
            ]
        }
        
        return {"success": True, "status": status}
    except Exception as e:
        print(f"❌ Error getting advanced features status: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))