#!/usr/bin/env python3
"""
Test script for AI integration
Run this after setting up the .env file with your OpenAI API key
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_endpoint():
    """Test the AI chat endpoint"""
    base_url = "http://localhost:8000"
    
    # Test data
    test_cases = [
        {
            "prompt": "What are the payment trends for consumers?",
            "userType": "consumer"
        },
        {
            "prompt": "Which merchants are performing best?",
            "userType": "merchant"
        },
        {
            "prompt": "Show me insights about payment failures",
            "userType": "consumer"
        }
    ]
    
    print("Testing AI Chat Integration...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['userType'].upper()}")
        print(f"Prompt: {test_case['prompt']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/ai/chat",
                headers={"Content-Type": "application/json"},
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Response: {data['response'][:200]}...")
                print(f"User Type: {data['userType']}")
                print(f"Status: {data['status']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

def test_health_endpoint():
    """Test the health endpoint"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/ai/health")
        if response.status_code == 200:
            print("✅ AI Health endpoint is working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("AI Integration Test Script")
    print("Make sure the backend is running on http://localhost:8000")
    print("And that you have set OPENAI_API_KEY in your .env file")
    print()
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        exit(1)
    
    # Test health endpoint first
    test_health_endpoint()
    print()
    
    # Test AI chat endpoint
    test_ai_endpoint()
