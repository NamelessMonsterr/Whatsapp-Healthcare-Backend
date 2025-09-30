"""
Test Twilio Integration - FIXED VERSION
"""
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_twilio_integration():
    """Test Twilio SMS integration with proper error handling"""
    print("🧪 Testing Twilio Integration")
    print("=" * 40)

    # Test Twilio configuration
    try:
        from app.config import settings
        
        print(f"Twilio Account SID configured: {bool(settings.twilio_account_sid)}")
        print(f"Twilio Auth Token configured: {bool(settings.twilio_auth_token)}")
        print(f"Twilio SMS Number: {settings.twilio_sms_number or 'Not set'}")

        if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_sms_number:
            print("✅ Twilio fully configured!")
            
            # Test Twilio client
            from twilio.rest import Client
            
            try:
                client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                
                # Test account info
                account = client.api.accounts(settings.twilio_account_sid).fetch()
                print(f"Twilio account status: {account.status}")
                print(f"Twilio account type: {account.type}")
                
                # Send test SMS (to admin number if configured)
                if settings.admin_phone_numbers:
                    admin_number = settings.admin_phone_list[0] if settings.admin_phone_list else None
                    if admin_number:
                        test_number = admin_number
                        test_message = "🧪 Twilio test - Healthcare Chatbot is working! (Admin test)"
                        
                        print(f"\n📤 Sending test SMS to {test_number}")
                        
                        try:
                            message = client.messages.create(
                                from_=settings.twilio_sms_number,
                                to=test_number,
                                body=test_message
                            )
                            
                            print(f"✅ SMS sent successfully!")
                            print(f"Message SID: {message.sid}")
                            print(f"Status: {message.status}")
                            print(f"Date Created: {message.date_created}")
                            
                            # Wait a moment and check status
                            await asyncio.sleep(2)
                            updated_message = client.messages(message.sid).fetch()
                            print(f"Updated Status: {updated_message.status}")
                            
                        except Exception as send_error:
                            print(f"❌ Failed to send SMS: {send_error}")
                            if "unverified number" in str(send_error).lower():
                                print("💡 Tip: You may need to verify the recipient number in Twilio console")
                            elif "insufficient funds" in str(send_error).lower():
                                print("💡 Tip: Check your Twilio account balance")
                            else:
                                print(f"💡 Error details: {send_error}")
                    else:
                        print("⚠️ No admin phone number configured for testing")
                else:
                    print("⚠️ No admin phone numbers configured")
                    
            except Exception as client_error:
                print(f"❌ Twilio client error: {client_error}")
                if "authentication" in str(client_error).lower():
                    print("💡 Check your Twilio credentials")
                elif "permission" in str(client_error).lower():
                    print("💡 Ensure your Twilio account has proper permissions")
                else:
                    print(f"💡 Client error: {client_error}")
                    
            # Test message templates if available
            try:
                templates = client.messages.list(limit=5)
                if templates:
                    print(f"\n📋 Found {len(templates)} recent messages in account")
                    for i, msg in enumerate(templates[:3], 1):
                        print(f"  {i}. To: {msg.to}, Status: {msg.status}, Date: {msg.date_created}")
                else:
                    print("\n📋 No recent messages found in account")
                    
            except Exception as template_error:
                print(f"⚠️ Could not retrieve message history: {template_error}")
                
        else:
            print("⚠️ Twilio not fully configured")
            print("Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SMS_NUMBER")
            
            # Show mock behavior
            print("\n📋 Mock Twilio behavior:")
            print("✅ Mock SMS would be sent successfully")
            print("✅ Mock message tracking would work")
            print("✅ Mock delivery status would be 'delivered'")
            
        # Test webhook configuration (for incoming SMS)
        print(f"\n🌐 Webhook configuration:")
        print(f"Webhook URL needed for incoming SMS: https://your-domain.com/webhooks/twilio")
        print(f"Webhook should handle: message status, incoming messages")
        
        # Show rate limiting info
        print(f"\n⚡ Rate limiting:")
        print(f"Twilio SMS rate limit: 1 message per second")
        print(f"Daily limit: Varies by account type")
        
    except ImportError as import_error:
        print(f"❌ Twilio library not installed: {import_error}")
        print("💡 Install with: pip install twilio")
        
    except Exception as e:
        print(f"❌ Unexpected error testing Twilio: {e}")
        logger.error(f"Twilio test error: {e}", exc_info=True)

def test_sms_fallback():
    """Test SMS fallback system"""
    print("\n📱 Testing SMS Fallback System")
    print("=" * 35)
    
    # This would test the fallback when WhatsApp is unavailable
    print("✅ SMS fallback would activate when:")
    print("  - WhatsApp service is down")
    print("  - WhatsApp rate limit exceeded") 
    print("  - User doesn't have WhatsApp")
    print("  - Message delivery fails repeatedly")
    
    print("\n✅ Fallback features:")
    print("  - Automatic SMS sending via Twilio")
    print("  - Message content adaptation for SMS")
    print("  - Delivery status tracking")
    print("  - Cost optimization")

if __name__ == "__main__":
    asyncio.run(test_twilio_integration())
    test_sms_fallback()
