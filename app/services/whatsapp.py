"""
Unified WhatsApp Service - FIXED WITH ASYNC HTTPX
"""
import logging
from typing import Dict, Any, List, Optional
import json
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

class UnifiedWhatsAppService:
    """Unified WhatsApp service with proper async client"""

    def __init__(self):
        self.access_token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.business_account_id = settings.whatsapp_business_account_id
        self.verify_token = settings.verify_token

        # ✅ FIXED: Correct API version
        self.base_url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        logger.info("Unified WhatsApp Service initialized")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Phone Number ID: {self.phone_number_id}")
        logger.info(f"Access Token Prefix: {self.access_token[:15]}...")

        # Reuse async client
        self.client = httpx.AsyncClient(timeout=30)

    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message"""
        try:
            to_clean = to.replace("whatsapp:", "").replace("+", "")
            logger.info(f"📤 Sending WhatsApp text to {to_clean}")
            logger.info(f"Message: {text[:100]}...")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,
                "text": {"body": text}
            }

            response = await self.client.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ WhatsApp text sent successfully")
                return {"success": True, "data": data}
            else:
                logger.error(f"❌ Failed text. Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error sending WhatsApp text: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_interactive_message(self, to: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send interactive message with buttons"""
        try:
            to_clean = to.replace("whatsapp:", "").replace("+", "")
            logger.info(f"📤 Sending WhatsApp interactive to {to_clean}")

            url = f"{self.base_url}/messages"

            limited_buttons = buttons[:3]
            formatted_buttons = [
                {
                    "type": "reply",
                    "reply": {
                        "id": b.get("id", f"button_{i}"),
                        "title": b.get("title", f"Button {i+1}")[:20]
                    }
                }
                for i, b in enumerate(limited_buttons)
            ]

            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text},
                    "action": {"buttons": formatted_buttons}
                }
            }

            response = await self.client.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ WhatsApp interactive sent successfully")
                return {"success": True, "data": data}
            else:
                logger.error(f"❌ Failed interactive. Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error sending interactive: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        try:
            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }

            response = await self.client.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                logger.info(f"✅ Message {message_id} marked as read")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"❌ Failed mark read. Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error marking read: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def parse_webhook_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse webhook message"""
        try:
            logger.info("📥 Parsing webhook")
            logger.info(f"Webhook data: {json.dumps(data, indent=2)}")

            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])[0]
            contacts = value.get('contacts', [{}])[0]

            if not messages:
                logger.info("No messages found")
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
            logger.error(f"Error parsing webhook: {e}", exc_info=True)
            return None

    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """Verify webhook"""
        try:
            hub_mode = data.get('hub.mode')
            hub_verify_token = data.get('hub.verify_token')
            hub_challenge = data.get('hub.challenge')

            logger.info(f"🔍 Webhook verification request: mode={hub_mode}, token={hub_verify_token}")

            if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
                logger.info("✅ Webhook verified")
                return True
            else:
                logger.error("❌ Webhook verification failed")
                return False

        except Exception as e:
            logger.error(f"Error verifying webhook: {e}", exc_info=True)
            return False

    async def close(self):
        """Close async client"""
        try:
            await self.client.aclose()
            logger.info("🔌 WhatsApp service closed")
            return {"success": True, "message": "WhatsApp service closed"}
        except Exception as e:
            logger.error(f"Error closing WhatsApp service: {e}")
            return {"success": False, "error": str(e)}


# ✅ Create service instance
whatsapp_service = UnifiedWhatsAppService()


# Test runner
async def test_whatsapp_service():
    """Quick test for hackathon"""
    print("🧪 Testing WhatsApp Service")
    service = UnifiedWhatsAppService()

    test_number = "917019567529"  # ✅ No +
    test_message = "🧪 Healthcare Chatbot test - it's working!"

    result = await service.send_text_message(test_number, test_message)
    print(f"Result: {result}")

    await service.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_whatsapp_service())
