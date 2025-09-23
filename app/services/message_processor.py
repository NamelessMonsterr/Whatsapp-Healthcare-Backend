"""
Message Processor Service - Updated for Multilingual Support
"""
import logging
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime
import re

from app.services.whatsapp import whatsapp_service
from app.ml.healthcare_models import healthcare_service  # ✅ Use multilingual service
from app.core.database import DatabaseManager, get_db_context
from app.config import settings

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Process incoming WhatsApp messages and generate responses"""
    
    def __init__(self):
        self.whatsapp = whatsapp_service
        self.healthcare = healthcare_service  # ✅ Multilingual healthcare service
        self.db_manager = DatabaseManager()
        logger.info("Message Processor initialized with multilingual support")
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook data"""
        try:
            # Parse the webhook message
            message_data = self.whatsapp.parse_webhook_message(data)
            
            if not message_data:
                logger.info("No message data found in webhook")
                return {"status": "no_message"}
            
            logger.info(f"Processing message: {json.dumps(message_data, indent=2)}")
            
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
                # Send a default response for unsupported message types
                await self.whatsapp.send_text_message(
                    message_data['from'],
                    "I can currently only process text messages. Please send your health query as text."
                )
                return {"status": "unsupported_type", "type": message_data['type']}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def process_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text message with multilingual support"""
        sender = message_data['from']
        text = message_data.get('text', '')
        message_id = message_data['message_id']
        contact_name = message_data.get('contact_name', 'User')
        
        try:
            # Mark message as read
            await self.whatsapp.mark_as_read(message_id)
            
            # Save to database and extract needed data
            user_language = 'en'  # Default language
            conversation_id = None  # Store conversation ID
            
            with get_db_context() as db:
                # Get or create user
                user = self.db_manager.create_user(db, sender, contact_name)
                
                # Extract user language preference WITHIN the session
                user_language = getattr(user, 'language_preference', 'en')
                
                # Get or create conversation
                conversation = self.db_manager.get_or_create_active_conversation(db, user.id)
                
                # Store conversation ID for later use
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
            
            # ✅ Process with multilingual healthcare service
            logger.info(f"Processing health query: {text}")
            
            # Detect language automatically
            detected_language = self.healthcare.detect_language(text)
            logger.info(f"Detected language: {detected_language}")
            
            # Process with AI models using the detected language
            response = self.healthcare.process_healthcare_query(text, detected_language)
            
            # Log successful AI processing
            logger.info(f"AI processing successful - Intent: {response.intent}, Confidence: {response.confidence}")
            
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
            
            # Save bot response to database in a NEW session
            if result.get('success'):
                with get_db_context() as db:
                    bot_message_id = result.get('data', {}).get('messages', [{}])[0].get('id', str(uuid.uuid4()))
                    
                    # Save bot message using the stored conversation_id
                    bot_message = self.db_manager.save_message(
                        db,
                        conversation_id,  # Use the stored conversation_id
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
            
            # Send follow-up options for certain intents
            if response.intent in ["symptom", "medication"] and result.get('success'):
                await self._send_follow_up_options(sender, response.intent)
            
            return {
                "status": "success",
                "intent": response.intent,
                "confidence": response.confidence,
                "response_sent": result.get('success', False),
                "language": response.language,
                "model_used": response.model_used
            }
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}", exc_info=True)
            
            # Send error message to user
            await self.whatsapp.send_text_message(
                sender,
                "I apologize, but I'm having trouble processing your message. Please try again or contact support if the issue persists."
            )
            
            return {"status": "error", "error": str(e)}
    
    # ... rest of your existing methods ...

# Create service instance
message_processor = MessageProcessor()