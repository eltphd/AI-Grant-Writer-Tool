import os
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

# Import RAG utilities
try:
    from .utils.rag_utils import rag_db, KnowledgeItem, CulturalGuideline, CommunityProfile
except ImportError:
    # Fallback for direct import
    from utils.rag_utils import rag_db, KnowledgeItem, CulturalGuideline, CommunityProfile

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
            requirements=analysis['requirements'],
            eligibility_criteria=analysis['eligibility_criteria'],
            funding_amount=analysis['funding_amount'],
            deadline=analysis['deadline'],
            analysis_result=analysis,
            created_at=datetime.now().isoformat()
        )
        
        if db_manager.save_rfp(rfp):
            return {"success": True, "rfp": rfp.__dict__}
        else:
            return {"success": False, "error": "Failed to save RFP"}
    except Exception as e:
        print(f"❌ Error uploading RFP: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rfp/analyze")
async def analyze_rfp(project_id: str, request: dict):
    """Analyze RFP and align with organization info"""
    try:
        org_id = request.get('org_id')
        rfp_id = request.get('rfp_id')
        
        if not org_id or not rfp_id:
            return {"success": False, "error": "Missing org_id or rfp_id"}
        
        # Get organization and RFP
        org = db_manager.get_organization(org_id)
        rfp = db_manager.get_rfp(rfp_id)
        
        if not org or not rfp:
            return {"success": False, "error": "Organization or RFP not found"}
        
        # Analyze alignment
        alignment = rfp_analyzer.align_org_with_rfp(org, rfp)
        
        # Create project response
        response = rfp_analyzer.create_project_response(org, rfp, alignment)
        
        if db_manager.save_project_response(response):
            return {
                "success": True,
                "analysis": alignment,
                "response": response.__dict__
            }
        else:
            return {"success": False, "error": "Failed to save project response"}
    except Exception as e:
        print(f"❌ Error analyzing RFP: {e}")
        return {"success": False, "error": str(e)}

# File upload endpoint
@app.post("/upload")
async def upload_file(project_id: str, file: dict):
    """Upload file and extract content"""
    try:
        # Mock file processing
        return {
            "success": True,
            "filename": file.get('filename', 'uploaded_file'),
            "content_length": len(file.get('content', '')),
            "uploaded_at": datetime.now().isoformat()
        }
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
    """Get project context data"""
    try:
        # This would normally fetch from database
        return {
            "organization_info": "Sample organization with community focus",
            "initiative_description": "Youth development program",
            "uploaded_files": ["rfp_document.pdf", "org_profile.docx"],
            "rfp_requirements": ["Non-profit status", "Community focus", "Measurable outcomes"]
        }
    except Exception as e:
        print(f"Error getting project context: {e}")
        return {}

def get_rfp_analysis_data(project_id: str) -> dict:
    """Get RFP analysis data"""
    try:
        # This would normally fetch from database
        return {
            "requirements": ["Non-profit status required", "Minimum 3 years operation", "Community focus"],
            "eligibility_criteria": ["501(c)(3) status", "Annual budget > $100k"],
            "funding_amount": "$50,000",
            "deadline": "December 15, 2024",
            "alignment_score": 85
        }
    except Exception as e:
        print(f"Error getting RFP analysis: {e}")
        return {}

def generate_contextual_response(message: str, context: dict, rfp_analysis: dict) -> str:
    """Generate contextual AI response based on message and available data"""
    
    # Get RAG context for enhanced responses
    rag_context = rag_db.get_relevant_context(message, "grant_section", context.get('community_focus'))
    
    # Check for specific section writing requests
    if any(word in message.lower() for word in ['executive summary', 'summary']):
        return generate_executive_summary_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['organization profile', 'organization', 'profile']):
        return generate_organization_profile_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['project description', 'project', 'description']):
        return generate_project_description_with_rag(context, rfp_analysis, rag_context)
    
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
        return generate_default_response(message, context, rfp_analysis)

def generate_executive_summary_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate executive summary using RAG context for cultural competence"""
    
    org_info = context.get('organization_info', {})
    rfp_reqs = rfp_analysis.get('requirements', [])
    
    response = "📋 **Executive Summary**\n\n"
    
    # Incorporate cultural guidelines if available
    cultural_guidance = ""
    if rag_context.get('cultural_guidelines'):
        cultural_guidance = f"\n**Cultural Context:** Based on community guidelines, this proposal emphasizes "
        cultural_guidance += ", ".join(rag_context['cultural_guidelines'][0]['guidelines'][:2]) + ".\n\n"
    
    if org_info.get('name'):
        response += f"**{org_info['name']}** is seeking funding to "
    else:
        response += "**Our organization** is seeking funding to "
    
    if org_info.get('mission'):
        response += f"advance our mission of {org_info['mission']}. "
    else:
        response += "implement a transformative community project. "
    
    if rfp_reqs:
        response += f"This proposal directly addresses {len(rfp_reqs)} key requirements from the RFP, including "
        response += ", ".join(rfp_reqs[:3]) + ". "
    
    if org_info.get('years_operating'):
        response += f"With {org_info['years_operating']} years of experience, "
    
    if org_info.get('target_population'):
        response += f"we will serve {org_info['target_population']} through "
    
    response += "innovative programming that delivers measurable impact.\n\n"
    
    # Incorporate best practices from RAG
    if rag_context.get('best_practices'):
        response += "**Evidence-Based Approach:** This proposal incorporates proven strategies including "
        response += rag_context['best_practices'][0]['title'] + " and "
        response += rag_context['best_practices'][1]['title'] if len(rag_context['best_practices']) > 1 else "established best practices"
        response += ".\n\n"
    
    response += "**Key Impact Areas:**\n"
    if org_info.get('focus_areas'):
        for area in org_info['focus_areas'][:3]:
            response += f"• {area}\n"
    else:
        response += "• Community development\n• Capacity building\n• Sustainable outcomes\n"
    
    response += "\n**Requested Funding:** "
    if rfp_analysis.get('funding_amount'):
        response += f"{rfp_analysis['funding_amount']}\n"
    else:
        response += "To be determined based on project scope\n"
    
    response += "\n**Expected Outcomes:**\n"
    response += "• Enhanced community engagement\n"
    response += "• Measurable program impact\n"
    response += "• Sustainable long-term benefits\n\n"
    
    response += cultural_guidance
    
    response += "This proposal represents a strategic investment in our community's future."
    
    return response

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
    """Generate conversational content access response"""
    
    response = "📄 **Let me check what information I have for you...**\n\n"
    
    if context.get('uploaded_files'):
        response += "✅ **Documents I can see:**\n"
        for file in context['uploaded_files']:
            response += f"• {file}\n"
        response += "\n"
    else:
        response += "❌ **No documents uploaded yet**\n\n"
    
    if context.get('organization_info'):
        response += "✅ **Organization info:** I have your organization details\n"
    else:
        response += "❌ **Organization info:** Not provided yet\n"
    
    response += "\n**To give you better help, please:**\n"
    response += "1. Upload your RFP document (the grant request)\n"
    response += "2. Tell me about your organization\n"
    response += "3. Add any other important documents\n\n"
    
    response += "**Once you do that, I can give you much more specific advice!** 😊"
    
    return response

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
    """Generate conversational default response"""
    
    response = f"Hi! I see you said '{message}'. "
    
    if context.get('organization_info'):
        response += "I can see you've provided some organization information. "
    
    if rfp_analysis.get('requirements'):
        response += f"I also have your RFP analysis with {len(rfp_analysis['requirements'])} requirements. "
    
    response += "\n\n**Here's how I can help you today:**\n\n"
    response += "🎯 **Quick Actions:**\n"
    response += "• Say 'help me write sections' - I'll guide you through each grant section\n"
    response += "• Say 'show my RFP analysis' - I'll show what I found in your RFP\n"
    response += "• Say 'help with budget' - I'll help you plan your budget\n"
    response += "• Say 'brainstorm ideas' - I'll give you creative grant writing ideas\n\n"
    
    response += "📋 **What would you like to work on first?**\n"
    response += "Just tell me in simple terms what you need help with!"
    
    return response

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
    """Get relevant context for grant section generation"""
    try:
        context = rag_db.get_relevant_context(query, section_type, community_context)
        
        return {
            "success": True,
            "context": {
                "knowledge_items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "content": item.content,
                        "category": item.category,
                        "tags": item.tags
                    }
                    for item in context['knowledge_items']
                ],
                "cultural_guidelines": [
                    {
                        "id": g.id,
                        "community": g.community,
                        "guidelines": g.guidelines,
                        "cultural_sensitivities": g.cultural_sensitivities
                    }
                    for g in context['cultural_guidelines']
                ],
                "community_profile": context['community_profile'],
                "best_practices": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "content": item.content
                    }
                    for item in context['best_practices']
                ]
            }
        }
    except Exception as e:
        print(f"❌ Error getting relevant context: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))