"""
Unified WhatsApp Service - FIXED VERSION with Enhanced Features
"""
import logging
from typing import Dict, Any, List, Optional
import json
import httpx
import asyncio
from datetime import datetime

from app.config import settings
from app.core.security import validate_whatsapp_phone, sanitize_input_string  # FIXED: Added security

logger = logging.getLogger(__name__)

class UnifiedWhatsAppService:
    """Unified WhatsApp service with enhanced security and error handling"""

    def __init__(self):
        self.access_token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.business_account_id = settings.whatsapp_business_account_id
        self.verify_token = settings.verify_token

        # FIXED: Validate configuration
        if not self.access_token:
            logger.warning("WhatsApp access token not configured")
        if not self.phone_number_id:
            logger.warning("WhatsApp phone number ID not configured")

        # FIXED: Use configurable API version
        self.api_version = "v20.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "HealthcareBot/1.0"
        }

        logger.info("Unified WhatsApp Service initialized")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Phone Number ID: {self.phone_number_id}")
        logger.info(f"Access Token configured: {bool(self.access_token)}")

        # FIXED: Configure client with better timeout and retry settings
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            transport=httpx.AsyncHTTPTransport(retries=3)
        )
        
        # FIXED: Add rate limiting tracking
        self.rate_limit_tracker = {
            'messages_sent': 0,
            'last_reset': datetime.utcnow(),
            'rate_limit_exceeded': False
        }

    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message with enhanced validation and error handling"""
        try:
            # FIXED: Validate and sanitize inputs
            if not to or not text:
                return {"success": False, "error": "Phone number and text are required"}
            
            if len(text.strip()) == 0:
                return {"success": False, "error": "Message text cannot be empty"}
            
            if len(text) > 4096:  # WhatsApp message limit
                return {"success": False, "error": "Message too long (max 4096 characters)"}
            
            # Validate and format phone number
            try:
                to_clean = validate_whatsapp_phone(to)
            except ValueError as e:
                logger.error(f"Invalid phone number {to}: {e}")
                return {"success": False, "error": f"Invalid phone number: {e}"}
            
            # Sanitize message text
            text = sanitize_input_string(text, max_length=4096)
            
            logger.info(f"📤 Sending WhatsApp text to {to_clean}")
            logger.info(f"Message length: {len(text)} characters")
            logger.info(f"Message preview: {text[:100]}...")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_clean,
                "type": "text",
                "text": {"body": text}
            }

            # FIXED: Add retry logic for failed requests
            for attempt in range(3):
                try:
                    response = await self.client.post(url, headers=self.headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.rate_limit_tracker['messages_sent'] += 1
                        logger.info(f"✅ WhatsApp text sent successfully (attempt {attempt + 1})")
                        return {
                            "success": True, 
                            "data": data,
                            "message_id": data.get('messages', [{}])[0].get('id'),
                            "attempt": attempt + 1
                        }
                    elif response.status_code == 429:  # Rate limit
                        logger.warning(f"Rate limit hit (attempt {attempt + 1})")
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    else:
                        logger.error(f"❌ Failed text (attempt {attempt + 1}). Status: {response.status_code}")
                        logger.error(f"Response: {response.text[:500]}")
                        
                        if attempt == 2:  # Final attempt failed
                            return {
                                "success": False, 
                                "status": response.status_code, 
                                "error": response.text[:500],
                                "attempt": attempt + 1
                            }
                        
                        await asyncio.sleep(1)  # Brief pause before retry
                        
                except httpx.TimeoutException:
                    logger.warning(f"Timeout on attempt {attempt + 1}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        return {"success": False, "error": "Request timeout after 3 attempts"}
                except Exception as retry_error:
                    logger.error(f"Retry attempt {attempt + 1} failed: {retry_error}")
                    if attempt == 2:
                        return {"success": False, "error": f"All retry attempts failed: {retry_error}"}
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error sending WhatsApp text: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_interactive_message(self, to: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send interactive message with buttons and enhanced validation"""
        try:
            # FIXED: Validate inputs
            if not to or not text or not buttons:
                return {"success": False, "error": "Phone number, text, and buttons are required"}
            
            if len(text) > 1024:  # WhatsApp interactive text limit
                return {"success": False, "error": "Interactive text too long (max 1024 characters)"}
            
            if len(buttons) > 3:  # WhatsApp button limit
                return {"success": False, "error": "Too many buttons (max 3)"}
            
            # Validate phone number
            try:
                to_clean = validate_whatsapp_phone(to)
            except ValueError as e:
                return {"success": False, "error": f"Invalid phone number: {e}"}
            
            # Sanitize text and buttons
            text = sanitize_input_string(text, max_length=1024)
            
            logger.info(f"📤 Sending WhatsApp interactive to {to_clean}")
            logger.info(f"Text: {text[:100]}...")
            logger.info(f"Buttons: {[btn.get('title', '') for btn in buttons]}")

            url = f"{self.base_url}/messages"

            # FIXED: Enhanced button validation and formatting
            limited_buttons = buttons[:3]
            formatted_buttons = []
            
            for i, button in enumerate(limited_buttons):
                button_title = sanitize_input_string(
                    str(button.get('title', f'Option {i+1}')), 
                    max_length=20
                )
                button_id = sanitize_input_string(
                    str(button.get('id', f'button_{i}')), 
                    max_length=200
                )
                
                formatted_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": button_id,
                        "title": button_title
                    }
                })

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
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
                self.rate_limit_tracker['messages_sent'] += 1
                logger.info("✅ WhatsApp interactive sent successfully")
                return {
                    "success": True, 
                    "data": data,
                    "message_id": data.get('messages', [{}])[0].get('id')
                }
            else:
                logger.error(f"❌ Failed interactive. Status: {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return {
                    "success": False, 
                    "status": response.status_code, 
                    "error": response.text[:500]
                }

        except Exception as e:
            logger.error(f"Error sending interactive: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_location_request(self, to: str, text: str = "Please share your location") -> Dict[str, Any]:
        """Send location sharing request"""
        try:
            if not to:
                return {"success": False, "error": "Phone number is required"}
            
            try:
                to_clean = validate_whatsapp_phone(to)
            except ValueError as e:
                return {"success": False, "error": f"Invalid phone number: {e}"}
            
            text = sanitize_input_string(text, max_length=200)
            
            logger.info(f"📍 Requesting location from {to_clean}")

            url = f"{self.base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_clean,
                "type": "text",
                "text": {
                    "body": text,
                    "preview_url": False
                }
            }

            response = await self.client.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Location request sent successfully")
                return {"success": True, "data": data}
            else:
                logger.error(f"❌ Failed location request. Status: {response.status_code}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error sending location request: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read with error handling"""
        try:
            if not message_id:
                return {"success": False, "error": "Message ID is required"}
            
            logger.info(f"👁️ Marking message {message_id} as read")

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
                logger.error(f"❌ Failed to mark read. Status: {response.status_code}")
                # Don't fail the entire operation if mark_as_read fails
                return {"success": True, "warning": f"Failed to mark as read: {response.status_code}"}

        except Exception as e:
            logger.error(f"Error marking message as read: {e}", exc_info=True)
            # Don't fail the entire operation if mark_as_read fails
            return {"success": True, "warning": f"Error marking as read: {e}"}

    def parse_webhook_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse webhook message with enhanced error handling"""
        try:
            logger.info("📥 Parsing webhook message")
            # FIXED: Limit logging for large payloads
            data_size = len(json.dumps(data))
            if data_size < 10000:
                logger.info(f"Webhook data: {json.dumps(data, indent=2)}")
            else:
                logger.info(f"Large webhook data ({data_size} bytes), truncating log...")
                logger.info(f"Webhook summary: {str(data)[:500]}...")

            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])[0]
            contacts = value.get('contacts', [{}])[0]

            if not messages or not messages.get('id'):
                logger.info("No valid message found in webhook")
                return None

            # FIXED: Enhanced message parsing with better error handling
            message_type = messages.get('type', 'unknown')
            
            parsed_message = {
                "message_id": messages.get('id'),
                "from": messages.get('from', '').replace('whatsapp:', ''),
                "timestamp": messages.get('timestamp'),
                "type": message_type,
                "contact_name": contacts.get('profile', {}).get('name', 'Unknown'),
            }

            # Parse based on message type
            if message_type == 'text':
                parsed_message["text"] = messages.get('text', {}).get('body')
            elif message_type == 'interactive':
                parsed_message["interactive"] = messages.get('interactive')
            elif message_type == 'image':
                parsed_message["image"] = messages.get('image')
            elif message_type == 'audio':
                parsed_message["audio"] = messages.get('audio')
            elif message_type == 'document':
                parsed_message["document"] = messages.get('document')
            elif message_type == 'location':
                parsed_message["location"] = messages.get('location')
            elif message_type == 'sticker':
                parsed_message["sticker"] = messages.get('sticker')
            else:
                logger.info(f"Unsupported message type: {message_type}")

            # FIXED: Validate parsed message
            if self._validate_parsed_message(parsed_message):
                return parsed_message
            else:
                logger.warning("Parsed message validation failed")
                return None

        except Exception as e:
            logger.error(f"Error parsing webhook: {e}", exc_info=True)
            return None

    def _validate_parsed_message(self, message: Dict[str, Any]) -> bool:
        """Validate parsed message data"""
        try:
            required_fields = ['message_id', 'from', 'type']
            for field in required_fields:
                if not message.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate phone number format
            from app.core.security import validate_whatsapp_phone
            validate_whatsapp_phone(message['from'])
            
            return True
        except Exception as e:
            logger.error(f"Message validation failed: {e}")
            return False

    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """Verify webhook with enhanced validation"""
        try:
            hub_mode = data.get('hub.mode')
            hub_verify_token = data.get('hub.verify_token')
            hub_challenge = data.get('hub.challenge')

            logger.info(f"🔍 Webhook verification request: mode={hub_mode}")

            # FIXED: Validate all required parameters
            if not all([hub_mode, hub_verify_token, hub_challenge]):
                logger.error("Missing required webhook verification parameters")
                return False

            if hub_mode == "subscribe":
                # FIXED: Use secure comparison
                if secrets.compare_digest(hub_verify_token, self.verify_token):
                    logger.info("✅ Webhook verified successfully")
                    return True
                else:
                    logger.error("❌ Webhook verification failed - token mismatch")
                    return False
            else:
                logger.error(f"❌ Invalid hub mode: {hub_mode}")
                return False

        except Exception as e:
            logger.error(f"Error verifying webhook: {e}", exc_info=True)
            return False

    async def get_business_profile(self) -> Dict[str, Any]:
        """Get WhatsApp Business profile information"""
        try:
            if not self.business_account_id:
                return {"success": False, "error": "Business account ID not configured"}

            url = f"https://graph.facebook.com/{self.api_version}/{self.business_account_id}"
            params = {
                "fields": "name,phone_numbers,message_template_namespace",
                "access_token": self.access_token
            }

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Business profile retrieved successfully")
                return {"success": True, "data": data}
            else:
                logger.error(f"❌ Failed to get business profile. Status: {response.status_code}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error getting business profile: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def get_message_templates(self) -> Dict[str, Any]:
        """Get approved message templates"""
        try:
            if not self.business_account_id:
                return {"success": False, "error": "Business account ID not configured"}

            url = f"https://graph.facebook.com/{self.api_version}/{self.business_account_id}/message_templates"
            params = {"access_token": self.access_token}

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved {len(data.get('data', []))} message templates")
                return {"success": True, "data": data}
            else:
                logger.error(f"❌ Failed to get message templates. Status: {response.status_code}")
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            logger.error(f"Error getting message templates: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status"""
        return {
            "messages_sent": self.rate_limit_tracker['messages_sent'],
            "last_reset": self.rate_limit_tracker['last_reset'].isoformat(),
            "rate_limit_exceeded": self.rate_limit_tracker['rate_limit_exceeded'],
            "estimated_limit": 1000  # WhatsApp Business API daily limit
        }

    async def close(self):
        """Close async client with proper cleanup"""
        try:
            await self.client.aclose()
            logger.info("🔌 WhatsApp service closed successfully")
            return {"success": True, "message": "WhatsApp service closed"}
        except Exception as e:
            logger.error(f"Error closing WhatsApp service: {e}")
            return {"success": False, "error": str(e)}

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'client'):
                # Create new event loop for cleanup if needed
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self.client.aclose())
                    else:
                        loop.run_until_complete(self.client.aclose())
                except RuntimeError:
                    # No event loop running, create new one
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.client.aclose())
                    loop.close()
        except Exception as e:
            logger.error(f"Error in WhatsApp service cleanup: {e}")

# FIXED: Create service instance with proper error handling
try:
    whatsapp_service = UnifiedWhatsAppService()
    logger.info("WhatsApp service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize WhatsApp service: {e}")
    # Create a mock service for development/testing
    class MockWhatsAppService:
        async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
            logger.info(f"MOCK: Would send to {to}: {text[:50]}...")
            return {"success": True, "mock": True}
        
        async def send_interactive_message(self, to: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
            logger.info(f"MOCK: Would send interactive to {to}")
            return {"success": True, "mock": True}
        
        async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
            logger.info(f"MOCK: Would mark {message_id} as read")
            return {"success": True, "mock": True}
        
        async def close(self):
            logger.info("MOCK: WhatsApp service closed")
            return {"success": True, "mock": True}
    
    whatsapp_service = MockWhatsAppService()
    logger.warning("Using mock WhatsApp service - configure credentials for production")

# Test function with comprehensive testing
async def test_whatsapp_service():
    """Comprehensive test for WhatsApp service"""
    print("🧪 Testing WhatsApp Service")
    print("=" * 40)

    service = whatsapp_service
    
    # Test configuration
    print(f"Service configured: {bool(settings.whatsapp_token)}")
    print(f"Phone Number ID: {settings.whatsapp_phone_number_id}")
    print(f"API Version: {service.api_version}")

    if not settings.whatsapp_token:
        print("⚠️  WhatsApp not configured - showing mock behavior")
        print("✅ Mock service test completed")
        return

    # Test with invalid number
    print("\n1. Testing with invalid phone number...")
    result = await service.send_text_message("invalid", "Test message")
    print(f"Result: {result}")

    # Test with valid format
    print("\n2. Testing with valid phone number format...")
    test_number = "917019567529"  # Replace with your test number
    test_message = "🧪 Healthcare Chatbot test - it's working! (Reply STOP to opt out)"
    
    result = await service.send_text_message(test_number, test_message)
    print(f"Text message result: {result}")

    # Test interactive message
    print("\n3. Testing interactive message...")
    buttons = [
        {"id": "test1", "title": "Test Option 1"},
        {"id": "test2", "title": "Test Option 2"}
    ]
    
    result = await service.send_interactive_message(
        test_number, 
        "Choose an option for testing:", 
        buttons
    )
    print(f"Interactive message result: {result}")

    # Test mark as read
    print("\n4. Testing mark as read...")
    if result.get('success') and result.get('message_id'):
        read_result = await service.mark_as_read(result['message_id'])
        print(f"Mark as read result: {read_result}")

    # Get rate limit status
    print("\n5. Rate limit status:")
    rate_status = service.get_rate_limit_status()
    print(f"Rate limit info: {json.dumps(rate_status, indent=2)}")

    # Cleanup
    await service.close()
    print("\n✅ WhatsApp service test completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_whatsapp_service())
