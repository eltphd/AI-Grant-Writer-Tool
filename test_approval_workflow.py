#!/usr/bin/env python3
"""
Test script for the approval workflow functionality.
This script tests the evaluation feedback loop and approval workflow.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8080"  # Change to your API base URL
TEST_PROJECT_ID = "test_project_approval"

def test_evaluation_feedback_loop():
    """Test the evaluation feedback loop functionality"""
    print("🧪 Testing Evaluation Feedback Loop...")
    
    # Test message that should trigger cultural competency evaluation
    test_message = "Write an executive summary for our tribal community health initiative"
    
    # Test context with community focus
    test_context = {
        "project_id": TEST_PROJECT_ID,
        "organization_info": "Tribal Health Organization",
        "community_focus": "Native American tribal community",
        "uploaded_files": ["health_initiative.pdf"],
        "initiative_description": "Community health program for tribal members"
    }
    
    # Test RFP analysis
    test_rfp_analysis = {
        "requirements": ["Cultural sensitivity", "Community engagement"],
        "eligibility_criteria": ["Tribal organization", "Health focus"],
        "funding_amount": "$500,000"
    }
    
    try:
        # Send message to trigger evaluation
        response = requests.post(f"{API_BASE}/chat/send_message", json={
            "project_id": TEST_PROJECT_ID,
            "message": test_message,
            "context": test_context,
            "rfp_analysis": test_rfp_analysis
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Message sent successfully")
            print(f"Response: {data.get('response', 'No response')[:200]}...")
            
            # Check if response contains approval flag
            if "flagged for approval" in data.get('response', '').lower():
                print("✅ Approval workflow triggered correctly")
            else:
                print("ℹ️ No approval needed for this response")
                
        else:
            print(f"❌ Error sending message: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing evaluation feedback loop: {e}")

def test_approval_endpoints():
    """Test the approval workflow endpoints"""
    print("\n🧪 Testing Approval Endpoints...")
    
    # Test getting pending approvals
    try:
        response = requests.get(f"{API_BASE}/approval/pending/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pending approvals retrieved: {len(data.get('pending_approvals', []))}")
        else:
            print(f"❌ Error getting pending approvals: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing pending approvals: {e}")
    
    # Test getting approval statistics
    try:
        response = requests.get(f"{API_BASE}/approval/stats/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Approval stats retrieved:")
            print(f"   Total requests: {stats.get('total_requests', 0)}")
            print(f"   Pending: {stats.get('pending', 0)}")
            print(f"   Approved: {stats.get('approved', 0)}")
            print(f"   Denied: {stats.get('denied', 0)}")
        else:
            print(f"❌ Error getting approval stats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing approval stats: {e}")

def test_cultural_evaluation():
    """Test the cultural evaluation functionality"""
    print("\n🧪 Testing Cultural Evaluation...")
    
    test_response = "Our tribal community health initiative will serve Native American families with culturally appropriate care."
    
    try:
        response = requests.post(f"{API_BASE}/evaluate/cultural", json={
            "response_text": test_response,
            "community_context": "Native American tribal community"
        })
        
        if response.status_code == 200:
            data = response.json()
            evaluation = data.get('evaluation', {})
            print(f"✅ Cultural evaluation completed:")
            print(f"   Cultural score: {evaluation.get('overall_score', 'N/A')}")
            print(f"   Recommendations: {len(evaluation.get('recommendations', []))}")
        else:
            print(f"❌ Error evaluating cultural competency: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing cultural evaluation: {e}")

def test_sensitivity_detection():
    """Test sensitivity detection functionality"""
    print("\n🧪 Testing Sensitivity Detection...")
    
    # Test response with potential PII
    test_response_with_pii = "Contact John Smith at john.smith@tribalhealth.org or call 555-123-4567 for more information."
    
    # Test response with cultural references
    test_response_cultural = "Our tribal elders and traditional healers will guide this sacred health initiative for our indigenous community."
    
    try:
        # Test PII detection
        response = requests.post(f"{API_BASE}/evaluate/cultural", json={
            "response_text": test_response_with_pii,
            "community_context": "Tribal community"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PII detection test completed")
            print(f"   Response: {data.get('evaluation', {}).get('overall_score', 'N/A')}")
        else:
            print(f"❌ Error testing PII detection: {response.status_code}")
            
        # Test cultural sensitivity detection
        response = requests.post(f"{API_BASE}/evaluate/cultural", json={
            "response_text": test_response_cultural,
            "community_context": "Native American tribal community"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cultural sensitivity test completed")
            print(f"   Response: {data.get('evaluation', {}).get('overall_score', 'N/A')}")
        else:
            print(f"❌ Error testing cultural sensitivity: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing sensitivity detection: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Approval Workflow Tests...")
    print(f"API Base: {API_BASE}")
    print(f"Test Project ID: {TEST_PROJECT_ID}")
    print("=" * 50)
    
    # Test evaluation feedback loop
    test_evaluation_feedback_loop()
    
    # Test approval endpoints
    test_approval_endpoints()
    
    # Test cultural evaluation
    test_cultural_evaluation()
    
    # Test sensitivity detection
    test_sensitivity_detection()
    
    print("\n" + "=" * 50)
    print("✅ Approval Workflow Tests Completed!")
    print("\nNext Steps:")
    print("1. Check the frontend approval interface")
    print("2. Test approval/denial workflows")
    print("3. Verify secure storage access grants")
    print("4. Monitor evaluation performance metrics")

if __name__ == "__main__":
    main() 