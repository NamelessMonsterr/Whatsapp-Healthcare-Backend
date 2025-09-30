"""
Database models for the healthcare chatbot - FIXED VERSION
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

Base = declarative_base()

class User(Base):
    """User model for storing WhatsApp users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    language_preference = Column(String(10), default="en")
    location = Column(String(200), nullable=True)  # FIXED: Added missing location column
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_interaction = Column(DateTime, default=datetime.utcnow)  # FIXED: Added for recent users query

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(phone={self.phone_number}, name={self.name})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "name": self.name,
            "language_preference": self.language_preference,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "is_active": self.is_active
        }

class Conversation(Base):
    """Conversation threads between users and bot"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    context_data = Column(JSON, nullable=True)  # FIXED: Added for storing conversation context

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, user_id={self.user_id})>"

class Message(Base):
    """Individual messages in conversations"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, index=True)  # WhatsApp message ID
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(10), nullable=False)  # 'user' or 'bot'
    message_type = Column(String(20), default="text")  # text, image, audio, etc.
    content = Column(Text, nullable=False)
    content_length = Column(Integer, default=0)  # FIXED: Added for analytics

    # ML Processing fields
    detected_language = Column(String(10), nullable=True)
    detected_intent = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    processing_time_ms = Column(Float, nullable=True)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)  # FIXED: Added for failed message handling

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.message_id}, sender={self.sender_type})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "sender_type": self.sender_type,
            "message_type": self.message_type,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "detected_language": self.detected_language,
            "detected_intent": self.detected_intent,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_processed": self.is_processed
        }

class HealthQuery(Base):
    """Specific health-related queries for analytics"""
    __tablename__ = "health_queries"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), ForeignKey("messages.message_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # FIXED: Added user reference
    category = Column(String(50), nullable=True)  # symptoms, medication, general, emergency
    subcategory = Column(String(50), nullable=True)
    urgency_level = Column(String(20), nullable=True)  # low, medium, high, critical
    symptoms_detected = Column(Text, nullable=True)  # JSON string of symptoms
    conditions_mentioned = Column(Text, nullable=True)  # JSON string of conditions
    created_at = Column(DateTime, default=datetime.utcnow)
    response_sent = Column(Boolean, default=False)  # FIXED: Added to track if response was sent

    # Relationships
    message = relationship("Message")
    user = relationship("User")

    def __repr__(self):
        return f"<HealthQuery(category={self.category}, urgency={self.urgency_level})>"

class ModelPerformance(Base):
    """Track ML model performance metrics"""
    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    request_count = Column(Integer, default=0)
    total_processing_time = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    last_used = Column(DateTime, default=datetime.utcnow)
    date = Column(DateTime, default=datetime.utcnow)
    average_confidence = Column(Float, default=0.0)  # FIXED: Added for model quality tracking
    model_version = Column(String(50), nullable=True)  # FIXED: Added for model versioning

    def __repr__(self):
        return f"<ModelPerformance(model={self.model_name}, requests={self.request_count})>"
    
    def to_dict(self):
        return {
            "model_name": self.model_name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "average_confidence": self.average_confidence,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100
        }

# FIXED: Added BroadcastAlert model for tracking admin alerts
class BroadcastAlert(Base):
    """Track broadcast alerts sent to users"""
    __tablename__ = "broadcast_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    alert_type = Column(String(50), nullable=False)  # outbreak, emergency, health_advisory, info
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    target_users_count = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    created_by = Column(String(100), nullable=False)  # admin identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    target_regions = Column(Text, nullable=True)  # JSON array of regions
    failed_numbers = Column(Text, nullable=True)  # JSON array of failed numbers

    def __repr__(self):
        return f"<BroadcastAlert(type={self.alert_type}, priority={self.priority})>"
    
    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "message": self.message[:100] + "..." if len(self.message) > 100 else self.message,
            "priority": self.priority,
            "target_users_count": self.target_users_count,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries,
            "success_rate": (self.successful_deliveries / max(self.target_users_count, 1)) * 100,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
