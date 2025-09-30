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

        # FIXED: Correct API base URL construction
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
            'max_per_minute': 60
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
                return None
            
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
                "from": message.get('from', '').replace('whatsapp:', ''),
                "timestamp": message.get('timestamp'),
                "type": message_type,
                "contact_name": contact.get('profile', {}).get('name', 'Unknown User'),
            }
            
            # FIXED: Parse based on message type with validation
            if message_type == 'text':
                text_data = message.get('text', {})
                if isinstance(text_data, dict):
                    parsed_message["text"] = text_data.get('body')
                else:
                    parsed_message["text"] = str(text_data)
            elif message_type == 'interactive':
                parsed_message["interactive"] = message.get('interactive')
            elif message_type == 'image':
                parsed_message["image"] = message.get('image')
            elif message_type == 'audio':
                parsed_message["audio"] = message.get('audio')
            elif message_type == 'document':
                parsed_message["document"] = message.get('document')
            elif message_type == 'location':
                parsed_message["location"] = message.get('location')
            elif message_type == 'sticker':
                parsed_message["sticker"] = message.get('sticker')
            else:
                logger.info(f"Unsupported message type: {message_type}")
            
            # FIXED: Validate parsed message
            if self._validate_parsed_message(parsed_message):
                logger.info(f"✅ Parsed {message_type} message from {mask_sensitive_data(parsed_message['from'])}")
                return parsed_message
            else:
                logger.warning("Parsed message validation failed")
                return None

        except Exception as e:
            logger.error(f"❌ Error parsing webhook: {e}", exc_info=True)
            return None

    def _validate_parsed_message(self, message: Dict[str, Any]) -> bool:
        """Validate parsed message data"""
        try:
            # FIXED: Check required fields
            required_fields = ['message_id', 'from', 'type']
            for field in required_fields:
                if not message.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # FIXED: Validate phone number format
            phone = message.get('from', '')
            if not phone or len(phone) < 10 or len(phone) > 15:
                logger.warning("Invalid phone number format")
                return False
            
            # FIXED: Validate message ID
            msg_id = message.get('message_id')
            if not msg_id or len(msg_id) < 5:
                logger.warning("Invalid message ID")
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Message validation failed: {e}")
            return False

    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """Verify webhook with secure token comparison"""
        try:
            hub_mode = data.get('hub.mode')
            hub_verify_token = data.get('hub.verify_token')
            hub_challenge = data.get('hub.challenge')

            logger.info(f"🔍 Webhook verification request: mode={hub_mode}")

            # FIXED: Validate all required parameters
            if not all([hub_mode, hub_verify_token, hub_challenge]):
                logger.error("Missing required webhook verification parameters")
                return False

            if hub_mode != "subscribe":
                logger.error(f"Invalid hub mode: {hub_mode}")
                return False
            
            # FIXED: Use secure constant-time comparison to prevent timing attacks
            if secrets.compare_digest(hub_verify_token, self.verify_token):
                logger.info("✅ Webhook verified successfully")
                return True
            else:
                logger.error("❌ Webhook verification failed - token mismatch")
                return False

        except Exception as e:
            logger.error(f"❌ Error verifying webhook: {e}", exc_info=True)
            return False

    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic and proper error handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "POST":
                    response = await self.client.post(url, headers=self.headers, **kwargs)
                elif method.upper() == "GET":
                    response = await self.client.get(url, headers=self.headers, **kwargs)
                else:
                    return {"success": False, "error": f"Unsupported HTTP method: {method}"}
                
                # FIXED: Handle different status codes appropriately
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        return {"success": False, "error": "Rate limit exceeded after retries"}
                elif response.status_code >= 500:  # Server error
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Server error {response.status_code}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        return {"success": False, "error": f"Server error: {response.status_code}"}
                else:
                    # Client error
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    return {"success": False, "error": error_msg}
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Request timeout, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {"success": False, "error": "Request timeout after retries"}
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.error(f"Request error: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {"success": False, "error": f"Request failed: {str(e)}"}
        
        return {"success": False, "error": "Max retries exceeded"}

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.utcnow()
        
        # Reset counter if minute has passed
        if (now - self.rate_limiter['last_reset']).total_seconds() > 60:
            self.rate_limiter['messages_sent'] = 0
            self.rate_limiter['last_reset'] = now
        
        return self.rate_limiter['messages_sent'] < self.rate_limiter['max_per_minute']

    def _update_rate_limit(self):
        """Update rate limit counter"""
        self.rate_limiter['messages_sent'] += 1

    async def close(self):
        """Close async client properly"""
        try:
            await self.client.aclose()
            logger.info("🔌 WhatsApp service closed successfully")
            return {"success": True, "message": "WhatsApp service closed"}
        except Exception as e:
            logger.error(f"❌ Error closing WhatsApp service: {e}")
            return {"success": False, "error": str(e)}

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'client'):
                # Note: This is a fallback - prefer explicit close() call
                asyncio.create_task(self.client.aclose())
        except:
            pass

# ✅ Create service instance with error handling
try:
    whatsapp_service = UnifiedWhatsAppService()
    logger.info("✅ WhatsApp service instance created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create WhatsApp service: {e}")
    whatsapp_service = None

# Test function
async def test_whatsapp_service():
    """Comprehensive test for WhatsApp service"""
    print("🧪 Testing WhatsApp Service")
    
    if not whatsapp_service:
        print("❌ WhatsApp service not available")
        return
    
    # Test phone validation
    test_numbers = [
        "+91917019567529",  # Valid with +
        "917019567529",     # Valid without +
        "91917019567529",   # Valid with country code
        "123",              # Invalid
        "",                 # Empty
    ]
    
    print("📱 Phone validation tests:")
    for number in test_numbers:
        try:
            validated = validate_whatsapp_phone(number)
            print(f"  ✅ {number} -> {validated}")
        except ValueError as e:
            print(f"  ❌ {number} -> Error: {e}")
    
    # Test message parsing
    test_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "test_msg_123",
                        "from": "91917019567529",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Hello, this is a test message"}
                    }],
                    "contacts": [{
                        "profile": {"name": "Test User"}
                    }]
                }
            }]
        }]
    }
    
    print("\n📨 Webhook parsing test:")
    parsed = whatsapp_service.parse_webhook_message(test_webhook)
    if parsed:
        print(f"  ✅ Parsed successfully: {parsed}")
    else:
        print("  ❌ Failed to parse webhook")
    
    # Test webhook verification
    print("\n🔍 Webhook verification test:")
    verify_data = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.verify_token,
        "hub.challenge": "test_challenge_123"
    }
    
    if whatsapp_service.verify_webhook(verify_data):
        print("  ✅ Webhook verification passed")
    else:
        print("  ❌ Webhook verification failed")
    
    await whatsapp_service.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_whatsapp_service())
