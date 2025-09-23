"""
Test SMS Integration with Twilio
"""
import requests
import uuid
import time

def test_sms_integration():
    """Test SMS integration with Twilio"""
    print("🧪 Testing SMS Integration with Twilio")
    print("=" * 35)
    
    # Test SMS sending
    test_number = "+917019567529"  # Your number
    test_message = "🧪 SMS Integration Test - Healthcare Chatbot is working!"
    
    print(f"Sending SMS to {test_number}")
    print(f"Message: {test_message}")
    
    # Test via your service
    try:
        from app.services.twilio_sms import twilio_sms_service
        
        if twilio_sms_service.is_configured:
            print("✅ Twilio SMS service configured")
            
            result = twilio_sms_service.send_sms_message(test_number, test_message)
            print(f"SMS Result: {result}")
            
            if result.get('success'):
                print("🎉 SMS sent successfully!")
                print(f"SID: {result['data']['sid']}")
                print(f"Status: {result['data']['status']}")
            else:
                print("❌ SMS failed to send")
                print(f"Error: {result.get('error')}")
        else:
            print("⚠️  Twilio SMS not configured")
            print("Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to .env")
            
    except Exception as e:
        print(f"❌ Error testing SMS: {e}")

def test_emergency_sms():
    """Test emergency SMS"""
    print("\n🚨 Testing Emergency SMS")
    print("=" * 25)
    
    test_number = "+917019567529"
    emergency_type = "Severe Chest Pain"
    location = "Delhi"
    
    print(f"Sending emergency SMS for {emergency_type} in {location}")
    
    try:
        from app.services.twilio_sms import twilio_sms_service
        
        if twilio_sms_service.is_configured:
            result = twilio_sms_service.send_emergency_sms(test_number, emergency_type, location)
            print(f"Emergency SMS Result: {result}")
            
            if result.get('success'):
                print("🎉 Emergency SMS sent successfully!")
            else:
                print("❌ Emergency SMS failed")
        else:
            print("⚠️  Twilio SMS not configured")
            
    except Exception as e:
        print(f"❌ Error testing emergency SMS: {e}")

def test_health_advisory_sms():
    """Test health advisory SMS"""
    print("\n💡 Testing Health Advisory SMS")
    print("=" * 30)
    
    test_number = "+917019567529"
    topic = "Seasonal Flu Prevention"
    recommendations = [
        "Get seasonal flu vaccination",
        "Wash hands frequently with soap",
        "Avoid touching face with unwashed hands",
        "Cover mouth and nose when coughing/sneezing",
        "Stay home when sick",
        "Maintain good nutrition and sleep"
    ]
    
    print(f"Sending health advisory SMS on {topic}")
    
    try:
        from app.services.twilio_sms import twilio_sms_service
        
        if twilio_sms_service.is_configured:
            result = twilio_sms_service.send_health_advisory_sms(test_number, topic, recommendations)
            print(f"Health Advisory SMS Result: {result}")
            
            if result.get('success'):
                print("🎉 Health advisory SMS sent successfully!")
            else:
                print("❌ Health advisory SMS failed")
        else:
            print("⚠️  Twilio SMS not configured")
            
    except Exception as e:
        print(f"❌ Error testing health advisory SMS: {e}")

if __name__ == "__main__":
    test_sms_integration()
    test_emergency_sms()
    test_health_advisory_sms()
    
    print("\n🎉 SMS Integration Testing Completed!")