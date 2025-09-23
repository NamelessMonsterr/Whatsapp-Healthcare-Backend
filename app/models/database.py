"""
Database models for the healthcare chatbot
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for storing WhatsApp users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    language_preference = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(phone={self.phone_number}, name={self.name})>"

class Conversation(Base):
    """Conversation threads between users and bot"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
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
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.message_id}, sender={self.sender_type})>"

class HealthQuery(Base):
    """Specific health-related queries for analytics"""
    __tablename__ = "health_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), ForeignKey("messages.message_id"), nullable=False)
    category = Column(String(50), nullable=True)  # symptoms, medication, general, emergency
    subcategory = Column(String(50), nullable=True)
    urgency_level = Column(String(20), nullable=True)  # low, medium, high, critical
    symptoms_detected = Column(Text, nullable=True)  # JSON string of symptoms
    conditions_mentioned = Column(Text, nullable=True)  # JSON string of conditions
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    
    def __repr__(self):
        return f"<ModelPerformance(model={self.model_name}, requests={self.request_count})>"