#!/usr/bin/env python3
"""
WhatsApp API Debug & Fix Script
This script will help you diagnose and fix WhatsApp API permission issues.
"""

import requests
import json
from typing import Dict, Any

class WhatsAppDebugger:
    def __init__(self):
        # These values need to be filled from your Meta Developer Console
        self.ACCESS_TOKEN = ""  # Get from WhatsApp > API Setup
        self.PHONE_NUMBER_ID = ""  # Get from WhatsApp > API Setup  
        self.APP_ID = ""  # Your App ID
        self.APP_SECRET = ""  # Your App Secret
        self.API_VERSION = "v18.0"
        
    def step_1_get_credentials(self):
        """Instructions to get the required credentials"""
        print("🔧 STEP 1: Get Your Credentials")
        print("=" * 50)
        print("1. Go to https://developers.facebook.com/")
        print("2. Select your app")
        print("3. Go to WhatsApp > API Setup")
        print("4. Copy the following values:")
        print("   - Temporary access token")
        print("   - Phone number ID")
        print("   - Your App ID (from App Settings > Basic)")
        print("\n")
        
        # Get user input
        self.ACCESS_TOKEN = input("📝 Enter your ACCESS TOKEN: ").strip()
        self.PHONE_NUMBER_ID = input("📝 Enter your PHONE NUMBER ID: ").strip()
        self.APP_ID = input("📝 Enter your APP ID: ").strip()
        
        if not all([self.ACCESS_TOKEN, self.PHONE_NUMBER_ID, self.APP_ID]):
            print("❌ Missing credentials. Please provide all required values.")
            return False
        
        print("✅ Credentials collected!")
        return True
    
    def step_2_test_access_token(self) -> bool:
        """Test if the access token is valid"""
        print("\n🔍 STEP 2: Testing Access Token")
        print("=" * 50)
        
        try:
            url = f"https://graph.facebook.com/{self.API_VERSION}/me"
            params = {"access_token": self.ACCESS_TOKEN}
            
            response = requests.get(url, params=params)
            result = response.json()
            
            if response.status_code == 200:
                print(f"✅ Access token is valid!")
                print(f"   App Name: {result.get('name', 'N/A')}")
                print(f"   App ID: {result.get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Access token invalid!")
                print(f"   Error: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing token: {e}")
            return False
    
    def step_3_check_permissions(self) -> bool:
        """Check app permissions"""
        print("\n🔐 STEP 3: Checking Permissions")
        print("=" * 50)
        
        try:
            url = f"https://graph.facebook.com/{self.API_VERSION}/me/permissions"
            params = {"access_token": self.ACCESS_TOKEN}
            
            response = requests.get(url, params=params)
            result = response.json()
            
            if response.status_code == 200:
                permissions = result.get('data', [])
                granted_permissions = [p['permission'] for p in permissions if p['status'] == 'granted']
                
                print("✅ Current permissions:")
                for perm in granted_permissions:
                    print(f"   - {perm}")
                
                # Check for required WhatsApp permissions
                required_perms = ['whatsapp_business_messaging', 'whatsapp_business_management']
                missing_perms = [p for p in required_perms if p not in granted_permissions]
                
                if missing_perms:
                    print(f"\n⚠️  Missing required permissions: {missing_perms}")
                    print("   You need to add WhatsApp product to your app and request permissions.")
                    return False
                else:
                    print("✅ All required permissions granted!")
                    return True
                    
            else:
                print(f"❌ Error checking permissions: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking permissions: {e}")
            return False
    
    def step_4_test_phone_number(self) -> bool:
        """Test phone number configuration"""
        print("\n📱 STEP 4: Testing Phone Number")
        print("=" * 50)
        
        try:
            url = f"https://graph.facebook.com/{self.API_VERSION}/{self.PHONE_NUMBER_ID}"
            headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
            
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                print("✅ Phone number is properly configured!")
                print(f"   Display Name: {result.get('display_phone_number', 'N/A')}")
                print(f"   Verified: {result.get('verified_name', 'N/A')}")
                print(f"   Quality Rating: {result.get('quality_rating', 'N/A')}")
                return True
            else:
                print(f"❌ Phone number configuration error!")
                print(f"   Error: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing phone number: {e}")
            return False
    
    def step_5_send_test_message(self) -> bool:
        """Send a test message"""
        print("\n💬 STEP 5: Sending Test Message")
        print("=" * 50)
        
        test_number = input("📝 Enter test phone number (with country code, e.g., +1234567890): ").strip()
        if not test_number:
            print("⏭️  Skipping test message (no number provided)")
            return True
        
        try:
            url = f"https://graph.facebook.com/{self.API_VERSION}/{self.PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {self.ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": test_number,
                "type": "text",
                "text": {"body": "🎉 WhatsApp API test successful! Your integration is working."}
            }
            
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200:
                print("✅ Test message sent successfully!")
                print(f"   Message ID: {result.get('messages', [{}])[0].get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to send test message!")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending test message: {e}")
            return False
    
    def generate_config(self):
        """Generate configuration for your application"""
        print("\n⚙️  STEP 6: Configuration for Your App")
        print("=" * 50)
        
        config = f'''
# WhatsApp API Configuration
WHATSAPP_ACCESS_TOKEN = "{self.ACCESS_TOKEN}"
WHATSAPP_PHONE_NUMBER_ID = "{self.PHONE_NUMBER_ID}"
WHATSAPP_API_VERSION = "{self.API_VERSION}"
WHATSAPP_API_URL = "https://graph.facebook.com/{self.API_VERSION}"

# Example usage in your application:
import requests

def send_whatsapp_message(to_number: str, message: str):
    url = f"{{WHATSAPP_API_URL}}/{{WHATSAPP_PHONE_NUMBER_ID}}/messages"
    
    headers = {{
        "Authorization": f"Bearer {{WHATSAPP_ACCESS_TOKEN}}",
        "Content-Type": "application/json"
    }}
    
    data = {{
        "messaging_product": "whatsapp", 
        "to": to_number,
        "type": "text",
        "text": {{"body": message}}
    }}
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200, response.json()
        '''
        
        print(config)
        
        # Save to file
        with open('whatsapp_config.py', 'w') as f:
            f.write(config.strip())
        print("\n✅ Configuration saved to 'whatsapp_config.py'")
    
    def run_diagnosis(self):
        """Run the complete diagnosis"""
        print("🚀 WhatsApp API Diagnostic Tool")
        print("=" * 50)
        print("This tool will help you fix your WhatsApp API permission issues.\n")
        
        # Step 1: Get credentials
        if not self.step_1_get_credentials():
            return
        
        # Step 2: Test token
        if not self.step_2_test_access_token():
            print("\n🔧 FIX: Get a new access token from WhatsApp > API Setup")
            return
        
        # Step 3: Check permissions
        if not self.step_3_check_permissions():
            print("\n🔧 FIX: Add WhatsApp product to your app and complete business verification")
            return
        
        # Step 4: Test phone number
        if not self.step_4_test_phone_number():
            print("\n🔧 FIX: Verify your phone number in WhatsApp > API Setup")
            return
        
        # Step 5: Send test message
        self.step_5_send_test_message()
        
        # Step 6: Generate config
        self.generate_config()
        
        print("\n🎉 Diagnosis Complete!")
        print("If all steps passed, your WhatsApp API should be working now.")

if __name__ == "__main__":
    debugger = WhatsAppDebugger()
    debugger.run_diagnosis()