#!/usr/bin/env python3
"""
Test script to verify the dynamic company information feature
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_company_info_flow():
    """Test the complete company information flow"""
    
    print("🧪 Testing Company Information Flow")
    print("=" * 50)
    
    # Step 1: Reset session
    print("\n1. Resetting session...")
    try:
        response = requests.post(f"{BASE_URL}/reset_session")
        if response.status_code == 200:
            print("✅ Session reset successfully")
        else:
            print(f"❌ Session reset failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error resetting session: {e}")
        return False
    
    # Step 2: Check initial company info (should be empty)
    print("\n2. Checking initial company info...")
    try:
        response = requests.get(f"{BASE_URL}/get_company_info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Initial company info: {data}")
            if not data.get('has_company_info'):
                print("✅ Company info is empty as expected")
            else:
                print("⚠️  Company info should be empty initially")
        else:
            print(f"❌ Failed to get company info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting company info: {e}")
    
    # Step 3: Update company information
    print("\n3. Updating company information...")
    company_data = {
        "companyName": "TechCorp AI Solutions",
        "jobPosition": "Senior AI Engineer", 
        "companyField": "Artificial Intelligence & Machine Learning",
        "companyProducts": "AI-powered educational platforms, chatbots, recommendation systems",
        "companyCulture": "Innovation-focused, collaborative, remote-friendly",
        "otherInfo": "Series B startup with 200+ employees, focus on EdTech"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/update_company_info",
            headers={"Content-Type": "application/json"},
            json=company_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Company info updated successfully")
            print(f"   Updated data: {data.get('company_info', {})}")
        else:
            print(f"❌ Failed to update company info: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating company info: {e}")
        return False
    
    # Step 4: Verify updated company info
    print("\n4. Verifying updated company info...")
    try:
        response = requests.get(f"{BASE_URL}/get_company_info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Updated company info: {data}")
            if data.get('has_company_info'):
                print("✅ Company info is now populated")
                stored_info = data.get('company_info', {})
                if stored_info.get('company_name') == company_data['companyName']:
                    print("✅ Company name matches")
                else:
                    print("❌ Company name doesn't match")
            else:
                print("❌ Company info should be populated now")
        else:
            print(f"❌ Failed to verify company info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying company info: {e}")
    
    # Step 5: Test a chat message to see if context is applied
    print("\n5. Testing chat with company context...")
    try:
        test_message = {"message": "Hello, I'm ready for the interview!"}
        response = requests.post(
            f"{BASE_URL}/send_message",
            headers={"Content-Type": "application/json"},
            json=test_message
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('reply', '')
            print("✅ Chat response received")
            print(f"   Response preview: {reply[:200]}...")
            
            # Check if company name appears in response
            if company_data['companyName'] in reply:
                print("✅ Company name found in response - context is working!")
            else:
                print("⚠️  Company name not found in response - context might not be applied")
        else:
            print(f"❌ Failed to send chat message: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_company_info_flow()
