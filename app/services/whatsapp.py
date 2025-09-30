"""
Unified WhatsApp Service - COMPLETELY FIXED VERSION
"""
import logging
from typing import Dict, Any, List, Optional
import json
import httpx
import secrets
from datetime import datetime, timedelta
import asyncio
import re
from app.config import settings
from app.core.security import validate_whatsapp_phone, sanitize_input_string, mask_sensitive_data

logger = logging.getLogger(__name__)

class UnifiedWhatsAppService:
    """Completely fixed WhatsApp service with all security and functionality issues resolved"""

    def __init__(self):
        self.access_token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.business_account_id = settings.whatsapp_business_account_id
        self.verify_token = settings.verify_token
        self.api_version = "v20.0"

        # FIXED: Validate configuration
        if not self.phone_number_id:
            raise ValueError("WhatsApp Phone Number ID is not configured")
            
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "HealthcareBot/1.0"
        }

        logger.info("✅ Unified WhatsApp Service initialized")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Phone Number ID: {mask_sensitive_data(self.phone_number_id)}")

        # FIXED: Proper async client with timeout and connection limits
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        timeout = httpx.Timeout(30.0, connect=10.0)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers={"User-Agent": "HealthcareBot/1.0"}
        )
        
        # FIXED: Rate limiting
        self.rate_limiter = {
            'messages_sent': 0,
            'last_reset': datetime.utcnow(),
            'max_per_minute': settings.rate_limit_per_minute
        }

    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message with full validation and error handling"""
        try:
            # FIXED: Comprehensive input validation
            if not to or not text:
                return {"success": False, "error": "Phone number and text are required"}
            
            if len(text) > 4096:  # WhatsApp limit
                return {"success": False, "error": "Message too long (max 4096 characters)"}
            
            # FIXED: Proper phone number validation
            try:
                to_clean = validate_whatsapp_phone(to)
            except ValueError as e:
                return {"success": False, "error": f"Invalid phone number: {e}"}
            
            # FIXED: Input sanitization
            text_clean = sanitize_input_string(text, max_length=4096)
            
            # FIXED: Rate limiting check
            if not self._check_rate_limit():
                return {"success": False, "error": "Rate limit exceeded. Please try again later."}
            
            logger.info(f"📤 Sending WhatsApp text to {mask_sensitive_data(to_clean)}")
            logger.info(f"Message: {text_clean[:100]}...")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_clean,
                "type": "text",
                "text": {"body": text_clean}
            }

            # FIXED: Proper error handling and retry logic
            response = await self._make_request_with_retry("POST", url, json=payload)
            
            if response.get('success'):
                self._update_rate_limit()
                logger.info("✅ WhatsApp text sent successfully")
                return {"success": True, "data": response['data']}
            else:
                logger.error(f"❌ Failed to send text: {response.get('error')}")
                return {"success": False, "error": response.get('error')}

        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp text: {e}", exc_info=True)
            return {"success": False, "error": f"Internal error: {str(e)}"}

    async def send_interactive_message(self, to: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send interactive message with buttons - COMPLETELY FIXED"""
        try:
            # FIXED: Comprehensive validation
            if not to or not text or not buttons:
                return {"success": False, "error": "Phone number, text, and buttons are required"}
            
            if len(buttons) > 3:  # WhatsApp limit
                return {"success": False, "error": "Maximum 3 buttons allowed"}
            
            if len(text) > 1024:  # WhatsApp limit for interactive messages
                return {"success": False, "error": "Interactive message text too long (max 1024 characters)"}
            
            # FIXED: Phone validation
            try:
                to_clean = validate_whatsapp_phone(to)
            except ValueError as e:
                return {"success": False, "error": f"Invalid phone number: {e}"}
            
            # FIXED: Input sanitization
            text_clean = sanitize_input_string(text, max_length=1024)
            
            # FIXED: Button validation and formatting
            formatted_buttons = []
            for i, button in enumerate(buttons):
                if not button.get('title'):
                    return {"success": False, "error": f"Button {i+1} missing title"}
                
                title = sanitize_input_string(button['title'], max_length=20)
                if len(title) < 1:
                    return {"success": False, "error": f"Button {i+1} title too short"}
                
                formatted_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": button.get("id", f"button_{i}"),
                        "title": title
                    }
                })
            
            logger.info(f"📤 Sending WhatsApp interactive to {mask_sensitive_data(to_clean)}")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_clean,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text_clean},
                    "action": {"buttons": formatted_buttons}
                }
            }

            response = await self._make_request_with_retry("POST", url, json=payload)
            
            if response.get('success'):
                self._update_rate_limit()
                logger.info("✅ WhatsApp interactive sent successfully")
                return {"success": True, "data": response['data']}
            else:
                logger.error(f"❌ Failed to send interactive: {response.get('error')}")
                return {"success": False, "error": response.get('error')}

        except Exception as e:
            logger.error(f"❌ Error sending interactive: {e}", exc_info=True)
            return {"success": False, "error": f"Internal error: {str(e)}"}

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read with proper error handling"""
        try:
            if not message_id:
                return {"success": False, "error": "Message ID is required"}
            
            # FIXED: Message ID validation
            if len(message_id) < 5 or len(message_id) > 100:
                return {"success": False, "error": "Invalid message ID format"}
            
            logger.info(f"👁️ Marking message {mask_sensitive_data(message_id)} as read")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }

            response = await self._make_request_with_retry("POST", url, json=payload)
            
            if response.get('success'):
                logger.info(f"✅ Message marked as read successfully")
                return {"success": True, "data": response['data']}
            else:
                # FIXED: Don't fail if mark_as_read fails - it's not critical
                logger.warning(f"⚠️ Failed to mark as read: {response.get('error')}")
                return {"success": True, "warning": f"Failed to mark as read: {response.get('error')}"}

        except Exception as e:
            logger.warning(f"⚠️ Error marking message as read: {e}")
            # FIXED: Return success=True for non-critical operations
            return {"success": True, "warning": f"Error marking as read: {e}"}

    def parse_webhook_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse webhook message with comprehensive error handling"""
        try:
            logger.info("📥 Parsing webhook message")
            
            # FIXED: Handle large payloads efficiently
            data_str = json.dumps(data)
            if len(data_str) > 50000:  # 50KB limit
                logger.warning(f"Large webhook payload: {len(data_str)} bytes")
                # Log summary only
                return self._parse_webhook_summary(data)
            
            # FIXED: Safe navigation through nested data
            entry = data.get('entry', [])
            if not entry or not isinstance(entry, list):
                logger.warning("No entry found in webhook data")
                return None
            
            changes = entry[0].get('changes', [])
            if not changes or not isinstance(changes, list):
                logger.warning("No changes found in webhook data")
                return None
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            contacts = value.get('contacts', [])
            
            if not messages or not isinstance(messages, list):
                logger.info("No messages found in webhook")
                return None
            
            message = messages[0]
            if not isinstance(message, dict):
                logger.warning("Invalid message format")
                return None
            
            contact = contacts[0] if contacts and isinstance(contacts, list) else {}
            
            # FIXED: Extract message type safely
            message_type = message.get('type', 'unknown')
            
            # FIXED: Build parsed message with validation
            parsed_message = {
                "message_id": message.get('id'),
                "from": message.get('from', '').replace('whatsapp:',
