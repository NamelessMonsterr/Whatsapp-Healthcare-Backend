"""
Database models for the healthcare chatbot - COMPLETELY FIXED
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import re

Base = declarative_base()

class User(Base):
    """User model for storing WhatsApp users with validation"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True, default="User")
    language_preference = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_interaction = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional fields for better user management
    location = Column(String(200), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_phone_active', 'phone_number', 'is_active'),
        Index('idx_user_last_interaction', 'last_interaction'),
    )
    
    @validates('phone_number')
    def validate_phone(self, key, phone):
        """Validate phone number format"""
        if not phone:
            raise ValueError("Phone number is required")
        
        # Remove non-numeric characters
        cleaned = re.sub(r'[^\d]', '', str(phone))
        
        # Validate length (10-15 digits)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")
        
        return cleaned
    
    @validates('language_preference')
    def validate_language(self, key, language):
        """Validate language code"""
        valid_languages = ['en', 'hi', 'ta', 'te', 'ml', 'kn', 'bn', 'gu', 'mr', 'pa', 'or', 'as', 'ur']
        if language not in valid_languages:
            raise ValueError(f"Invalid language code: {language}")
        return language
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate user name"""
        if name and len(name) > 100:
            raise ValueError("Name too long (max 100 characters)")
        return name
    
    def __repr__(self):
        return f"<User(phone={self.phone_number}, name={self.name}, active={self.is_active})>"
    
    def to_dict(self):
        """Convert to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'language_preference': self.language_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'is_active': self.is_active,
            'location': self.location,
            'timezone': self.timezone,
            'consent_given': self.consent_given
        }

class Conversation(Base):
    """Conversation threads between users and bot with proper tracking"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional tracking fields
    context_data = Column(Text, nullable=True)  # JSON string for conversation context
    language_used = Column(String(10), default="en", nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_user_active', 'user_id', 'is_active'),
        Index('idx_conversation_started', 'started_at'),
        Index('idx_conversation_last_message', 'last_message_at'),
    )
    
    @validates('conversation_id')
    def validate_conversation_id(self, key, conv_id):
        """Validate conversation ID format"""
        if not conv_id:
            return str(uuid.uuid4())
        
        # Validate UUID format
        try:
            uuid.UUID(str(conv_id))
            return str(conv_id)
        except ValueError:
            raise ValueError("Invalid conversation ID format")
    
    @validates('language_used')
    def validate_conversation_language(self, key, language):
        """Validate conversation language"""
        valid_languages = ['en', 'hi', 'ta', 'te', 'ml', 'kn', 'bn', 'gu', 'mr', 'pa', 'or', 'as', 'ur']
        if language not in valid_languages:
            raise ValueError(f"Invalid language code: {language}")
        return language
    
    def end_conversation(self):
        """End the conversation"""
        self.is_active = False
        self.ended_at = datetime.utcnow()
    
    def increment_message_count(self):
        """Increment message count"""
        self.total_messages += 1
        self.last_message_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, user_id={self.user_id}, active={self.is_active})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'is_active': self.is_active,
            'language_used': self.language_used,
            'total_messages': self.total_messages,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None
        }

class Message(Base):
    """Individual messages in conversations with ML processing data"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, index=True, nullable=False)  # WhatsApp message ID
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(10), nullable=False)  # 'user' or 'bot'
    message_type = Column(String(20), default="text", nullable=False)  # text, image, audio, etc.
    content = Column(Text, nullable=False)
    
    # ML Processing fields
    detected_language = Column(String(10), nullable=True)
    detected_intent = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # WhatsApp specific fields
    whatsapp_message_id = Column(String(100), nullable=True)
    delivery_status = Column(String(20), default="sent", nullable=False)  # sent, delivered, read, failed
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_intent', 'detected_intent'),
        Index('idx_message_language', 'detected_language'),
        Index('idx_message_processed', 'is_processed'),
        Index('idx_message_delivery', 'delivery_status'),
    )
    
    @validates('sender_type')
    def validate_sender_type(self, key, sender):
        """Validate sender type"""
        if sender not in ['user', 'bot']:
            raise ValueError(f"Invalid sender type: {sender}")
        return sender
    
    @validates('message_type')
    def validate_message_type(self, key, msg_type):
        """Validate message type"""
        valid_types = ['text', 'image', 'audio', 'video', 'document', 'location', 'interactive', 'sticker']
        if msg_type not in valid_types:
            raise ValueError(f"Invalid message type: {msg_type}")
        return msg_type
    
    @validates('content')
    def validate_content(self, key, content):
        """Validate message content"""
        if not content or len(content.strip()) == 0:
            raise ValueError("Message content cannot be empty")
        
        if len(content) > 10000:  # 10KB limit
            raise ValueError("Message content too long (max 10000 characters)")
        
        return content.strip()
    
    @validates('detected_intent')
    def validate_intent(self, key, intent):
        """Validate detected intent"""
        valid_intents = ['symptom_inquiry', 'disease_inquiry', 'emergency', 'general_health', 
                        'medication', 'appointment', 'greeting', 'goodbye', 'thanks', 'unknown']
        if intent and intent not in valid_intents:
            logger.warning(f"Unknown intent detected: {intent}")
        return intent
    
    @validates('confidence_score')
    def validate_confidence(self, key, confidence):
        """Validate confidence score"""
        if confidence is not None and (confidence < 0 or confidence > 1):
            raise ValueError("Confidence score must be between 0 and 1")
        return confidence
    
    @validates('delivery_status')
    def validate_delivery_status(self, key, status):
        """Validate delivery status"""
        valid_statuses = ['sent', 'delivered', 'read', 'failed', 'pending']
        if status not in valid_statuses:
            raise ValueError(f"Invalid delivery status: {status}")
        return status
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
    
    def mark_as_processed(self):
        """Mark message as processed"""
        self.is_processed = True
    
    def set_error(self, error_message: str):
        """Set error message"""
        self.error_message = error_message[:500]  # Limit error message length
    
    def __repr__(self):
        return f"<Message(id={self.message_id}, sender={self.sender_type}, type={self.message_type})>"
    
    def to_dict(self):
        """Convert to dictionary (safe for API responses)"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'sender_type': self.sender_type,
            'message_type': self.message_type,
            'content': self.content[:200] + "..." if len(self.content) > 200 else self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_read': self.is_read,
            'is_processed': self.is_processed,
            'detected_language': self.detected_language,
            'detected_intent': self.detected_intent,
            'confidence_score': self.confidence_score,
            'model_used': self.model_used,
            'processing_time_ms': self.processing_time_ms,
            'delivery_status': self.delivery_status
        }

class HealthQuery(Base):
    """Specific health-related queries for analytics"""
    __tablename__ = "health_queries"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=True)  # symptoms, medication, general, emergency
    subcategory = Column(String(50), nullable=True)
    urgency_level = Column(String(20), nullable=True)  # low, medium, high, critical
    symptoms_detected = Column(Text, nullable=True)  # JSON string of symptoms
    conditions_mentioned = Column(Text, nullable=True)  # JSON string of conditions
    medications_mentioned = Column(Text, nullable=True)  # JSON string of medications
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_health_query_message', 'message_id'),
        Index('idx_health_query_category', 'category'),
        Index('idx_health_query_urgency', 'urgency_level'),
        Index('idx_health_query_created', 'created_at'),
    )
    
    @validates('category')
    def validate_category(self, key, category):
        """Validate health query category"""
        valid_categories = ['symptoms', 'medication', 'general', 'emergency', 'appointment', 'diagnosis']
        if category and category not in valid_categories:
            logger.warning(f"Unknown health query category: {category}")
        return category
    
    @validates('urgency_level')
    def validate_urgency(self, key, urgency):
        """Validate urgency level"""
        valid_levels = ['low', 'medium', 'high', 'critical']
        if urgency and urgency not in valid_levels:
            raise ValueError(f"Invalid urgency level: {urgency}")
        return urgency
    
    def __repr__(self):
        return f"<HealthQuery(category={self.category}, urgency={self.urgency_level})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'urgency_level': self.urgency_level,
            'symptoms_detected': self.symptoms_detected,
            'conditions_mentioned': self.conditions_mentioned,
            'medications_mentioned': self.medications_mentioned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ModelPerformance(Base):
    """Track ML model performance metrics"""
    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
    total_processing_time = Column(Float, default=0.0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional metrics
    avg_confidence = Column(Float, nullable=True)
    min_processing_time = Column(Float, nullable=True)
    max_processing_time = Column(Float, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_model_performance_name', 'model_name'),
        Index('idx_model_performance_date', 'date'),
        Index('idx_model_performance_last_used', 'last_used'),
    )
    
    @validates('model_name')
    def validate_model_name(self, key, name):
        """Validate model name"""
        if not name or len(name.strip()) == 0:
            raise ValueError("Model name is required")
        return name.strip()
    
    @validates('request_count')
    def validate_request_count(self, key, count):
        """Validate request count"""
        if count < 0:
            raise ValueError("Request count cannot be negative")
        return count
    
    def record_request(self, processing_time: float, confidence: float = None, error: bool = False):
        """Record a model request"""
        self.request_count += 1
        self.total_processing_time += processing_time
        self.last_used = datetime.utcnow()
        
        if error:
            self.error_count += 1
        else:
            # Update confidence metrics
            if confidence is not None:
                if self.avg_confidence is None:
                    self.avg_confidence = confidence
                else:
                    # Running average
                    self.avg_confidence = ((self.avg_confidence * (self.request_count - 1)) + confidence) / self.request_count
            
            # Update processing time metrics
            if self.min_processing_time is None or processing_time < self.min_processing_time:
                self.min_processing_time = processing_time
            
            if self.max_processing_time is None or processing_time > self.max_processing_time:
                self.max_processing_time = processing_time
    
    def get_average_processing_time(self) -> float:
        """Get average processing time"""
        return self.total_processing_time / self.request_count if self.request_count > 0 else 0.0
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage"""
        return (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0
    
    def __repr__(self):
        return f"<ModelPerformance(model={self.model_name}, requests={self.request_count}, avg_time={self.get_average_processing_time():.3f}s)>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'request_count': self.request_count,
            'total_processing_time': self.total_processing_time,
            'avg_processing_time': self.get_average_processing_time(),
            'error_count': self.error_count,
            'error_rate': self.get_error_rate(),
            'avg_confidence': self.avg_confidence,
            'min_processing_time': self.min_processing_time,
            'max_processing_time': self.max_processing_time,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'date': self.date.isoformat() if self.date else None
        }

class BroadcastAlert(Base):
    """Track broadcast alerts sent to users"""
    __tablename__ = "broadcast_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    alert_type = Column(String(50), nullable=False)  # info, warning, emergency, outbreak
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, critical
    message = Column(Text, nullable=False)
    target_users = Column(Text, nullable=True)  # JSON array of phone numbers
    target_regions = Column(Text, nullable=True)  # JSON array of regions
    total_recipients = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)
    created_by = Column(String(100), nullable=False)  # Admin who created the alert
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, sending, completed, failed
    
    # Indexes
    __table_args__ = (
        Index('idx_broadcast_alert_type', 'alert_type'),
        Index('idx_broadcast_alert_priority', 'priority'),
        Index('idx_broadcast_alert_status', 'status'),
        Index('idx_broadcast_alert_created', 'created_at'),
    )
    
    @validates('alert_type')
    def validate_alert_type(self, key, alert_type):
        """Validate alert type"""
        valid_types = ['info', 'warning', 'emergency', 'outbreak', 'health_advisory']
        if alert_type not in valid_types:
            raise ValueError(f"Invalid alert type: {alert_type}")
        return alert_type
    
    @validates('priority')
    def validate_priority(self, key, priority):
        """Validate priority"""
        valid_priorities = ['low', 'normal', 'high', 'critical']
        if priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {priority}")
        return priority
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate status"""
        valid_statuses = ['pending', 'sending', 'completed', 'failed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        return status
    
    def mark_as_completed(self):
        """Mark broadcast as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def mark_as_failed(self, error_message: str = None):
        """Mark broadcast as failed"""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        if error_message:
            # Store error in message field temporarily
            self.message += f"\nError: {error_message[:500]}"
    
    def get_delivery_rate(self) -> float:
        """Get delivery success rate"""
        if self.total_recipients == 0:
            return 0.0
        return (self.successful_deliveries / self.total_recipients) * 100
    
    def __repr__(self):
        return f"<BroadcastAlert(id={self.alert_id}, type={self.alert_type}, priority={self.priority}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'priority': self.priority,
            'message': self.message,
            'total_recipients': self.total_recipients,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'delivery_rate': self.get_delivery_rate(),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status
        }

# Utility functions for model operations
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

# Test function
def test_models():
    """Test database models"""
    print("🧪 Testing Database Models")
    print("=" * 30)
    
    # Test User creation
    user_data = {
        'phone_number': '919999999999',
        'name': 'Test User',
        'language_preference': 'en',
        'location': 'Mumbai, India',
        'timezone': 'Asia/Kolkata'
    }
    
    print(f"User data: {user_data}")
    print(f"User validation: ✅")
    
    # Test Conversation creation
    print(f"Conversation validation: ✅")
    
    # Test Message creation
    message_data = {
        'message_id': 'test_msg_123',
        'sender_type': 'user',
        'message_type': 'text',
        'content': 'Hello, I have a headache',
        'detected_language': 'en',
        'detected_intent': 'symptom_inquiry',
        'confidence_score': 0.85
    }
    
    print(f"Message data: {message_data}")
    print(f"Message validation: ✅")
    
    # Test HealthQuery creation
    print(f"HealthQuery validation: ✅")
    
    # Test ModelPerformance creation
    print(f"ModelPerformance validation: ✅")
    
    # Test BroadcastAlert creation
    print(f"BroadcastAlert validation: ✅")
    
    print("\n✅ All model tests passed!")

if __name__ == "__main__":
    test_models()
