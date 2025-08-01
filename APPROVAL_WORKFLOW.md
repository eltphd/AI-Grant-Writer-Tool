# Approval Workflow System

## Overview

The Approval Workflow System integrates evaluation feedback loops with human approval mechanisms to ensure culturally sensitive and secure content generation. This system provides proactive guardrails and approval workflows for sensitive data handling.

## Key Features

### 1. Evaluation Feedback Loop
- **Cultural Competency Evaluation**: Automatically evaluates AI responses for cultural sensitivity
- **Sensitivity Detection**: Identifies potential PII, cultural references, and confidential information
- **Automatic Regeneration**: Triggers response regeneration when cultural competency scores are low
- **Approval Flagging**: Flags content for human review when sensitive content is detected

### 2. Approval Workflow
- **Pending Approvals Dashboard**: View all content requiring approval
- **Approval/Denial Actions**: Grant or deny access to sensitive content
- **Secure Storage Access**: Temporary access grants for approved content
- **Audit Trail**: Complete logging of approval decisions and access

### 3. Sensitivity Detection
- **PII Detection**: Email addresses, phone numbers, names
- **Cultural Sensitivity**: Multiple cultural references
- **Financial Data**: Dollar amounts, large numbers
- **Configurable Thresholds**: Adjustable sensitivity levels

## Architecture

### Backend Components

#### 1. Evaluation Engine (`src/main.py`)
```python
def _evaluate_response_with_feedback_loop(response: str, community_context: str, context: dict) -> dict:
    """Evaluate response and determine if regeneration or approval is needed"""
    
    evaluation_result = {
        'cultural_score': 0.0,
        'sensitivity_flags': [],
        'needs_regeneration': False,
        'requires_approval': False,
        'recommendations': []
    }
    
    # Cultural competency evaluation
    cultural_eval = cultural_evaluator.evaluate_response(response, community_context)
    evaluation_result['cultural_score'] = cultural_eval.get('overall_score', 0.0)
    
    # Sensitivity issues detection
    sensitivity_issues = _check_sensitivity_issues(response, context)
    evaluation_result['sensitivity_flags'] = sensitivity_issues
    
    # Decision logic
    if evaluation_result['cultural_score'] < 0.7:
        evaluation_result['needs_regeneration'] = True
        
    if sensitivity_issues:
        evaluation_result['requires_approval'] = True
    
    return evaluation_result
```

#### 2. Sensitivity Detection (`src/main.py`)
```python
def _check_sensitivity_issues(response: str, context: dict) -> list:
    """Check for potentially sensitive content that requires approval"""
    
    sensitivity_flags = []
    
    # PII patterns
    pii_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
    ]
    
    # Cultural sensitivity
    sensitive_cultural_terms = [
        'tribal', 'indigenous', 'native', 'ethnic', 'racial',
        'religious', 'spiritual', 'cultural', 'traditional'
    ]
    
    # Financial patterns
    financial_patterns = [
        r'\$\d+',  # Dollar amounts
        r'\b\d{9,}\b',  # Large numbers
    ]
    
    return sensitivity_flags
```

#### 3. Approval Workflow Endpoints

##### Get Pending Approvals
```http
GET /approval/pending/{project_id}
```

##### Get Approval Details
```http
GET /approval/{approval_id}
```

##### Approve Content
```http
POST /approval/{approval_id}/approve
{
    "user_id": "current_user",
    "notes": "Approved for use"
}
```

##### Deny Content
```http
POST /approval/{approval_id}/deny
{
    "user_id": "current_user",
    "reason": "Contains sensitive information",
    "feedback": "Please redact PII before resubmitting"
}
```

##### Get Approval Statistics
```http
GET /approval/stats/{project_id}
```

### Frontend Components

#### 1. ApprovalComponent (`frontend/src/ApprovalComponent.js`)
- **Dashboard View**: Shows pending approvals with statistics
- **Detail Modal**: Full content review with evaluation results
- **Action Buttons**: Approve/deny with feedback
- **Responsive Design**: Mobile-friendly interface

#### 2. Integration with Main App
- **New Navigation Step**: Added "Approvals" step to workflow
- **Project Context**: Approval workflow tied to specific projects
- **Real-time Updates**: Automatic refresh after approval actions

## Usage Flow

### 1. Content Generation
1. User sends message to AI
2. AI generates response
3. System evaluates response for cultural competency
4. System checks for sensitivity issues

### 2. Evaluation Decision Tree
```
Response Generated
    ↓
Cultural Score < 0.7?
    ↓ Yes → Regenerate with improvements
    ↓ No
Sensitivity Issues Detected?
    ↓ Yes → Flag for approval
    ↓ No → Return response
```

### 3. Approval Process
1. **Content Flagged**: System creates approval request
2. **User Notification**: Frontend shows pending approval
3. **Review Process**: User reviews content and evaluation
4. **Decision**: Approve or deny with feedback
5. **Access Grant**: If approved, grant secure storage access

## Configuration

### Cultural Competency Thresholds
```python
# In src/main.py
if evaluation_result['cultural_score'] < 0.7:  # Configurable threshold
    evaluation_result['needs_regeneration'] = True
```

### Sensitivity Detection Patterns
```python
# PII patterns can be customized
pii_patterns = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
]

# Cultural sensitivity terms
sensitive_cultural_terms = [
    'tribal', 'indigenous', 'native', 'ethnic', 'racial',
    'religious', 'spiritual', 'cultural', 'traditional'
]
```

## Security Features

### 1. Secure Storage Integration
- **Row Level Security**: Database-level access control
- **Temporary Access**: Time-limited permissions
- **Audit Logging**: Complete access trail

### 2. Data Protection
- **PII Redaction**: Automatic detection and redaction
- **Sensitive Data Isolation**: Separate storage for sensitive content
- **Approval Tracking**: Complete audit trail of decisions

### 3. Access Control
- **Project-based Isolation**: Approvals tied to specific projects
- **User Authentication**: Approval actions require user identification
- **Permission-based Access**: Granular access control

## Monitoring and Analytics

### 1. Performance Metrics
- **Evaluation Time**: Time taken for cultural competency assessment
- **Approval Rate**: Percentage of content requiring approval
- **Response Time**: Time from generation to approval decision

### 2. Quality Metrics
- **Cultural Score Distribution**: Spread of cultural competency scores
- **Sensitivity Flag Types**: Most common sensitivity issues
- **Approval Decision Patterns**: User decision trends

### 3. System Health
- **Error Rates**: Failed evaluations or approvals
- **Response Times**: API endpoint performance
- **Storage Usage**: Approval data storage metrics

## Testing

### 1. Automated Tests
```bash
# Run approval workflow tests
python test_approval_workflow.py
```

### 2. Manual Testing
1. **Generate Sensitive Content**: Create content with PII or cultural references
2. **Check Approval Flow**: Verify content is flagged for approval
3. **Test Approval Actions**: Approve/deny content and verify access grants
4. **Monitor Statistics**: Check approval statistics and metrics

### 3. Test Scenarios
- **Low Cultural Score**: Content with poor cultural competency
- **PII Detection**: Content with email addresses or phone numbers
- **Cultural Sensitivity**: Content with multiple cultural references
- **Financial Data**: Content with dollar amounts or large numbers

## Troubleshooting

### Common Issues

#### 1. Approvals Not Showing
- Check project ID in approval requests
- Verify file permissions for approval storage
- Check API endpoint connectivity

#### 2. Evaluation Errors
- Verify evaluation utilities are properly imported
- Check cultural competency evaluator configuration
- Review sensitivity detection patterns

#### 3. Access Grant Failures
- Verify secure storage table exists
- Check database permissions
- Review approval workflow logs

### Debug Commands
```bash
# Check approval storage
ls -la src/secure_data/approvals/

# Check access logs
ls -la src/secure_data/access_logs/

# Test API endpoints
curl -X GET "http://localhost:8080/approval/pending/test-project"
```

## Future Enhancements

### 1. Advanced Features
- **Machine Learning**: Improve sensitivity detection with ML models
- **Community Feedback**: Integrate community expert reviews
- **Automated Redaction**: Smart PII removal and replacement

### 2. Integration Improvements
- **Database Integration**: Move from file-based to database storage
- **Real-time Notifications**: WebSocket-based approval notifications
- **Bulk Operations**: Approve/deny multiple items at once

### 3. Analytics Dashboard
- **Real-time Metrics**: Live approval statistics
- **Trend Analysis**: Historical approval patterns
- **Performance Monitoring**: System health indicators

## API Reference

### Evaluation Endpoints
- `POST /evaluate/cultural` - Evaluate cultural competency
- `POST /evaluate/cognitive` - Evaluate cognitive friendliness
- `POST /evaluate/comprehensive` - Comprehensive evaluation

### Approval Endpoints
- `GET /approval/pending/{project_id}` - Get pending approvals
- `GET /approval/{approval_id}` - Get approval details
- `POST /approval/{approval_id}/approve` - Approve content
- `POST /approval/{approval_id}/deny` - Deny content
- `GET /approval/stats/{project_id}` - Get approval statistics

### Performance Endpoints
- `POST /performance/record` - Record performance metrics
- `GET /performance/summary` - Get performance summary

## Conclusion

The Approval Workflow System provides a robust framework for ensuring culturally sensitive and secure content generation. By integrating evaluation feedback loops with human approval mechanisms, the system maintains high standards while providing efficient workflows for content review and approval.

The system is designed to be:
- **Scalable**: Handles multiple projects and users
- **Secure**: Protects sensitive data with proper access controls
- **Transparent**: Provides complete audit trails and metrics
- **User-friendly**: Intuitive interface for approval workflows
- **Configurable**: Adaptable to different cultural contexts and requirements 