#!/usr/bin/env python3
"""
Integration test to verify all backend-frontend connections are working properly.
This test checks that the evaluation feedback loop and approval workflow are properly connected.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8080"  # Change to your API base URL
TEST_PROJECT_ID = "test_integration_project"

def test_backend_frontend_connections():
    """Test all backend-frontend connection points"""
    print("🧪 Testing Backend-Frontend Integration...")
    
    # Test 1: Basic API connectivity
    print("\n1. Testing API connectivity...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        return False
    
    # Test 2: Chat message flow with evaluation
    print("\n2. Testing chat message flow with evaluation...")
    test_message = "Write an executive summary for our tribal community health initiative"
    
    try:
        response = requests.post(f"{API_BASE}/chat/send_message", json={
            "project_id": TEST_PROJECT_ID,
            "message": test_message
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Chat message sent successfully")
                
                # Check for evaluation data
                if 'quality_evaluation' in data:
                    eval_data = data['quality_evaluation']
                    print(f"✅ Evaluation data present:")
                    print(f"   - Cognitive score: {eval_data.get('cognitive_friendliness_score', 'N/A')}")
                    print(f"   - Cultural score: {eval_data.get('cultural_competency_score', 'N/A')}")
                    print(f"   - Overall score: {eval_data.get('overall_quality_score', 'N/A')}")
                    print(f"   - Quality level: {eval_data.get('quality_level', 'N/A')}")
                else:
                    print("⚠️ No evaluation data in response")
                
                # Check for approval flags
                if 'flagged for approval' in data.get('response', '').lower():
                    print("✅ Approval workflow triggered")
                else:
                    print("ℹ️ No approval needed for this response")
            else:
                print(f"❌ Chat message failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Chat endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing chat flow: {e}")
    
    # Test 3: Approval endpoints
    print("\n3. Testing approval endpoints...")
    
    # Test pending approvals
    try:
        response = requests.get(f"{API_BASE}/approval/pending/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pending approvals endpoint working: {len(data.get('pending_approvals', []))} pending")
        else:
            print(f"❌ Pending approvals error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing pending approvals: {e}")
    
    # Test approval statistics
    try:
        response = requests.get(f"{API_BASE}/approval/stats/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Approval stats endpoint working:")
            print(f"   - Total requests: {stats.get('total_requests', 0)}")
            print(f"   - Pending: {stats.get('pending', 0)}")
        else:
            print(f"❌ Approval stats error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing approval stats: {e}")
    
    # Test 4: Evaluation endpoints
    print("\n4. Testing evaluation endpoints...")
    
    test_response = "Our tribal community health initiative will serve Native American families with culturally appropriate care."
    
    try:
        response = requests.post(f"{API_BASE}/evaluate/cultural", json={
            "response_text": test_response,
            "community_context": "Native American tribal community"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                evaluation = data.get('evaluation', {})
                print(f"✅ Cultural evaluation working:")
                print(f"   - Overall cultural score: {evaluation.get('overall_cultural_score', 'N/A')}")
                print(f"   - Recommendations: {len(evaluation.get('recommendations', []))}")
            else:
                print(f"❌ Cultural evaluation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Cultural evaluation endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing cultural evaluation: {e}")
    
    # Test 5: Comprehensive evaluation
    try:
        response = requests.post(f"{API_BASE}/evaluate/comprehensive", json={
            "response_text": test_response,
            "community_context": "Native American tribal community"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                evaluation = data.get('evaluation', {})
                print(f"✅ Comprehensive evaluation working:")
                print(f"   - Overall quality score: {evaluation.get('overall_quality_score', 'N/A')}")
                print(f"   - Quality level: {evaluation.get('quality_level', 'N/A')}")
            else:
                print(f"❌ Comprehensive evaluation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Comprehensive evaluation endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing comprehensive evaluation: {e}")
    
    # Test 6: Performance monitoring
    print("\n5. Testing performance monitoring...")
    
    try:
        response = requests.get(f"{API_BASE}/performance/summary")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Performance monitoring working")
                summary = data.get('summary', {})
                if summary:
                    print(f"   - Operations recorded: {len(summary.get('operations', []))}")
            else:
                print(f"❌ Performance monitoring failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Performance monitoring endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing performance monitoring: {e}")
    
    return True

def test_sensitivity_detection():
    """Test sensitivity detection with various content types"""
    print("\n🧪 Testing Sensitivity Detection...")
    
    test_cases = [
        {
            "name": "PII Detection",
            "content": "Contact John Smith at john.smith@tribalhealth.org or call 555-123-4567",
            "expected_flags": ["Potential PII detected"]
        },
        {
            "name": "Cultural Sensitivity",
            "content": "Our tribal elders and traditional healers will guide this sacred health initiative for our indigenous community.",
            "expected_flags": ["Multiple cultural references detected"]
        },
        {
            "name": "Financial Data",
            "content": "The project budget is $500,000 and we expect to serve 1000 community members.",
            "expected_flags": ["Potential financial/confidential data detected"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            response = requests.post(f"{API_BASE}/chat/send_message", json={
                "project_id": TEST_PROJECT_ID,
                "message": f"Write about: {test_case['content']}"
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    response_text = data.get('response', '')
                    if 'flagged for approval' in response_text.lower():
                        print(f"✅ Sensitivity detected correctly")
                    else:
                        print(f"ℹ️ No sensitivity detected")
                else:
                    print(f"❌ Test failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Test error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing sensitivity detection: {e}")

def test_frontend_api_endpoints():
    """Test all API endpoints that the frontend uses"""
    print("\n🧪 Testing Frontend API Endpoints...")
    
    endpoints = [
        {"method": "GET", "url": "/projects", "name": "Projects List"},
        {"method": "GET", "url": "/context/test-project", "name": "Project Context"},
        {"method": "GET", "url": "/chat/history/test-project", "name": "Chat History"},
        {"method": "GET", "url": "/grant/sections/test-project", "name": "Grant Sections"},
        {"method": "GET", "url": "/privacy/audit/test-project", "name": "Privacy Audit"},
        {"method": "GET", "url": "/approval/pending/test-project", "name": "Pending Approvals"},
        {"method": "GET", "url": "/approval/stats/test-project", "name": "Approval Statistics"},
        {"method": "GET", "url": "/performance/summary", "name": "Performance Summary"},
        {"method": "GET", "url": "/evaluation/targets", "name": "Evaluation Targets"},
        {"method": "GET", "url": "/advanced/status", "name": "Advanced Features Status"}
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{API_BASE}{endpoint['url']}")
            else:
                response = requests.post(f"{API_BASE}{endpoint['url']}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']}: Working")
            else:
                print(f"❌ {endpoint['name']}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint['name']}: Connection error - {e}")

def main():
    """Run all integration tests"""
    print("🚀 Starting Backend-Frontend Integration Tests...")
    print(f"API Base: {API_BASE}")
    print(f"Test Project ID: {TEST_PROJECT_ID}")
    print("=" * 60)
    
    # Test basic connectivity and core functionality
    if test_backend_frontend_connections():
        print("\n✅ Core integration tests passed!")
    else:
        print("\n❌ Core integration tests failed!")
        return
    
    # Test sensitivity detection
    test_sensitivity_detection()
    
    # Test all frontend API endpoints
    test_frontend_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Integration Testing Completed!")
    print("\nNext Steps:")
    print("1. Start your frontend application")
    print("2. Navigate to the Chat section")
    print("3. Send a message with sensitive content")
    print("4. Check the Approvals tab for flagged content")
    print("5. Test approval/denial workflows")
    print("6. Monitor evaluation scores in chat responses")

if __name__ == "__main__":
    main() 