"""
Message Processor Service - FIXED VERSION with Async Support
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
from app.core.security import is_safe_message_content, sanitize_input_string  # FIXED: Added security

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Process incoming WhatsApp messages and generate responses with async support"""

    def __init__(self):
        self.whatsapp = whatsapp_service
        self.healthcare = healthcare_service
        self.db_manager = DatabaseManager()
        logger.info("Message Processor initialized with multilingual support")

    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook data with async support"""
        try:
            # Parse the webhook message
            message_data = self.whatsapp.parse_webhook_message(data)

            if not message_data:
                logger.info("No message data found in webhook")
                return {"status": "no_message"}

            logger.info(f"Processing message: {json.dumps(message_data, indent=2)}")

            # FIXED: Validate message data
            if not self._validate_message_data(message_data):
                return {"status": "invalid_message_data"}

            # Handle different message types
            if message_data['type'] == 'text':
                return await self.process_text_message(message_data)

            elif message_data['type'] == 'interactive':
                return await self.process_interactive_message(message_data)

            elif message_data['type'] == 'image':
                return await self.process_media_message(message_data, 'image')

            elif message_data['type'] == 'audio':
                return await self.process_media_message(message_data, 'audio')

            else:
                # FIXED: Send more helpful response for unsupported types
                await self.whatsapp.send_text_message(
                    message_data['from'],
                    "I can currently process text messages, images, and audio. "
                    "Please send your health query as text for the best experience."
                )
                return {"status": "unsupported_type", "type": message_data['type']}

        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _validate_message_data(self, message_data: Dict[str, Any]) -> bool:
        """Validate message data structure"""
        try:
            required_fields = ['from', 'type', 'message_id']
            for field in required_fields:
                if field not in message_data or not message_data[field]:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate phone number format
            from app.core.security import validate_whatsapp_phone
            validate_whatsapp_phone(message_data['from'])
            
            return True
        except Exception as e:
            logger.error(f"Message validation failed: {e}")
            return False

    async def process_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text message with multilingual support and async database operations"""
        sender = message_data['from']
        text = message_data.get('text', '')
        message_id = message_data['message_id']
        contact_name = message_data.get('contact_name', 'User')

        try:
            # FIXED: Validate message content
            is_safe, reason = is_safe_message_content(text)
            if not is_safe:
                logger.warning(f"Unsafe message content from {sender}: {reason}")
                await self.whatsapp.send_text_message(
                    sender,
                    "I'm sorry, but I cannot process that message. Please rephrase your health query."
                )
                return {"status": "unsafe_content", "reason": reason}

            # Sanitize message content
            text = sanitize_input_string(text, max_length=2000)

            # Mark message as read
            await self.whatsapp.mark_as_read(message_id)

            # FIXED: Use async database operations
            user_language = 'en'  # Default language
            conversation_id = None
            user_id = None

            async with get_db_context() as db:
                # Get or create user
                user = await self.db_manager.create_user(db, sender, contact_name)
                user_id = user.id
                user_language = getattr(user, 'language_preference', 'en')

                # Get or create conversation
                conversation = await self.db_manager.get_or_create_active_conversation(db, user.id)
                conversation_id = conversation.id

                # Save incoming message
                await self.db_manager.save_message(
                    db,
                    conversation_id,
                    message_id,
                    'user',
                    text,
                    message_type='text'
                )

            # Process with multilingual healthcare service
            logger.info(f"Processing health query: {text[:100]}...")

            # Detect language automatically
            detected_language = self.healthcare.detect_language(text)
            logger.info(f"Detected language: {detected_language}")

            # Process with AI models using the detected language
            response = self.healthcare.process_healthcare_query(text, detected_language)

            # Log successful AI processing
            logger.info(f"AI processing successful - Intent: {response.intent}, Confidence: {response.confidence:.3f}")

            # Handle emergency cases with special formatting
            if response.intent == "emergency":
                # Send emergency response with buttons
                buttons = [
                    {"id": "call_emergency", "title": "Call 108"},
                    {"id": "find_hospital", "title": "Find Hospital"},
                    {"id": "first_aid", "title": "First Aid Tips"}
                ]

                result = await self.whatsapp.send_interactive_message(
                    sender,
                    response.answer,
                    buttons
                )
            else:
                # Send regular text response
                result = await self.whatsapp.send_text_message(sender, response.answer)

            # FIXED: Save bot response to database with error handling
            if result.get('success'):
                try:
                    bot_message_id = result.get('data', {}).get('messages', [{}])[0].get('id', str(uuid.uuid4()))
                    
                    async with get_db_context() as db:
                        # Save bot message
                        await self.db_manager.save_message(
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
                        await self.db_manager.update_message_ml_data(
                            db,
                            message_id,
                            detected_language=response.language,
                            detected_intent=response.intent
                        )
                except Exception as db_error:
                    logger.error(f"Error saving bot response to database: {db_error}")
                    # Continue even if DB save fails

            # Send follow-up options for certain intents
            if response.intent in ["symptom", "medication"] and result.get('success'):
                await self._send_follow_up_options(sender, response.intent)

            return {
                "status": "success",
                "intent": response.intent,
                "confidence": response.confidence,
                "response_sent": result.get('success', False),
                "language": response.language,
                "model_used": response.model_used,
                "processing_time": response.processing_time
            }

        except Exception as e:
            logger.error(f"Error processing text message: {e}", exc_info=True)
            
            # FIXED: Send user-friendly error message
            error_message = (
                "I apologize, but I'm having trouble processing your message. "
                "Please try rephrasing your health query, or contact support if the issue persists."
            )
            
            try:
                await self.whatsapp.send_text_message(sender, error_message)
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")

            return {"status": "error", "error": str(e)}

    async def process_interactive_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process interactive message (button clicks, etc.)"""
        try:
            sender = message_data['from']
            interactive_data = message_data.get('interactive', {})
            message_id = message_data['message_id']
            
            # Extract interactive response
            if interactive_data.get('type') == 'button_reply':
                button_id = interactive_data.get('button_reply', {}).get('id')
                button_text = interactive_data.get('button_reply', {}).get('title')
                
                logger.info(f"Interactive button clicked: {button_id} - {button_text}")
                
                # Handle different button actions
                if button_id == 'call_emergency':
                    response = "🚨 Please call 108 for immediate emergency assistance. Stay calm and provide your location clearly."
                elif button_id == 'find_hospital':
                    response = "🏥 Finding nearby hospitals... Please share your location for accurate results."
                elif button_id == 'first_aid':
                    response = "🩹 Basic first aid tips: 1) Stay calm 2) Ensure safety 3) Call for help 4) Don't move injured person unless necessary"
                else:
                    response = f"You selected: {button_text}. How can I help you with this?"
                
                await self.whatsapp.send_text_message(sender, response)
                
                return {
                    "status": "success",
                    "type": "interactive",
                    "button_id": button_id,
                    "button_text": button_text
                }
            
            return {"status": "unsupported_interactive"}

        except Exception as e:
            logger.error(f"Error processing interactive message: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def process_media_message(self, message_data: Dict[str, Any], media_type: str) -> Dict[str, Any]:
        """Process media messages (images, audio)"""
        try:
            sender = message_data['from']
            message_id = message_data['message_id']
            
            # Mark as read
            await self.whatsapp.mark_as_read(message_id)
            
            # For now, acknowledge receipt and explain limitations
            if media_type == 'image':
                response = (
                    "📸 I received your image. Currently, I can only analyze text messages for health queries. "
                    "Please describe your symptoms or health concern in text, and I'll be happy to help!"
                )
            elif media_type == 'audio':
                response = (
                    "🎤 I received your voice message. Currently, I can only process text messages for health queries. "
                    "Please type your health question, and I'll provide assistance right away!"
                )
            else:
                response = (
                    "📎 I received your file. Currently, I can only process text messages for health queries. "
                    "Please type your health question, and I'll help you immediately!"
                )
            
            await self.whatsapp.send_text_message(sender, response)
            
            return {
                "status": "success",
                "type": media_type,
                "message": "Media acknowledged, text response sent"
            }

        except Exception as e:
            logger.error(f"Error processing {media_type} message: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def _send_follow_up_options(self, sender: str, intent: str):
        """Send follow-up options based on intent"""
        try:
            if intent == "symptom":
                follow_up = (
                    "🩺 Would you like more information about:\n"
                    "• Home remedies\n"
                    "• When to see a doctor\n"
                    "• Related symptoms to watch for\n"
                    "• Prevention tips\n\n"
                    "Just let me know what you'd like to know more about!"
                )
            elif intent == "medication":
                follow_up = (
                    "💊 For medication information, I recommend:\n"
                    "• Always follow your doctor's prescription\n"
                    "• Read medication labels carefully\n"
                    "• Ask your pharmacist about side effects\n"
                    "• Never self-medicate for serious conditions\n\n"
                    "Would you like information about drug interactions or side effects?"
                )
            else:
                return

            await self.whatsapp.send_text_message(sender, follow_up)
            
        except Exception as e:
            logger.error(f"Error sending follow-up options: {e}")

# FIXED: Create service instance
message_processor = MessageProcessor()
