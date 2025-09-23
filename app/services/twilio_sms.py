"""
Twilio SMS Service - Healthcare Alerts via SMS
"""
import logging
from typing import Dict, Any, List, Optional
import json
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
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                self.is_configured = True
                logger.info(f"✅ Twilio SMS Service initialized - Number: {self.sms_number}")
            except ImportError:
                logger.warning("⚠️  Twilio not installed - install with: pip install twilio")
                self.client = None
                self.is_configured = False
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
            
        except Exception as e:
            logger.error(f"❌ Error sending Twilio SMS: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble sending your SMS. Please try again later."
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