"""
Twilio SMS Service - Healthcare Alerts via SMS
"""
import logging
from typing import Dict, Any, List, Optional
import json
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import asyncio
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class TwilioSMSService:
    """Twilio SMS service for healthcare alerts"""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.sms_number = settings.twilio_sms_number
        self.verify_token = settings.twilio_verify_token
        
        # Initialize Twilio client
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.is_configured = True
            logger.info(f"✅ Twilio SMS Service initialized - Number: {self.sms_number}")
        else:
            self.client = None
            self.is_configured = False
            logger.warning("⚠️  Twilio SMS not configured - Missing account SID or auth token")
    
    def send_sms_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send SMS message via Twilio
        
        Args:
            to: Recipient phone number (+91XXXXXXXXXX format)
            text: Message text to send
            
        Returns:
            Dict with sending results
        """
        try:
            if not self.is_configured:
                logger.warning("Twilio SMS not configured - returning mock success")
                return {
                    "success": True,
                    "message": "Twilio SMS not configured - mock success",
                    "data": {"sid": "mock_sms_sid_123"}
                }
            
            # Format recipient number (ensure +91 prefix for India)
            if not to.startswith("+"):
                if to.startswith("91"):
                    to = f"+{to}"
                else:
                    to = f"+91{to}"
            
            logger.info(f"📤 Sending Twilio SMS to {to}")
            logger.info(f"Message: {text[:100]}...")
            
            # Send SMS
            message = self.client.messages.create(
                from_=self.sms_number,
                to=to,
                body=text
            )
            
            logger.info(f"✅ Twilio SMS sent successfully - SID: {message.sid}")
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "data": {
                    "sid": message.sid,
                    "status": message.status,
                    "timestamp": message.date_created.isoformat() if message.date_created else datetime.utcnow().isoformat(),
                    "from": self.sms_number,
                    "to": to,
                    "body": text[:50] + "..." if len(text) > 50 else text
                }
            }
            
        except TwilioException as e:
            logger.error(f"❌ Twilio SMS API error: {e}")
            return {
                "success": False,
                "error": f"Twilio SMS API error: {e}",
                "message": "I'm having trouble sending your SMS. Please try again later."
            }
        except Exception as e:
            logger.error(f"❌ Error sending Twilio SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending your SMS. Please try again later."
            }
    
    def send_bulk_sms_messages(self, recipients: List[str], text: str) -> Dict[str, Any]:
        """
        Send bulk SMS messages to multiple recipients
        
        Args:
            recipients: List of recipient phone numbers
            text: Message text to send
            
        Returns:
            Dict with bulk sending results
        """
        try:
            if not self.is_configured:
                logger.warning("Twilio SMS not configured - returning mock success for bulk SMS")
                return {
                    "success": True,
                    "message": "Twilio SMS not configured - mock bulk success",
                    "data": {
                        "total": len(recipients),
                        "sent": len(recipients),
                        "failed": 0,
                        "sids": [f"mock_bulk_sid_{i}" for i in range(len(recipients))]
                    }
                }
            
            logger.info(f"📤 Sending bulk SMS to {len(recipients)} recipients")
            logger.info(f"Message: {text[:100]}...")
            
            successful_sends = 0
            failed_sends = 0
            message_sids = []
            errors = []
            
            # Send to each recipient with rate limiting
            for i, recipient in enumerate(recipients):
                try:
                    # Add small delay to avoid rate limiting
                    if i > 0:
                        asyncio.sleep(0.1)
                    
                    result = self.send_sms_message(recipient, text)
                    
                    if result.get('success'):
                        successful_sends += 1
                        message_sids.append(result['data']['sid'])
                        logger.info(f"✅ SMS {i+1}/{len(recipients)} sent to {recipient}")
                    else:
                        failed_sends += 1
                        errors.append(f"Recipient {recipient}: {result.get('error', 'Unknown error')}")
                        logger.error(f"❌ SMS {i+1}/{len(recipients)} failed to {recipient}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    failed_sends += 1
                    errors.append(f"Recipient {recipient}: {str(e)}")
                    logger.error(f"❌ Bulk SMS error for {recipient}: {e}", exc_info=True)
            
            logger.info(f"✅ Bulk SMS completed - Sent: {successful_sends}, Failed: {failed_sends}")
            
            return {
                "success": successful_sends > 0,
                "message": f"Bulk SMS completed - {successful_sends}/{len(recipients)} sent successfully",
                "data": {
                    "total": len(recipients),
                    "sent": successful_sends,
                    "failed": failed_sends,
                    "sids": message_sids,
                    "errors": errors if errors else None
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending bulk SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending bulk SMS. Please try again later."
            }
    
    def send_emergency_sms(self, to: str, emergency_type: str, location: str = None) -> Dict[str, Any]:
        """
        Send emergency SMS with specific formatting
        
        Args:
            to: Recipient phone number
            emergency_type: Type of emergency
            location: Location information
            
        Returns:
            Dict with sending results
        """
        try:
            if not self.is_configured:
                logger.warning("Twilio SMS not configured - returning mock success for emergency SMS")
                return {
                    "success": True,
                    "message": "Twilio SMS not configured - mock emergency success",
                    "data": {"sid": "mock_emergency_sid_123"}
                }
            
            # Create emergency message
            location_text = f" in {location}" if location else ""
            
            emergency_message = (
                f"🚨 EMERGENCY ALERT - {emergency_type.upper()}{location_text}\n\n"
                f"⚠️  IMMEDIATE ACTION REQUIRED:\n"
                f"• CALL EMERGENCY SERVICES (108) IMMEDIATELY\n"
                f"• DO NOT DRIVE YOURSELF TO HOSPITAL\n"
                f"• STAY CALM and sit comfortably\n"
                f"• LOOSEN TIGHT CLOTHING\n"
                f"• INFORM FAMILY MEMBERS\n"
                f"• NOTE WHEN SYMPTOMS STARTED\n\n"
                f"⏱️ TIME IS CRITICAL - Act immediately!\n\n"
                f"💡 This is AI-generated advice. Always consult a qualified healthcare professional for medical decisions!"
            )
            
            logger.info(f"🚨 Sending emergency SMS for {emergency_type} to {to}")
            
            # Send emergency SMS
            result = self.send_sms_message(to, emergency_message)
            
            if result.get('success'):
                logger.info(f"✅ Emergency SMS sent successfully to {to}")
            else:
                logger.error(f"❌ Failed to send emergency SMS to {to}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error sending emergency SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending emergency SMS. Please try again later."
            }
    
    def send_health_advisory_sms(self, to: str, topic: str, recommendations: List[str]) -> Dict[str, Any]:
        """
        Send health advisory SMS
        
        Args:
            to: Recipient phone number
            topic: Advisory topic
            recommendations: List of recommendations
            
        Returns:
            Dict with sending results
        """
        try:
            if not self.is_configured:
                logger.warning("Twilio SMS not configured - returning mock success for health advisory")
                return {
                    "success": True,
                    "message": "Twilio SMS not configured - mock health advisory success",
                    "data": {"sid": "mock_advisory_sid_123"}
                }
            
            # Create health advisory message
            recommendation_list = "\n".join([f"• {rec}" for rec in recommendations[:10]])
            
            advisory_message = (
                f"💡 HEALTH ADVISORY - {topic}\n\n"
                f"📋 RECOMMENDATIONS:\n"
                f"{recommendation_list}\n\n"
                f"📞 Consult healthcare provider for persistent symptoms!\n"
                f"🏥 Routine Care: Contact your doctor\n"
                f"💊 Pharmacy: For minor ailments\n\n"
                f"💡 This is general guidance - individual needs vary!"
            )
            
            logger.info(f"💡 Sending health advisory SMS on {topic} to {to}")
            
            # Send health advisory SMS
            result = self.send_sms_message(to, advisory_message)
            
            if result.get('success'):
                logger.info(f"✅ Health advisory SMS sent successfully to {to}")
            else:
                logger.error(f"❌ Failed to send health advisory SMS to {to}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error sending health advisory SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending health advisory SMS. Please try again later."
            }
    
    def send_medication_reminder_sms(self, to: str, medication: str, dosage: str, 
                                   frequency: str, next_dose_time: str = None) -> Dict[str, Any]:
        """
        Send medication reminder SMS
        
        Args:
            to: Recipient phone number
            medication: Medicine name
            dosage: Dosage amount
            frequency: How often to take
            next_dose_time: When next dose is due
            
        Returns:
            Dict with sending results
        """
        try:
            if not self.is_configured:
                logger.warning("Twilio SMS not configured - returning mock success for medication reminder")
                return {
                    "success": True,
                    "message": "Twilio SMS not configured - mock medication reminder success",
                    "data": {"sid": "mock_reminder_sid_123"}
                }
            
            # Create medication reminder message
            time_text = f"\n⏰ Next dose: {next_dose_time}" if next_dose_time else ""
            
            reminder_message = (
                f"💊 MEDICATION REMINDER\n\n"
                f"Medicine: {medication}\n"
                f"Dosage: {dosage}\n"
                f"Frequency: {frequency}"
                f"{time_text}\n\n"
                f"Please take your medication as prescribed.\n"
                f"If you have any side effects or concerns, consult your healthcare provider.\n\n"
                f"💡 This is a medication reminder - follow your prescription!"
            )
            
            logger.info(f"💊 Sending medication reminder SMS for {medication} to {to}")
            
            # Send medication reminder SMS
            result = self.send_sms_message(to, reminder_message)
            
            if result.get('success'):
                logger.info(f"✅ Medication reminder SMS sent successfully to {to}")
            else:
                logger.error(f"❌ Failed to send medication reminder SMS to {to}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error sending medication reminder SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending medication reminder SMS. Please try again later."
            }
    
    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Verify incoming webhook from Twilio
        
        Args:
            data: Webhook verification data
            
        Returns:
            Boolean indicating verification success
        """
        try:
            # Twilio verification
            account_sid = data.get('AccountSid')
            if account_sid and account_sid == self.account_sid:
                logger.info("✅ Twilio webhook verified successfully")
                return True
            
            # Manual verification token check
            verify_token = data.get('verify_token')
            if verify_token and verify_token == self.verify_token:
                logger.info("✅ Twilio manual verification successful")
                return True
            
            logger.error("❌ Twilio webhook verification failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error verifying Twilio webhook: {e}", exc_info=True)
            return False
    
    async def close(self):
        """Close Twilio SMS service"""
        try:
            if self.client:
                logger.info("🔌 Twilio SMS service closed")
            return {"success": True, "message": "Twilio SMS service closed"}
        except Exception as e:
            logger.error(f"❌ Error closing Twilio SMS service: {e}")
            return {"success": False, "error": str(e)}

# Create service instance
twilio_sms_service = TwilioSMSService()

# Test function
def test_twilio_sms_service():
    """Test Twilio SMS service"""
    print("🧪 Testing Twilio SMS Service")
    print("=" * 30)
    
    service = TwilioSMSService()
    
    if service.is_configured:
        print("✅ Twilio SMS service configured")
        print(f"SMS number: {service.sms_number}")
        
        # Test SMS sending (to yourself for testing)
        test_number = "+917019567529"  # Your number
        test_message = "🧪 Twilio SMS test - Healthcare Chatbot is working!"
        
        print(f"\n📤 Sending test SMS to {test_number}")
        result = service.send_sms_message(test_number, test_message)
        print(f"Result: {result}")
        
        if result.get('success'):
            print("✅ Twilio SMS sent successfully!")
        else:
            print("❌ Twilio SMS failed")
            print(f"Error: {result.get('error')}")
    else:
        print("⚠️  Twilio SMS not configured - showing mock behavior")
        
        # Test mock functionality
        test_number = "+917019567529"
        test_message = "🧪 Mock SMS test - Healthcare Chatbot is working!"
        
        print(f"\n📤 Sending mock SMS to {test_number}")
        result = service.send_sms_message(test_number, test_message)
        print(f"Mock result: {result}")
        
        if result.get('success'):
            print("✅ Mock SMS sent successfully!")
        else:
            print("❌ Mock SMS failed")

if __name__ == "__main__":
    test_twilio_sms_service()