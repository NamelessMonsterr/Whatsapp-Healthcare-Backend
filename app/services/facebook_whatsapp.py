"""
Facebook WhatsApp Service - Healthcare Chatbot Integration
"""
import logging
from typing import Dict, Any, List, Optional
import json
import requests
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class FacebookWhatsAppService:
    """Facebook WhatsApp Business API Service"""
    
    def __init__(self):
        self.access_token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.business_account_id = settings.whatsapp_business_account_id
        self.verify_token = settings.verify_token
        
        # ✅ FIXED: Correct base URL format
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Facebook WhatsApp Service initialized - Phone ID: {self.phone_number_id}")
    
    def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send text message via Facebook WhatsApp API
        
        Args:
            to: Recipient phone number
            text: Message text to send
            
        Returns:
            Dict with sending results
        """
        try:
            # ✅ FIXED: Ensure correct phone number format
            to_clean = to.replace("whatsapp:", "")
            
            logger.info(f"📤 Sending Facebook message to {to_clean}")
            logger.info(f"Message: {text[:100]}...")
            
            # ✅ FIXED: Correct endpoint URL
            url = f"{self.base_url}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,  # ✅ FIXED: Clean phone number
                "text": {"body": text}
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Facebook message sent successfully")
                return {"success": True, "data": data}
            else:
                error_data = response.json()
                logger.error(f"❌ Failed to send Facebook message. Status: {response.status_code}, Response: {error_data}")
                return {"success": False, "status": response.status_code, "error": error_data}
                
        except Exception as e:
            logger.error(f"Error sending Facebook text message: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def send_interactive_message(self, to: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send interactive message with buttons via Facebook WhatsApp API
        
        Args:
            to: Recipient phone number
            text: Message text
            buttons: List of button dictionaries
            
        Returns:
            Dict with sending results
        """
        try:
            # ✅ FIXED: Ensure correct phone number format
            to_clean = to.replace("whatsapp:", "")
            
            logger.info(f"📤 Sending Facebook interactive message to {to_clean}")
            logger.info(f"Buttons: {len(buttons)}")
            
            # ✅ FIXED: Correct endpoint URL
            url = f"{self.base_url}/messages"
            
            # Limit to 3 buttons (Facebook limit)
            limited_buttons = buttons[:3]
            
            # Format buttons for Facebook API
            formatted_buttons = []
            for i, button in enumerate(limited_buttons):
                formatted_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": button.get("id", f"button_{i}"),
                        "title": button.get("title", f"Button {i+1}")[:20]  # Facebook limit
                    }
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,  # ✅ FIXED: Clean phone number
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text},
                    "action": {"buttons": formatted_buttons}
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Facebook interactive message sent successfully")
                return {"success": True, "data": data}
            else:
                error_data = response.json()
                logger.error(f"❌ Failed to send Facebook interactive message. Status: {response.status_code}, Response: {error_data}")
                return {"success": False, "status": response.status_code, "error": error_data}
                
        except Exception as e:
            logger.error(f"Error sending Facebook interactive message: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def send_list_message(self, to: str, header: str, body: str, button_text: str, 
                         sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send list message via Facebook WhatsApp API
        
        Args:
            to: Recipient phone number
            header: List message header
            body: List message body
            button_text: Button text to open list
            sections: List sections with rows
            
        Returns:
            Dict with sending results
        """
        try:
            # ✅ FIXED: Ensure correct phone number format
            to_clean = to.replace("whatsapp:", "")
            
            logger.info(f"📤 Sending Facebook list message to {to_clean}")
            
            # ✅ FIXED: Correct endpoint URL
            url = f"{self.base_url}/messages"
            
            # Format sections for Facebook API (limit to 10 sections, 10 rows each)
            formatted_sections = []
            for section in sections[:10]:
                rows = []
                for row in section.get("rows", [])[:10]:
                    rows.append({
                        "id": row.get("id", "row_default")[:200],  # Facebook limit
                        "title": row.get("title", "Row Title")[:24],  # Facebook limit
                        "description": row.get("description", "")[:72]  # Facebook limit
                    })
                
                if rows:
                    formatted_section = {
                        "title": section.get("title", "Section")[:24],  # Facebook limit
                        "rows": rows
                    }
                    formatted_sections.append(formatted_section)
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,  # ✅ FIXED: Clean phone number
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": header[:60]},  # Facebook limit
                    "body": {"text": body[:1024]},  # Facebook limit
                    "footer": {"text": "Healthcare Chatbot"},
                    "action": {
                        "button": button_text[:20],  # Facebook limit
                        "sections": formatted_sections
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Facebook list message sent successfully")
                return {"success": True, "data": data}
            else:
                error_data = response.json()
                logger.error(f"❌ Failed to send Facebook list message. Status: {response.status_code}, Response: {error_data}")
                return {"success": False, "status": response.status_code, "error": error_data}
                
        except Exception as e:
            logger.error(f"Error sending Facebook list message: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def parse_webhook_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook message from Facebook
        
        Args:
            data: Raw webhook data
            
        Returns:
            Parsed message data or None
        """
        try:
            logger.info("📥 Parsing Facebook webhook message")
            logger.info(f"Webhook data: {json.dumps(data, indent=2)}")
            
            # Parse Facebook webhook format
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])[0]
            contacts = value.get('contacts', [{}])[0]
            
            if not messages:
                logger.info("No message data found in webhook")
                return None
            
            return {
                "message_id": messages.get('id'),
                "from": messages.get('from', '').replace('whatsapp:', ''),
                "timestamp": messages.get('timestamp'),
                "type": messages.get('type'),
                "contact_name": contacts.get('profile', {}).get('name'),
                "text": messages.get('text', {}).get('body') if messages.get('type') == 'text' else None,
                "interactive": messages.get('interactive'),
                "image": messages.get('image'),
                "audio": messages.get('audio'),
                "document": messages.get('document'),
                "location": messages.get('location'),
                "sticker": messages.get('sticker')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Facebook webhook message: {e}", exc_info=True)
            return None
    
    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Verify incoming webhook from Facebook
        
        Args:
            data: Webhook verification data
            
        Returns:
            Boolean indicating verification success
        """
        try:
            hub_mode = data.get('hub.mode')
            hub_verify_token = data.get('hub.verify_token')
            hub_challenge = data.get('hub.challenge')
            
            logger.info(f"🔍 Webhook verification request")
            logger.info(f"Mode: {hub_mode}, Token: {hub_verify_token}, Challenge: {hub_challenge}")
            
            if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
                logger.info("✅ Facebook webhook verified successfully")
                return True
            else:
                logger.error(f"❌ Facebook webhook verification failed")
                logger.error(f"Expected token: {self.verify_token}, Got: {hub_verify_token}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying Facebook webhook: {e}", exc_info=True)
            return False
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read via Facebook WhatsApp API
        
        Args:
            message_id: Message ID to mark as read
            
        Returns:
            Dict with success status
        """
        try:
            logger.info(f"✅ Marking message {message_id} as read")
            
            # ✅ FIXED: Correct endpoint URL
            url = f"{self.base_url}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Message {message_id} marked as read")
                return {"success": True, "data": data}
            else:
                error_data = response.json()
                logger.error(f"❌ Failed to mark message as read. Status: {response.status_code}, Response: {error_data}")
                return {"success": False, "status": response.status_code, "error": error_data}
                
        except Exception as e:
            logger.error(f"Error marking message as read: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close Facebook WhatsApp service"""
        try:
            logger.info("🔌 Facebook WhatsApp service closed")
            return {"success": True, "message": "Facebook WhatsApp service closed"}
        except Exception as e:
            logger.error(f"Error closing Facebook WhatsApp service: {e}")
            return {"success": False, "error": str(e)}

# Create service instance
facebook_whatsapp_service = FacebookWhatsAppService()