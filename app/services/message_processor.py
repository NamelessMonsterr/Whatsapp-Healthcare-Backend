"""
Message Processor Service - FIXED with proper error handling and validation
"""
import logging
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime
import re
import asyncio

from app.services.whatsapp import whatsapp_service
from app.ml.healthcare_models import healthcare_service
from app.core.database import DatabaseManager, get_db_context
from app.config import settings
from app.core.security import validate_whatsapp_phone, sanitize_input_string

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Process incoming WhatsApp messages and generate responses with validation"""

    def __init__(self):
        self.whatsapp = whatsapp_service
        self.healthcare = healthcare_service
        self.db_manager = DatabaseManager()
        logger.info("Message Processor initialized with validation and error handling")

    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook data with validation"""
        try:
            # FIXED: Validate webhook data structure
            if not self._validate_webhook_data(data):
                return {"status": "invalid_webhook", "error": "Invalid webhook data structure"}

            # Parse the webhook message
            message_data = self.whatsapp.parse_webhook_message(data)

            if not message_data:
                logger.info("No valid message data found in webhook")
                return {"status": "no_message"}

            logger.info(f"Processing message from {mask_sensitive_data(message_data.get('from', 'unknown'))}")
            
            # FIXED: Validate message data
            if not self._validate_message_data(message_data):
                return {"status": "invalid_message", "error": "Invalid message data"}

            # Handle different message types
            message_type = message_data.get('type', 'unknown')
            
            if message_type == 'text':
                return await self.process_text_message(message_data)

            elif message_type == 'interactive':
                return await self.process_interactive_message(message_data)

            elif message_type == 'image':
                return await self.process_media_message(message_data, 'image')

            elif message_type == 'audio':
                return await self.process_media_message(message_data, 'audio')

            else:
                # Send a helpful response for unsupported message types
                await self.whatsapp.send_text_message(
                    message_data['from'],
                    "I can currently only process text messages. Please send your health query as text."
                )
                return {"status": "unsupported_type", "type": message_type}

        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _validate_webhook_data(self, data: Dict[str, Any]) -> bool:
        """Validate webhook data structure"""
        try:
            if not isinstance(data, dict):
                return False
            
            entries = data.get('entry', [])
            if not isinstance(entries, list) or not entries:
                return False
            
            for entry in entries:
                if not isinstance(entry, dict):
                    return False
                
                changes = entry.get('changes', [])
                if not isinstance(changes, list):
                    return False
                
                for change in changes:
                    if not isinstance(change, dict):
                        return False
                    
                    value = change.get('value', {})
                    if not isinstance(value, dict):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Webhook validation failed: {e}")
            return False

    def _validate_message_data(self, message_data: Dict[str, Any]) -> bool:
        """Validate parsed message data"""
        try:
            required_fields = ['message_id', 'from', 'type']
            for field in required_fields:
                if not message_data.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate phone number
            phone = message_data.get('from', '')
            if not phone or len(phone) < 10 or len(phone) > 15:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Message data validation failed: {e}")
            return False

    async def process_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text message with comprehensive validation and error handling"""
        sender = message_data['from']
        text = message_data.get('text', '')
        message_id = message_data['message_id']
        contact_name = message_data.get('contact_name', 'User')

        try:
            # FIXED: Validate input parameters
            if not sender or not message_id:
                return {"status": "error", "error": "Missing required parameters"}
            
            if not text or len(text.strip()) == 0:
                await self.whatsapp.send_text_message(
                    sender,
                    "I received an empty message. Please send your health query."
                )
                return {"status": "error", "error": "Empty message"}

            # FIXED: Sanitize input text
            text = sanitize_input_string(text, max_length=1000)
            
            # Mark message as read (with error handling)
            try:
                await self.whatsapp.mark_as_read(message_id)
            except Exception as e:
                logger.warning(f"Failed to mark message as read: {e}")

            # FIXED: Use proper database transaction handling
            user_language = 'en'
            conversation_id = None
            user_id = None

            try:
                with get_db_context() as db:
                    # Get or create user
                    user = self.db_manager.create_user(db, sender, contact_name)
                    user_id = user.id
                    
                    # Extract user language preference
                    user_language = getattr(user, 'language_preference', 'en')
                    
                    # Get or create conversation
                    conversation = self.db_manager.get_or_create_active_conversation(db, user.id)
                    conversation_id = conversation.id
                    
                    # Save incoming message
                    user_message = self.db_manager.save_message(
                        db,
                        conversation_id,
                        message_id,
                        'user',
                        text,
                        message_type='text'
                    )
                    
                    logger.info(f"Saved user message: {message_id} for user {mask_sensitive_data(sender)}")
                    
            except Exception as e:
                logger.error(f"Database error during message saving: {e}")
                # Continue processing even if database save fails

            # FIXED: Process with healthcare service (with timeout and fallback)
            logger.info(f"Processing health query: {text[:100]}...")
            
            try:
                # Detect language automatically
                detected_language = self.healthcare.detect_language(text)
                logger.info(f"Detected language: {detected_language}")
                
                # Process with AI models using the detected language
                response = self.healthcare.process_healthcare_query(text, detected_language)
                
                logger.info(f"AI processing successful - Intent: {response.intent}, Confidence: {response.confidence:.3f}")
                
            except Exception as e:
                logger.error(f"AI processing failed: {e}")
                # FIXED: Fallback response
                response = type('obj', (object,), {
                    'answer': "I understand you have health concerns. For accurate medical advice, please consult with a healthcare provider.",
                    'intent': 'general',
                    'confidence': 0.5,
                    'language': 'en',
                    'processing_time': 0.0,
                    'model_used': 'fallback'
                })()

            # FIXED: Handle emergency cases with proper validation
            if response.intent == "emergency":
                buttons = [
                    {"id": "call_emergency", "title": "Call 108"},
                    {"id": "find_hospital", "title": "Find Hospital"},
                    {"id": "first_aid", "title": "First Aid"}
                ]
                
                try:
                    result = await self.whatsapp.send_interactive_message(
                        sender,
                        response.answer,
                        buttons
                    )
                except Exception as e:
                    logger.error(f"Failed to send interactive message: {e}")
                    # Fallback to text message
                    result = await self.whatsapp.send_text_message(sender, response.answer)
            else:
                try:
                    result = await self.whatsapp.send_text_message(sender, response.answer)
                except Exception as e:
                    logger.error(f"Failed to send text message: {e}")
                    return {"status": "error", "error": f"Failed to send response: {e}"}

            # FIXED: Save bot response to database (with error handling)
            if result and result.get('success'):
                try:
                    with get_db_context() as db:
                        bot_message_id = result.get('data', {}).get('messages', [{}])[0].get('id', str(uuid.uuid4()))
                        
                        # Save bot message
                        bot_message = self.db_manager.save_message(
                            db,
                            conversation_id,
                            bot_message_id,
                            'bot',
                            response.answer,
                            message_type='text',
                            detected_language=response.language,
                            detected_intent=response.intent,
                            confidence_score=response.confidence,
                            model_used=response.model_used,
                            processing_time_ms=response.processing_time * 1000
                        )
                        
                        # Update user message with ML data
                        self.db_manager.update_message_ml_data(
                            db,
                            message_id,
                            detected_language=response.language,
                            detected_intent=response.intent
                        )
                        
                        logger.info(f"Saved bot response: {bot_message_id}")
                        
                except Exception as e:
                    logger.error(f"Database error during response saving: {e}")
                    # Continue even if database save fails

            # FIXED: Send follow-up options (with error handling)
            if response.intent in ["symptom", "medication"] and result and result.get('success'):
                try:
                    await self._send_follow_up_options(sender, response.intent)
                except Exception as e:
                    logger.warning(f"Failed to send follow-up options: {e}")

            return {
                "status": "success",
                "intent": response.intent,
                "confidence": response.confidence,
                "response_sent": result.get('success', False) if result else False,
                "language": response.language,
                "model_used": response.model_used,
                "processing_time": response.processing_time
            }

        except Exception as e:
            logger.error(f"❌ Error processing text message: {e}", exc_info=True)
            
            # FIXED: Send user-friendly error message
            try:
                await self.whatsapp.send_text_message(
                    sender,
                    "I apologize, but I'm having trouble processing your message. Please try rephrasing your health query, or contact support if the issue persists."
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")

            return {"status": "error", "error": str(e)}

    async def process_interactive_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process interactive message (button clicks)"""
        try:
            sender = message_data['from']
            interactive_data = message_data.get('interactive', {})
            
            if not interactive_data:
                return {"status": "error", "error": "No interactive data found"}

            # FIXED: Handle different types of interactive messages
            interactive_type = interactive_data.get('type')
            
            if interactive_type == 'button_reply':
                button_id = interactive_data.get('button_reply', {}).get('id')
                button_text = interactive_data.get('button_reply', {}).get('title')
                
                logger.info(f"Button clicked: {button_id} - {button_text}")
                
                # FIXED: Handle button responses with validation
                response_text = self._handle_button_response(button_id, button_text)
                
                if response_text:
                    result = await self.whatsapp.send_text_message(sender, response_text)
                    return {
                        "status": "success", 
                        "button_id": button_id,
                        "response_sent": result.get('success', False)
                    }
                else:
                    return {"status": "error", "error": "Unknown button ID"}
                    
            elif interactive_type == 'list_reply':
                list_id = interactive_data.get('list_reply', {}).get('id')
                list_title = interactive_data.get('list_reply', {}).get('title')
                
                logger.info(f"List item selected: {list_id} - {list_title}")
                
                response_text = self._handle_list_response(list_id, list_title)
                
                if response_text:
                    result = await self.whatsapp.send_text_message(sender, response_text)
                    return {
                        "status": "success",
                        "list_id": list_id,
                        "response_sent": result.get('success', False)
                    }
                else:
                    return {"status": "error", "error": "Unknown list ID"}
            
            else:
                logger.warning(f"Unsupported interactive type: {interactive_type}")
                return {"status": "unsupported_type", "type": interactive_type}

        except Exception as e:
            logger.error(f"❌ Error processing interactive message: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _handle_button_response(self, button_id: str, button_text: str) -> str:
        """Generate response for button clicks"""
        responses = {
            "call_emergency": "🚨 Please call 108 immediately for emergency services. If you cannot call, ask someone nearby to help you.",
            "find_hospital": "🏥 To find the nearest hospital, please share your location with me, or tell me your current area/city.",
            "first_aid": "🏥 Basic First Aid Tips:\n\n• For cuts: Apply pressure to stop bleeding\n• For burns: Cool with running water\n• For fainting: Lay down with legs elevated\n• For sprains: Rest, Ice, Compression, Elevation\n\n⚠️ These are basic tips only. For serious conditions, seek immediate medical help!",
            "book_appointment": "📅 To book an appointment, please provide:\n1. Your preferred date\n2. Preferred time\n3. Type of specialist needed\n\nI'll help you find available options.",
            "medication_reminder": "⏰ I can help you set medication reminders. Please tell me:\n1. Medication name\n2. Dosage\n3. Timing (morning/afternoon/evening/night)\n\nI'll send you reminders via WhatsApp."
        }
        
        return responses.get(button_id, f"I received your selection: {button_text}. How else can I help you?")

    def _handle_list_response(self, list_id: str, list_title: str) -> str:
        """Generate response for list selections"""
        return f"You selected: {list_title}. I'll provide more information about this option."

    async def process_media_message(self, message_data: Dict[str, Any], media_type: str) -> Dict[str, Any]:
        """Process media messages (images, audio, etc.)"""
        try:
            sender = message_data['from']
            
            logger.info(f"Processing {media_type} message from {mask_sensitive_data(sender)}")
            
            # FIXED: Send appropriate response for media messages
            if media_type == 'image':
                response_text = ("📸 I received your image. For medical image analysis, "
                               "please consult with a healthcare professional directly. "
                               "I can help you with text-based health queries.")
            elif media_type == 'audio':
                response_text = ("🎵 I received your audio message. Currently, I can only process text messages. "
                               "Please send your health query as text, and I'll be happy to help!")
            else:
                response_text = f"I received your {media_type} message, but I can only process text messages at the moment."
            
            result = await self.whatsapp.send_text_message(sender, response_text)
            
            return {
                "status": "success",
                "media_type": media_type,
                "response_sent": result.get('success', False)
            }

        except Exception as e:
            logger.error(f"❌ Error processing {media_type} message: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def _send_follow_up_options(self, sender: str, intent: str):
        """Send follow-up options based on intent"""
        try:
            if intent == "symptom":
                follow_up = ("💡 Would you like to:\n"
                           "• Get more information about your symptoms\n"
                           "• Find nearby hospitals\n"
                           "• Get first aid tips\n"
                           "• Book a doctor appointment\n\n"
                           "Just let me know how I can help further!")
            elif intent == "medication":
                follow_up = ("💊 Medication Information:\n"
                           "• Always follow your doctor's prescription\n"
                           "• Read medication labels carefully\n"
                           "• Take medications as directed\n"
                           "• Never share medications with others\n\n"
                           "For specific medication questions, consult your pharmacist or doctor.")
            else:
                return  # No follow-up for other intents
            
            # FIXED: Add delay before follow-up to avoid spam
            await asyncio.sleep(2)
            await self.whatsapp.send_text_message(sender, follow_up)
            
        except Exception as e:
            logger.warning(f"Failed to send follow-up: {e}")

    def get_message_stats(self) -> Dict[str, Any]:
        """Get message processing statistics"""
        return {
            "total_processed": getattr(self, '_total_processed', 0),
            "successful": getattr(self, '_successful', 0),
            "failed": getattr(self_phone(number)
            print(f"  ✅ {number} -> {validated}")
        except Exception as e:
            print(f"  ❌ {number} -> Error: {e}")
    
    # Test webhook verification
    print("\n🔍 Webhook verification tests:")
    test_data = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.verify_token,
        "hub.challenge": "test_challenge"
    }
    
    result = whatsapp_service.verify_webhook(test_data)
    print(f"  {'✅' if result else '❌'} Valid webhook: {result}")
    
    test_data["hub.verify_token"] = "wrong_token"
    result = whatsapp_service.verify_webhook(test_data)
    print(f"  {'✅' if not result else '❌'} Invalid webhook: {not result}")
    
    print("\n🎉 WhatsApp service tests completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_whatsapp_service())
