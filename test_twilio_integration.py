"""
Test Twilio Integration
"""
import requests
import uuid
import time

def test_twilio_integration():
    """Test Twilio SMS integration"""
    print("🧪 Testing Twilio Integration")
    print("=" * 30)
    
    # Test Twilio configuration
    try:
        from app.config import settings
        print(f"Twilio Account SID: {bool(settings.twilio_account_sid)}")
        print(f"Twilio Auth Token: {bool(settings.twilio_auth_token)}")
        print(f"Twilio SMS Number: {settings.twilio_sms_number or 'Not set'}")
        
        if settings.twilio_account_sid and settings.twilio_auth_token:
            print("✅ Twilio configured!")
            
            # Test Twilio client
            from twilio.rest import Client
            client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            
            # Test account info
            account = client.api.accounts(settings.twilio_account_sid).fetch()
            print(f"Twilio account status: {account.status}")
            
            # Send test SMS (to yourself)
            test_number = "+917019567529"  # Your number
            test_message = "🧪 Twilio test - Healthcare Chatbot is working!"
            
            print(f"\n📤 Sending test SMS to {test_number}")
            
            message = client.messages.create(
                from_=settings.twilio_sms_number,
                to=test_number,
                body=test_message
            )
            
            print(f"✅ SMS sent! SID: {message.sid}")
            print(f"Status: {message.status}")
            
        else:
            print("⚠️  Twilio not configured - showing mock behavior")
            
            # Mock test
            test_number = "+917019567529"
            test_message = "🧪 Mock Twilio test - Healthcare Chatbot is working!"
            
            print(f"\n📤 Sending mock SMS to {test_number}")
            print(f"✅ Mock SMS sent successfully!")
            print(f"SID: mock_twilio_sid_123")
            print(f"Status: queued")
            
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
        
        if "twilio" in str(e).lower():
            print("💡 Install Twilio: pip install twilio")
        else:
            print("💡 Check your Twilio credentials in .env")

if __name__ == "__main__":
    test_twilio_integration()