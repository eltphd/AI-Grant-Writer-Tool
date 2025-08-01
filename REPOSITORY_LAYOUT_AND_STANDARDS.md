# AI Grant Writer Tool - Repository Layout and Development Standards

## Executive Summary

This document outlines the repository structure, version control strategy, and coding standards for the AI Grant Writer Tool. The project follows a monorepo structure with clear separation of concerns, comprehensive version control practices, and strict coding standards to ensure code quality and maintainability.

## 1. Repository Layout

### 1.1 Monorepo Structure

```
AI-Grant-Writer-Tool/
├── frontend/                          # React frontend application
│   ├── public/                        # Static assets
│   ├── src/                           # Source code
│   │   ├── components/                # React components
│   │   │   ├── auth/                  # Authentication components
│   │   │   ├── chat/                  # Chat interface components
│   │   │   ├── cultural/              # Cultural competency components
│   │   │   ├── documents/             # Document management components
│   │   │   ├── evaluation/            # Quality assessment components
│   │   │   ├── navigation/            # Navigation components
│   │   │   └── shared/                # Shared UI components
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── services/                  # API service layer
│   │   ├── utils/                     # Utility functions
│   │   ├── styles/                    # CSS and styling
│   │   ├── types/                     # TypeScript type definitions
│   │   └── contexts/                  # React contexts
│   ├── tests/                         # Frontend tests
│   ├── package.json                   # Frontend dependencies
│   └── README.md                      # Frontend documentation
│
├── backend/                           # FastAPI backend application
│   ├── src/                           # Source code
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── api/                       # API route handlers
│   │   │   ├── auth/                  # Authentication endpoints
│   │   │   ├── chat/                  # Chat endpoints
│   │   │   ├── cultural/              # Cultural competency endpoints
│   │   │   ├── documents/             # Document management endpoints
│   │   │   ├── evaluation/            # Quality assessment endpoints
│   │   │   └── rag/                   # RAG system endpoints
│   │   ├── core/                      # Core application logic
│   │   │   ├── config.py              # Configuration management
│   │   │   ├── security.py            # Security utilities
│   │   │   └── exceptions.py          # Custom exceptions
│   │   ├── models/                    # Data models
│   │   │   ├── user.py                # User model
│   │   │   ├── document.py            # Document model
│   │   │   ├── cultural.py            # Cultural data models
│   │   │   └── evaluation.py          # Evaluation models
│   │   ├── services/                  # Business logic services
│   │   │   ├── rag_service.py         # RAG system service
│   │   │   ├── llm_service.py         # LLM service
│   │   │   ├── cultural_service.py    # Cultural competency service
│   │   │   └── evaluation_service.py  # Quality assessment service
│   │   ├── utils/                     # Utility modules
│   │   │   ├── advanced_rag_utils.py  # Advanced RAG utilities
│   │   │   ├── specialized_llm_utils.py # Specialized LLM utilities
│   │   │   ├── evaluation_utils.py    # Evaluation utilities
│   │   │   ├── cultural_utils.py      # Cultural competency utilities
│   │   │   └── file_utils.py          # File processing utilities
│   │   └── database/                  # Database layer
│   │       ├── models.py              # Database models
│   │       ├── migrations/            # Database migrations
│   │       └── repositories.py        # Data access layer
│   ├── tests/                         # Backend tests
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   └── e2e/                       # End-to-end tests
│   ├── requirements.txt               # Python dependencies
│   └── README.md                      # Backend documentation
│
├── llm_models/                        # LLM and AI model components
│   ├── models/                        # Model definitions
│   │   ├── cultural_models.py         # Cultural competency models
│   │   ├── cognitive_models.py        # Cognitive friendliness models
│   │   └── evaluation_models.py       # Quality evaluation models
│   ├── prompts/                       # Prompt templates
│   │   ├── cultural_prompts.py        # Cultural competency prompts
│   │   ├── grant_writing_prompts.py   # Grant writing prompts
│   │   └── evaluation_prompts.py      # Evaluation prompts
│   ├── training/                      # Model training scripts
│   │   ├── fine_tuning.py             # Fine-tuning scripts
│   │   ├── cultural_training.py       # Cultural competency training
│   │   └── evaluation_training.py     # Evaluation model training
│   ├── evaluation/                    # Model evaluation
│   │   ├── cultural_evaluation.py     # Cultural competency evaluation
│   │   ├── cognitive_evaluation.py    # Cognitive friendliness evaluation
│   │   └── performance_evaluation.py  # Performance evaluation
│   └── README.md                      # LLM models documentation
│
├── rag_data/                          # RAG system data and knowledge base
│   ├── knowledge_base/                # Knowledge base data
│   │   ├── grant_narratives/          # Grant writing examples
│   │   ├── cultural_guidelines/       # Cultural competency guidelines
│   │   ├── organization_profiles/     # Organization profiles
│   │   ├── expert_feedback/           # Expert feedback data
│   │   └── community_contexts/        # Community context data
│   ├── embeddings/                    # Pre-computed embeddings
│   │   ├── cultural_embeddings/       # Cultural context embeddings
│   │   ├── grant_embeddings/          # Grant writing embeddings
│   │   └── community_embeddings/      # Community context embeddings
│   ├── processing/                    # Data processing scripts
│   │   ├── data_collection.py         # Data collection scripts
│   │   ├── data_cleaning.py           # Data cleaning scripts
│   │   ├── embedding_generation.py    # Embedding generation scripts
│   │   └── quality_assessment.py      # Data quality assessment
│   ├── validation/                    # Data validation
│   │   ├── cultural_validation.py     # Cultural data validation
│   │   ├── expert_validation.py       # Expert validation scripts
│   │   └── community_validation.py    # Community validation scripts
│   └── README.md                      # RAG data documentation
│
├── docs/                              # Project documentation
│   ├── technical/                     # Technical documentation
│   │   ├── architecture.md            # System architecture
│   │   ├── api_documentation.md       # API documentation
│   │   ├── deployment.md              # Deployment guide
│   │   └── development.md             # Development guide
│   ├── cultural/                      # Cultural competency documentation
│   │   ├── cultural_guidelines.md     # Cultural competency guidelines
│   │   ├── community_contexts.md      # Community context documentation
│   │   ├── expert_validation.md       # Expert validation process
│   │   └── cultural_sensitivity.md    # Cultural sensitivity guidelines
│   ├── user/                          # User documentation
│   │   ├── user_guide.md              # User guide
│   │   ├── api_reference.md           # API reference
│   │   └── troubleshooting.md         # Troubleshooting guide
│   └── README.md                      # Documentation index
│
├── infrastructure/                    # Infrastructure and deployment
│   ├── docker/                        # Docker configuration
│   │   ├── Dockerfile                 # Main application Dockerfile
│   │   ├── docker-compose.yml         # Docker Compose configuration
│   │   └── docker-compose.prod.yml    # Production Docker configuration
│   ├── kubernetes/                    # Kubernetes configuration
│   │   ├── deployments/               # Kubernetes deployments
│   │   ├── services/                  # Kubernetes services
│   │   └── configmaps/                # Kubernetes config maps
│   ├── terraform/                     # Infrastructure as Code
│   │   ├── modules/                   # Terraform modules
│   │   ├── environments/              # Environment configurations
│   │   └── variables.tf               # Terraform variables
│   ├── monitoring/                    # Monitoring configuration
│   │   ├── prometheus/                # Prometheus configuration
│   │   ├── grafana/                   # Grafana dashboards
│   │   └── alerts/                    # Alerting rules
│   └── scripts/                       # Deployment scripts
│       ├── deploy.sh                  # Deployment script
│       ├── backup.sh                  # Backup script
│       └── monitoring.sh              # Monitoring script
│
├── tests/                             # End-to-end tests
│   ├── e2e/                           # End-to-end test suites
│   │   ├── cultural_competency/       # Cultural competency tests
│   │   ├── cognitive_friendliness/    # Cognitive friendliness tests
│   │   ├── performance/               # Performance tests
│   │   └── security/                  # Security tests
│   ├── integration/                   # Integration tests
│   │   ├── api_integration/           # API integration tests
│   │   ├── rag_integration/           # RAG system integration tests
│   │   └── llm_integration/           # LLM integration tests
│   └── performance/                   # Performance tests
│       ├── load_tests/                # Load testing
│       ├── stress_tests/              # Stress testing
│       └── cultural_performance/      # Cultural competency performance
│
├── scripts/                           # Development and utility scripts
│   ├── setup/                         # Setup scripts
│   │   ├── install_dependencies.sh    # Dependency installation
│   │   ├── setup_environment.sh       # Environment setup
│   │   └── setup_cultural_data.sh     # Cultural data setup
│   ├── development/                   # Development scripts
│   │   ├── lint.sh                    # Linting script
│   │   ├── test.sh                    # Testing script
│   │   ├── format.sh                  # Code formatting script
│   │   └── security_check.sh          # Security check script
│   ├── data/                          # Data processing scripts
│   │   ├── collect_cultural_data.py   # Cultural data collection
│   │   ├── validate_cultural_data.py  # Cultural data validation
│   │   └── update_knowledge_base.py   # Knowledge base updates
│   └── monitoring/                    # Monitoring scripts
│       ├── performance_monitor.py     # Performance monitoring
│       ├── cultural_monitor.py        # Cultural competency monitoring
│       └── quality_monitor.py         # Quality assessment monitoring
│
├── config/                            # Configuration files
│   ├── development/                   # Development configuration
│   │   ├── app.config.json            # Application configuration
│   │   ├── database.config.json       # Database configuration
│   │   └── cultural.config.json       # Cultural competency configuration
│   ├── production/                    # Production configuration
│   │   ├── app.config.json            # Production app configuration
│   │   ├── database.config.json       # Production database configuration
│   │   └── security.config.json       # Security configuration
│   └── cultural/                      # Cultural competency configuration
│       ├── community_contexts.json    # Community context definitions
│       ├── cultural_guidelines.json   # Cultural competency guidelines
│       └── evaluation_criteria.json   # Evaluation criteria
│
├── .github/                           # GitHub configuration
│   ├── workflows/                     # GitHub Actions workflows
│   │   ├── ci.yml                     # Continuous integration
│   │   ├── cd.yml                     # Continuous deployment
│   │   ├── cultural_validation.yml    # Cultural competency validation
│   │   └── security_scan.yml          # Security scanning
│   ├── ISSUE_TEMPLATE/                # Issue templates
│   │   ├── bug_report.md              # Bug report template
│   │   ├── feature_request.md         # Feature request template
│   │   └── cultural_issue.md          # Cultural competency issue template
│   └── PULL_REQUEST_TEMPLATE.md       # Pull request template
│
├── .vscode/                           # VS Code configuration
│   ├── settings.json                  # Editor settings
│   ├── extensions.json                # Recommended extensions
│   └── launch.json                    # Debug configuration
│
├── .gitignore                         # Git ignore rules
├── README.md                          # Project overview
├── CONTRIBUTING.md                    # Contribution guidelines
├── CODE_OF_CONDUCT.md                 # Code of conduct
├── LICENSE                            # Project license
└── CHANGELOG.md                       # Change log
```

### 1.2 Key Directory Purposes

#### **Frontend Directory (`frontend/`)**
- **React Application**: Modern React with TypeScript
- **Component Organization**: Cultural competency components, evaluation components
- **Service Layer**: API integration with cultural sensitivity
- **Type Safety**: Comprehensive TypeScript definitions

#### **Backend Directory (`backend/`)**
- **FastAPI Application**: High-performance Python backend
- **API Organization**: Cultural competency endpoints, evaluation endpoints
- **Service Layer**: RAG service, LLM service, cultural service
- **Database Layer**: Cultural data models and repositories

#### **LLM Models Directory (`llm_models/`)**
- **Model Definitions**: Cultural competency models, cognitive friendliness models
- **Prompt Engineering**: Cultural prompts, grant writing prompts
- **Training Scripts**: Fine-tuning for cultural competency
- **Evaluation**: Cultural competency evaluation, performance evaluation

#### **RAG Data Directory (`rag_data/`)**
- **Knowledge Base**: Cultural guidelines, community contexts, expert feedback
- **Embeddings**: Pre-computed cultural context embeddings
- **Processing**: Data collection, cleaning, quality assessment
- **Validation**: Cultural validation, expert validation, community validation

#### **Documentation Directory (`docs/`)**
- **Technical Documentation**: Architecture, API, deployment guides
- **Cultural Documentation**: Cultural competency guidelines, community contexts
- **User Documentation**: User guides, API reference, troubleshooting

#### **Infrastructure Directory (`infrastructure/`)**
- **Docker Configuration**: Containerization with cultural data considerations
- **Kubernetes**: Scalable deployment with cultural competency monitoring
- **Monitoring**: Performance monitoring, cultural competency monitoring
- **Scripts**: Deployment, backup, monitoring scripts

## 2. Version Control Strategy

### 2.1 Branching Model: Gitflow with Cultural Competency Focus

#### **Main Branches:**
```
main/                    # Production-ready code
├── develop/             # Development integration branch
├── cultural/            # Cultural competency development branch
├── feature/             # Feature development branches
├── release/             # Release preparation branches
└── hotfix/              # Critical production fixes
```

#### **Branch Naming Conventions:**
```
# Feature branches
feature/cultural-competency-evaluation
feature/cognitive-friendliness-assessment
feature/community-context-integration
feature/expert-feedback-system

# Bug fix branches
bugfix/cultural-sensitivity-issue
bugfix/cognitive-accessibility-problem
bugfix/community-validation-error

# Release branches
release/v1.2.0-cultural-enhancements
release/v1.3.0-cognitive-improvements

# Hotfix branches
hotfix/critical-cultural-data-issue
hotfix/security-cultural-data-breach
```

### 2.2 Commit Message Conventions

#### **Conventional Commits with Cultural Focus:**
```
# Format: <type>(<scope>): <description>

# Cultural competency commits
feat(cultural): add community context validation
fix(cultural): resolve cultural sensitivity issue in prompts
docs(cultural): update cultural competency guidelines
test(cultural): add cultural competency evaluation tests

# Cognitive friendliness commits
feat(cognitive): implement readability assessment
fix(cognitive): improve accessibility in chat interface
docs(cognitive): add cognitive friendliness guidelines
test(cognitive): add cognitive accessibility tests

# RAG system commits
feat(rag): integrate cultural knowledge base
fix(rag): resolve cultural context retrieval issue
docs(rag): update cultural data processing guide
test(rag): add cultural embedding tests

# LLM commits
feat(llm): add cultural prompt engineering
fix(llm): resolve cultural bias in responses
docs(llm): update cultural competency prompts
test(llm): add cultural evaluation tests

# General commits
feat(auth): add cultural context to user profiles
fix(api): resolve cultural data validation issue
docs(api): update cultural competency endpoints
test(api): add cultural data validation tests
```

#### **Commit Types:**
- **feat**: New cultural competency features
- **fix**: Cultural sensitivity or accessibility fixes
- **docs**: Cultural competency documentation
- **style**: Cultural UI/UX improvements
- **refactor**: Cultural code improvements
- **test**: Cultural competency tests
- **chore**: Cultural data maintenance

#### **Scope Examples:**
- **cultural**: Cultural competency features
- **cognitive**: Cognitive friendliness features
- **rag**: RAG system features
- **llm**: LLM model features
- **api**: API endpoints
- **ui**: User interface
- **docs**: Documentation
- **test**: Testing

### 2.3 Pull Request Process

#### **Cultural Competency Review Process:**
1. **Cultural Expert Review**: Cultural competency expert review
2. **Community Validation**: Community representative validation
3. **Technical Review**: Technical implementation review
4. **Accessibility Review**: Cognitive friendliness review
5. **Security Review**: Cultural data security review

#### **Pull Request Template:**
```markdown
## Cultural Competency Impact
- [ ] Cultural sensitivity reviewed
- [ ] Community voice represented
- [ ] Traditional knowledge respected
- [ ] Cultural protocols followed

## Cognitive Friendliness Impact
- [ ] Accessibility standards met
- [ ] Readability improved
- [ ] User experience enhanced
- [ ] Clear language used

## Technical Implementation
- [ ] Code quality standards met
- [ ] Tests included and passing
- [ ] Documentation updated
- [ ] Performance considered

## Security and Privacy
- [ ] Cultural data protected
- [ ] Community consent respected
- [ ] Security standards met
- [ ] Privacy guidelines followed
```

## 3. Coding Standards

### 3.1 Python Coding Standards (Backend)

#### **PEP 8 with Cultural Considerations:**
```python
# Cultural competency imports
from cultural_utils import CulturalContext, CommunityProfile
from evaluation_utils import CulturalEvaluator, CognitiveEvaluator
from rag_utils import CulturalKnowledgeItem, CulturalGuideline

# Cultural competency class naming
class CulturalCompetencyService:
    """Service for managing cultural competency features."""
    
    def __init__(self, cultural_context: CulturalContext):
        self.cultural_context = cultural_context
        self.evaluator = CulturalEvaluator()
    
    def evaluate_cultural_sensitivity(self, content: str) -> float:
        """
        Evaluate cultural sensitivity of content.
        
        Args:
            content: Text content to evaluate
            
        Returns:
            Cultural sensitivity score (0-100)
        """
        return self.evaluator.evaluate_sensitivity(content, self.cultural_context)

# Cultural data structures
@dataclass
class CulturalKnowledgeItem:
    """Represents cultural knowledge item in RAG system."""
    
    id: str
    title: str
    content: str
    cultural_context: str
    community_focus: str
    cultural_sensitivity_score: Optional[float] = None
    expert_validation: bool = False
    pilot_test_results: Optional[Dict] = None
```

#### **Cultural Competency Code Organization:**
```python
# Cultural competency module structure
cultural_competency/
├── __init__.py
├── models.py              # Cultural data models
├── services.py            # Cultural competency services
├── evaluators.py          # Cultural evaluation logic
├── validators.py          # Cultural data validation
├── utils.py               # Cultural utility functions
└── tests/                 # Cultural competency tests
    ├── test_models.py
    ├── test_services.py
    ├── test_evaluators.py
    └── test_validators.py
```

### 3.2 TypeScript/JavaScript Standards (Frontend)

#### **Cultural UI Component Standards:**
```typescript
// Cultural competency interface definitions
interface CulturalContext {
  communityType: 'urban' | 'rural' | 'indigenous';
  culturalValues: string[];
  communicationStyles: string[];
  communityStrengths: string[];
  culturalProtocols: string[];
}

interface CulturalEvaluationResult {
  culturalSensitivityScore: number;
  communityVoiceRepresentation: number;
  traditionalKnowledgeRespect: number;
  stereotypeAvoidance: number;
  recommendations: string[];
}

// Cultural competency component
interface CulturalCompetencyProps {
  culturalContext: CulturalContext;
  onEvaluationComplete: (result: CulturalEvaluationResult) => void;
  communityFocus: string;
  expertValidation: boolean;
}

const CulturalCompetencyComponent: React.FC<CulturalCompetencyProps> = ({
  culturalContext,
  onEvaluationComplete,
  communityFocus,
  expertValidation
}) => {
  // Component implementation with cultural sensitivity
};
```

#### **Cultural Accessibility Standards:**
```typescript
// Cultural accessibility hooks
const useCulturalAccessibility = (culturalContext: CulturalContext) => {
  const [accessibilityLevel, setAccessibilityLevel] = useState('high');
  
  const checkCulturalAccessibility = useCallback((content: string) => {
    // Cultural accessibility checking logic
  }, [culturalContext]);
  
  return { accessibilityLevel, checkCulturalAccessibility };
};

// Cultural UI components
const CulturalSensitiveButton: React.FC<ButtonProps> = ({
  children,
  culturalContext,
  ...props
}) => {
  const { accessibilityLevel } = useCulturalAccessibility(culturalContext);
  
  return (
    <button
      className={`cultural-sensitive-button ${accessibilityLevel}`}
      aria-label={`Culturally sensitive ${children}`}
      {...props}
    >
      {children}
    </button>
  );
};
```

### 3.3 Linting and Formatting Rules

#### **Python Linting (Black + isort + flake8):**
```ini
# .flake8 configuration
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    *.egg-info,
    cultural_data,
    rag_data

# Cultural competency specific rules
per-file-ignores =
    cultural_utils.py: E501  # Allow longer lines for cultural descriptions
    evaluation_utils.py: E501  # Allow longer lines for evaluation criteria
```

#### **TypeScript Linting (ESLint + Prettier):**
```json
// .eslintrc.json
{
  "extends": [
    "@typescript-eslint/recommended",
    "react-hooks/recommended",
    "cultural-accessibility/recommended"
  ],
  "rules": {
    "cultural-sensitivity/respectful-language": "error",
    "cultural-sensitivity/community-voice": "warn",
    "accessibility/aria-labels": "error",
    "accessibility/color-contrast": "warn"
  }
}
```

#### **Cultural Competency Linting Rules:**
```javascript
// Cultural competency ESLint plugin
module.exports = {
  rules: {
    'cultural-sensitivity/respectful-language': {
      create(context) {
        return {
          Literal(node) {
            // Check for culturally insensitive language
            const text = node.value;
            if (containsInsensitiveLanguage(text)) {
              context.report({
                node,
                message: 'Use culturally respectful language'
              });
            }
          }
        };
      }
    }
  }
};
```

### 3.4 Testing Standards

#### **Cultural Competency Testing:**
```python
# Cultural competency test structure
class TestCulturalCompetency:
    """Test cultural competency features."""
    
    def test_cultural_sensitivity_evaluation(self):
        """Test cultural sensitivity evaluation."""
        evaluator = CulturalEvaluator()
        content = "This community demonstrates resilience..."
        score = evaluator.evaluate_sensitivity(content)
        assert 0 <= score <= 100
        assert score >= 80  # Minimum cultural sensitivity threshold
    
    def test_community_voice_representation(self):
        """Test community voice representation."""
        content = "Our community has identified..."
        representation = evaluator.evaluate_community_voice(content)
        assert representation >= 0.8  # 80% community voice threshold
    
    def test_traditional_knowledge_respect(self):
        """Test traditional knowledge respect."""
        content = "Traditional knowledge teaches us..."
        respect_score = evaluator.evaluate_traditional_knowledge(content)
        assert respect_score >= 0.9  # 90% traditional knowledge respect
```

#### **Cognitive Friendliness Testing:**
```python
# Cognitive friendliness test structure
class TestCognitiveFriendliness:
    """Test cognitive friendliness features."""
    
    def test_readability_assessment(self):
        """Test readability assessment."""
        evaluator = CognitiveEvaluator()
        content = "Clear, simple language for all users."
        readability = evaluator.assess_readability(content)
        assert readability.flesch_reading_ease >= 60
        assert readability.average_sentence_length <= 20
    
    def test_accessibility_features(self):
        """Test accessibility features."""
        content = "• Bullet points\n• Clear structure\n• Simple language"
        accessibility = evaluator.assess_accessibility(content)
        assert accessibility.has_bullet_points
        assert accessibility.has_clear_structure
        assert accessibility.uses_simple_language
```

### 3.5 Documentation Standards

#### **Cultural Competency Documentation:**
```python
"""
Cultural Competency Module

This module provides cultural competency evaluation and validation features
for the AI Grant Writer Tool. It ensures that all content generated
respects cultural diversity and community values.

Key Features:
- Cultural sensitivity evaluation
- Community voice representation
- Traditional knowledge respect
- Expert validation integration
- Community pilot testing

Cultural Contexts Supported:
- Urban communities: Diversity, accessibility, systemic barriers
- Rural communities: Tradition, self-reliance, geographic barriers
- Indigenous communities: Traditional knowledge, cultural protocols

Example Usage:
    >>> evaluator = CulturalEvaluator()
    >>> score = evaluator.evaluate_sensitivity(content, cultural_context)
    >>> print(f"Cultural sensitivity score: {score}")
"""

class CulturalEvaluator:
    """
    Evaluates cultural competency of content.
    
    This class provides comprehensive cultural competency evaluation
    including cultural sensitivity, community voice representation,
    and traditional knowledge respect.
    
    Attributes:
        cultural_contexts: Available cultural contexts
        expert_validators: Cultural expert validators
        community_feedback: Community feedback integration
        
    Methods:
        evaluate_sensitivity: Evaluate cultural sensitivity
        evaluate_community_voice: Evaluate community voice representation
        evaluate_traditional_knowledge: Evaluate traditional knowledge respect
    """
```

#### **API Documentation Standards:**
```python
@router.post("/cultural/evaluate")
async def evaluate_cultural_competency(
    request: CulturalEvaluationRequest,
    cultural_context: CulturalContext = Depends(get_cultural_context)
) -> CulturalEvaluationResponse:
    """
    Evaluate cultural competency of content.
    
    This endpoint evaluates the cultural competency of provided content
    using multiple criteria including cultural sensitivity, community
    voice representation, and traditional knowledge respect.
    
    Args:
        request: Cultural evaluation request containing content
        cultural_context: Cultural context for evaluation
        
    Returns:
        Cultural evaluation response with scores and recommendations
        
    Raises:
        CulturalValidationError: If content violates cultural protocols
        CommunityConsentError: If community consent is required but not provided
        
    Example:
        >>> response = await evaluate_cultural_competency(
        ...     request=CulturalEvaluationRequest(content="..."),
        ...     cultural_context=urban_context
        ... )
        >>> print(f"Cultural sensitivity: {response.cultural_sensitivity_score}")
    """
```

## 4. Development Workflow

### 4.1 Cultural Competency Development Process

#### **Feature Development Workflow:**
1. **Cultural Context Analysis**: Understand cultural context requirements
2. **Expert Consultation**: Consult with cultural experts
3. **Community Input**: Gather community input and feedback
4. **Implementation**: Implement with cultural sensitivity
5. **Expert Validation**: Validate with cultural experts
6. **Community Testing**: Test with community representatives
7. **Documentation**: Document cultural considerations

#### **Cultural Competency Review Checklist:**
- [ ] Cultural sensitivity reviewed
- [ ] Community voice represented
- [ ] Traditional knowledge respected
- [ ] Cultural protocols followed
- [ ] Expert validation completed
- [ ] Community testing conducted
- [ ] Documentation updated
- [ ] Accessibility standards met

### 4.2 Code Review Process

#### **Cultural Competency Review:**
- **Cultural Expert Review**: Cultural competency expert review
- **Community Representative Review**: Community representative review
- **Accessibility Review**: Cognitive friendliness review
- **Security Review**: Cultural data security review
- **Technical Review**: Technical implementation review

#### **Review Criteria:**
- **Cultural Sensitivity**: Respect for cultural diversity
- **Community Voice**: Authentic community representation
- **Traditional Knowledge**: Respect for traditional knowledge
- **Accessibility**: Cognitive friendliness and accessibility
- **Security**: Cultural data protection
- **Performance**: System performance and scalability

## 5. Conclusion

This comprehensive repository layout and development standards document provides a solid foundation for building a culturally competent, cognitively friendly AI grant writing assistant. The monorepo structure ensures clear separation of concerns while maintaining cultural competency focus throughout the development process.

The version control strategy prioritizes cultural competency and community validation, ensuring that all changes respect cultural diversity and community values. The coding standards emphasize cultural sensitivity, accessibility, and community voice representation.

The implementation of these standards will enable the development team to build a truly inclusive, culturally sensitive, and community-relevant AI grant writing assistant that respects and celebrates the diversity of communities served. 