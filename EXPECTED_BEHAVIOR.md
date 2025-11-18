# Expected Behavior of AI Grant Writer Agent with ArkBuilders Data

## Overview

The AI Grant Writer Tool uses a **Retrieval-Augmented Generation (RAG)** system that retrieves relevant context from your organization database and uses it to generate culturally-sensitive, organization-specific grant proposals.

---

## How the Agent Works with ArkBuilders Data

### 1. **Data Retrieval (RAG System)**

When you request grant content, the agent will:

1. **Load ArkBuilders Organization Profile**
   - Reads `arkbuilders_organization_profile.json`
   - Extracts: mission, programs, partnerships, target populations, budget capacity
   - Uses this as the primary context for all grant writing

2. **Retrieve Relevant Transcript Content**
   - Searches `arkbuilders_grant_transcript_processed.md` for relevant sections
   - Uses semantic search to find content matching your query
   - Pulls specific details: budget breakdowns, program descriptions, outcomes

3. **Combine with Cultural Knowledge**
   - Integrates community engagement guidelines
   - Applies cultural competency best practices
   - Ensures language is appropriate for target communities

### 2. **Grant Content Generation**

When generating grant sections, the agent will:

#### **Organization Profile Section**
- **Expected Output:**
  - Uses ArkBuilders mission: "Empower men to reach men through intergenerational mental health support"
  - Mentions partnerships: NAMI Franklin County, NAMI Allen County, NAMI A
  - Highlights key programs: Barbershop partnerships, Train-the-Trainer, Intergenerational conversations
  - References geographic focus: Franklin County, Allen County, Harding County, Ohio

#### **Program Description Section**
- **Expected Output:**
  - Describes the 4-phase methodology (Foundation Building → Training → Outreach → Ownership)
  - Details barbershop partnership model (5-8 barbershops)
  - Explains intergenerational approach (grandfathers, fathers, future fathers)
  - Mentions specific trainings: Ending the Silence, QPR
  - Emphasizes men-to-men approach (critical program element)

#### **Budget Section**
- **Expected Output:**
  - Uses the $150,000 budget structure from transcript
  - Breaks down: Admin (10% each), Personnel ($42K), Training ($90K), Stipends ($30K)
  - References specific roles: Program Director (0.5 FTE, $25K), Outreach Coordinator ($17K)
  - Includes ArkBuilders TA/Training line item ($37,500)

#### **Outcomes Section**
- **Expected Output:**
  - For Elders: "Understanding their value and wisdom is needed"
  - For Faith Community: "Stigma reduction and understanding of mental health"
  - For Youth: "Conversation, support, and feeling heard - 'If adults would listen, what would you tell them?'"

#### **Partnership Section**
- **Expected Output:**
  - Describes NAMI Franklin County as fiscal agent
  - Explains workflow: funds distribution, 10% admin fee
  - Details ArkBuilders role: Technical assistance, training, program implementation
  - Mentions NAMI Allen County as local implementation partner

### 3. **Cultural Sensitivity**

The agent will:
- Use inclusive language appropriate for men's mental health context
- Respect the men-to-men approach (not suggesting women facilitators)
- Acknowledge intergenerational dynamics
- Recognize faith community integration
- Use culturally appropriate language for Ohio communities

### 4. **RFP Analysis & Alignment**

When you upload an RFP, the agent will:
- Analyze the RFP requirements
- Compare against ArkBuilders capabilities and programs
- Identify alignment points (e.g., mental health, men's programs, intergenerational work)
- Suggest how ArkBuilders programs match funder priorities
- Flag any gaps or areas needing adjustment

---

## Expected Workflow

### Step 1: Create/Select Project
```
POST /projects
{
  "name": "NAMI Grant - ArkBuilders",
  "organization": "ArkBuilders"
}
```

### Step 2: Set Organization Context
```
POST /organization/create
{
  "name": "ArkBuilders",
  "mission": "...",
  "programs": [...]
}
```
**OR** the agent automatically loads from `arkbuilders_organization_profile.json`

### Step 3: Upload RFP (Optional)
```
POST /rfp/upload
{
  "file": "rfp_document.pdf",
  "project_id": "..."
}
```
Agent analyzes RFP and identifies alignment with ArkBuilders.

### Step 4: Generate Grant Sections
```
POST /chat
{
  "message": "Write the organization profile section",
  "project_id": "...",
  "organization_info": "ArkBuilders"
}
```

**Expected Behavior:**
- Agent retrieves ArkBuilders profile from database
- Searches transcript for relevant details
- Generates section using ArkBuilders-specific information
- Ensures cultural competency
- Returns grant-ready content

### Step 5: Refine & Iterate
```
POST /chat
{
  "message": "Add more detail about the barbershop partnerships",
  "project_id": "..."
}
```

Agent will:
- Pull specific barbershop details from transcript
- Expand on the 5-8 barbershop model
- Add men-to-men conversation details
- Maintain consistency with ArkBuilders approach

---

## Key Features You'll See

### 1. **Context-Aware Responses**
- All responses will reference ArkBuilders specifically
- Uses actual program names, partnerships, and budget figures
- Maintains consistency across all sections

### 2. **Automatic Data Integration**
- When you mention "our organization" or "we", agent knows it's ArkBuilders
- Pulls relevant details from transcript automatically
- Combines multiple data sources for comprehensive responses

### 3. **Cultural Competency**
- Language appropriate for men's mental health context
- Respects intergenerational approach
- Acknowledges faith community integration
- Uses inclusive, non-stigmatizing language

### 4. **Budget Accuracy**
- Uses actual budget figures from transcript ($150K total)
- Maintains correct percentages (10% admin, etc.)
- References specific line items (TA/Training $37.5K, etc.)

### 5. **Partnership Clarity**
- Clearly describes NAMI Franklin County as fiscal agent
- Explains ArkBuilders role as TA/training provider
- Details workflow and fund distribution

---

## Example Interactions

### Example 1: Organization Profile Request
**User:** "Write our organization profile"

**Agent Response (Expected):**
```
ArkBuilders is a nonprofit organization that empowers men to reach men 
through intergenerational mental health support, reducing stigma and 
building community capacity for men's mental health. We partner with 
NAMI Franklin County and NAMI Allen County to deliver men-led mental 
health support programs through barbershop partnerships, intergenerational 
conversations, and community-based training.

Our key programs include:
- Barbershop Mental Health Partnerships: Partnering with 5-8 barbershops 
  to facilitate men-to-men mental health conversations
- Train-the-Trainer Program: Training elders, fathers, and young people 
  in Ending the Silence and QPR
- Intergenerational Community Conversations: Facilitating conversations 
  between elders, fathers, and youth to bridge generational gaps

We serve fathers, grandfathers, future fathers, faith community leaders, 
and youth in Franklin County, Allen County, and Harding County, Ohio.
```

### Example 2: Budget Request
**User:** "What's our budget breakdown?"

**Agent Response (Expected):**
```
Based on the $150,000 grant:

Administrative (10% each):
- NAMI A: $15,000
- NAMI Franklin County: $15,000
Total Admin: $30,000

Program Personnel:
- Program Director (0.5 FTE): $25,000
- Community Outreach Coordinator: $17,000
Total Personnel: $42,000

Training & Technical Assistance:
- ArkBuilders TA/Training: $37,500
- Training & Curriculum Development: $52,500
Total Training: $90,000

Stipends:
- Community Leaders/Elders: $15,000
- Youth Participants: $15,000
Total Stipends: $30,000

Evaluation: $7,500
```

### Example 3: Program Description Request
**User:** "Describe our methodology"

**Agent Response (Expected):**
```
Our program follows a 4-phase approach:

Phase 1: Foundation Building & Partnership Development
- Recruit 5-8 barbershop partners
- Convene leadership group from faith community, elders, fathers, and youth
- Develop community of practice

Phase 2: Training & Capacity Building
- Train-the-trainer sessions for Ending the Silence and QPR
- Mental health stigma reduction training for faith community elders
- Intergenerational leadership development

Phase 3: Outreach & Implementation
- Barbershop-based outreach and engagement
- Community conversations: "If adults would listen, what would you tell them?"
- Intergenerational activities connecting elders and youth

Phase 4: Ownership & Sustainability
- Community ownership of program
- Replication model development
- Foundation for larger funding requests
```

---

## What Makes This Agent Special

1. **Organization-Specific**: Not generic - uses YOUR organization's actual data
2. **Transcript-Enhanced**: Pulls real details from your meeting transcript
3. **Culturally Competent**: Applies cultural sensitivity guidelines
4. **Consistent**: Maintains consistency across all sections
5. **Accurate**: Uses actual budget figures and program details
6. **Context-Aware**: Understands ArkBuilders' unique approach (men-to-men, intergenerational)

---

## Limitations & Considerations

1. **Data Dependency**: Agent only knows what's in the database/transcript
2. **Manual Review**: Always review generated content for accuracy
3. **RFP Requirements**: May need to adjust content to match specific RFP requirements
4. **Updates**: If ArkBuilders programs change, update the database files

---

## Next Steps

1. **Launch the server**: `python launch.py`
2. **Create a project**: Use the frontend or API to create a new grant project
3. **Set organization**: Ensure ArkBuilders is selected as the organization
4. **Start writing**: Ask the agent to generate grant sections
5. **Review & refine**: Iterate on the generated content

The agent will automatically use your ArkBuilders data to generate accurate, culturally-sensitive grant content!

