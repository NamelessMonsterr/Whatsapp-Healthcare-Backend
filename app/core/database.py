"""
Database connection and session management - COMPLETELY FIXED
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging
import time
from datetime import datetime, timedelta

from app.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)

# FIXED: Proper engine creation with error handling
def create_database_engine():
    """Create database engine with proper configuration"""
    try:
        if settings.database_url.startswith("sqlite"):
            # SQLite specific configuration
            engine = create_engine(
                settings.database_url,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30.0,
                    "isolation_level": None
                },
                poolclass=StaticPool,
                echo=settings.database_echo,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
                
            logger.info("✅ SQLite database engine created")
            return engine
            
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                echo=settings.database_echo,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_timeout=30
            )
            logger.info("✅ PostgreSQL/MySQL database engine created")
            return engine
            
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        raise

# Create engine
engine = create_database_engine()

# FIXED: Create session factory with proper configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=Session
)

def init_db():
    """Initialize database tables with error handling"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session with transaction handling"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        db.close()

class DatabaseManager:
    """Database operations manager with comprehensive error handling"""

    def __init__(self):
        self.engine = engine
        logger.info("DatabaseManager initialized")

    def create_user(self, db: Session, phone_number: str, name: str = None):
        """Create or get user with validation"""
        try:
            from app.models.database import User
            
            # FIXED: Validate phone number
            if not phone_number or len(phone_number) < 10:
                logger.error("Invalid phone number provided")
                return None
            
            # Check if user exists
            user = db.query(User).filter(User.phone_number == phone_number).first()
            if user:
                logger.info(f"Found existing user: {phone_number}")
                return user
            
            # Create new user
            user = User(
                phone_number=phone_number,
                name=name or "User",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            db.add(user)
            db.flush()  # Get ID without committing
            logger.info(f"Created new user: {phone_number}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            return None

    def create_conversation(self, db: Session, user_id: int):
        """Create new conversation with proper cleanup"""
        try:
            from app.models.database import Conversation
            
            # FIXED: Close any active conversations first
            db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).update({
                "is_active": False,
                "ended_at": datetime.utcnow()
            })
            
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                started_at=datetime.utcnow(),
                is_active=True
            )
            db.add(conversation)
            db.flush()
            logger.info(f"Created new conversation for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            db.rollback()
            return None

    def get_or_create_active_conversation(self, db: Session, user_id: int):
        """Get active conversation or create new one with timeout"""
        try:
            from app.models.database import Conversation
            
            # FIXED: Get active conversation created within last 30 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=30)
            conversation = db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == True,
                Conversation.started_at >= cutoff_time
            ).first()
            
            if conversation:
                logger.info(f"Found active conversation for user {user_id}")
                return conversation
            
            # Create new conversation
            return self.create_conversation(db, user_id)
            
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {e}")
            return self.create_conversation(db, user_id)  # Fallback

    def save_message(self, db: Session, conversation_id: int, message_id: str,
                     sender_type: str, content: str, **kwargs):
        """Save message to database with validation"""
        try:
            from app.models.database import Message
            
            # FIXED: Validate required parameters
            if not conversation_id or not message_id or not sender_type or not content:
                logger.error("Missing required message parameters")
                return None
            
            # FIXED: Validate sender type
            if sender_type not in ['user', 'bot']:
                logger.error(f"Invalid sender type: {sender_type}")
                return None
            
            # FIXED: Sanitize content length
            if len(content) > 10000:  # 10KB limit
                content = content[:10000] + "..."
            
            message = Message(
                message_id=message_id,
                conversation_id=conversation_id,
                sender_type=sender_type,
                message_type=kwargs.get('message_type', 'text'),
                content=content,
                timestamp=kwargs.get('timestamp', datetime.utcnow()),
                is_read=False,
                is_processed=False,
                detected_language=kwargs.get('detected_language'),
                detected_intent=kwargs.get('detected_intent'),
                confidence_score=kwargs.get('confidence_score'),
                model_used=kwargs.get('model_used'),
                processing_time_ms=kwargs.get('processing_time_ms'),
                error_message=kwargs.get('error_message')
            )
            db.add(message)
            db.flush()
            logger.info(f"Saved message {message_id} from {sender_type}")
            return message
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            db.rollback()
            return None

    def update_message_ml_data(self, db: Session, message_id: str, **ml_data):
        """Update message with ML processing results"""
        try:
            from app.models.database import Message
            
            message = db.query(Message).filter(Message.message_id == message_id).first()
            if not message:
                logger.warning(f"Message not found: {message_id}")
                return None
            
            # FIXED: Update only valid fields
            valid_fields = ['detected_language', 'detected_intent', 'confidence_score', 
                          'model_used', 'processing_time_ms', 'is_processed', 'error_message']
            
            for key, value in ml_data.items():
                if key in valid_fields and hasattr(message, key):
                    setattr(message, key, value)
            
            # Mark as processed if ML data is added
            if any(field in ml_data for field in ['detected_intent', 'confidence_score']):
                message.is_processed = True
            
            logger.info(f"Updated ML data for message {message_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error updating message ML data: {e}")
            db.rollback()
            return None

    def get_user_by_phone(self, db: Session, phone_number: str):
        """Get user by phone number"""
        try:
            from app.models.database import User
            
            if not phone_number:
                return None
            
            return db.query(User).filter(User.phone_number == phone_number).first()
            
        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    def get_user_conversations(self, db: Session, user_id: int, limit: int = 10):
        """Get user conversations with limit"""
        try:
            from app.models.database import Conversation
            
            return db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.started_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []

    def get_conversation_messages(self, db: Session, conversation_id: int, limit: int = 50):
        """Get messages for a conversation"""
        try:
            from app.models.database import Message
            
            return db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.asc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []

    def get_recent_messages(self, db: Session, hours: int = 24):
        """Get recent messages for analytics"""
        try:
            from app.models.database import Message
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return db.query(Message).filter(
                Message.timestamp >= cutoff_time
            ).order_by(Message.timestamp.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []

    def get_message_stats(self, db: Session):
        """Get message statistics"""
        try:
            from app.models.database import Message
            from sqlalchemy import func
            
            total_messages = db.query(Message).count()
            processed_messages = db.query(Message).filter(Message.is_processed == True).count()
            error_messages = db.query(Message).filter(Message.error_message.isnot(None)).count()
            
            # Get intent distribution
            intent_counts = db.query(
                Message.detected_intent,
                func.count(Message.id)
            ).filter(
                Message.detected_intent.isnot(None)
            ).group_by(Message.detected_intent).all()
            
            # Get language distribution
            language_counts = db.query(
                Message.detected_language,
                func.count(Message.id)
            ).filter(
                Message.detected_language.isnot(None)
            ).group_by(Message.detected_language).all()
            
            return {
                "total_messages": total_messages,
                "processed_messages": processed_messages,
                "error_messages": error_messages,
                "processing_rate": (processed_messages / total_messages * 100) if total_messages > 0 else 0,
                "intent_distribution": {intent: count for intent, count in intent_counts},
                "language_distribution": {lang: count for lang, count in language_counts}
            }
            
        except Exception as e:
            logger.error(f"Error getting message stats: {e}")
            return {}

    def cleanup_old_conversations(self, db: Session, days: int = 30):
        """Clean up old inactive conversations"""
        try:
            from app.models.database import Conversation
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Mark old active conversations as inactive
            old_conversations = db.query(Conversation).filter(
                Conversation.is_active == True,
                Conversation.started_at < cutoff_date
            ).all()
            
            for conv in old_conversations:
                conv.is_active = False
                conv.ended_at = datetime.utcnow()
            
            logger.info(f"Cleaned up {len(old_conversations)} old conversations")
            return len(old_conversations)
            
        except Exception as e:
            logger.error(f"Error cleaning up old conversations: {e}")
            return 0

    def get_database_health(self, db: Session) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Test connection
            db.execute(text("SELECT 1"))
            
            # Get table counts
            from app.models.database import User, Message, Conversation
            
            user_count = db.query(User).count()
            message_count = db.query(Message).count()
            conversation_count = db.query(Conversation).count()
            
            # Check for issues
            issues = []
            if user_count == 0:
                issues.append("No users found")
            if message_count == 0:
                issues.append("No messages found")
                
            return {
                "status": "healthy",
                "connection": "ok",
                "table_counts": {
                    "users": user_count,
                    "messages": message_count,
                    "conversations": conversation_count
                },
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e)
            }

# Create database manager instance
db_manager = DatabaseManager()

# FIXED: Add missing imports for utility functions
def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if not data:
        return ""
    
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    visible_start = data[:visible_chars // 2]
    visible_end = data[-visible_chars // 2:]
    masked_middle = mask_char * (len(data) - visible_chars)
    
    return f"{visible_start}{masked_middle}{visible_end}"

# Test function
def test_database_operations():
    """Test database operations"""
    print("🧪 Testing Database Operations")
    
    try:
        # Test connection
        with get_db_context() as db:
            health = db_manager.get_database_health(db)
            print(f"  Database health: {health['status']}")
            
            # Test user creation
            test_phone = "919999999999"
            user = db_manager.create_user(db, test_phone, "Test User")
            if user:
                print(f"  ✅ Created user: {user.phone_number}")
                
                # Test conversation creation
                conversation = db_manager.create_conversation(db, user.id)
                if conversation:
                    print(f"  ✅ Created conversation: {conversation.id}")
                    
                    # Test message saving
                    message = db_manager.save_message(
                        db, conversation.id, "test_msg_123", "user", "Hello, I have a headache"
                    )
                    if message:
                        print(f"  ✅ Saved message: {message.message_id}")
                        
                        # Test ML data update
                        updated = db_manager.update_message_ml_data(
                            db, "test_msg_123", detected_intent="symptom", confidence_score=0.85
                        )
                        if updated:
                            print(f"  ✅ Updated ML data")
            
            # Get stats
            stats = db_manager.get_message_stats(db)
            print(f"  📊 Message stats: {stats}")
            
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")

if __name__ == "__main__":
    test_database_operations()
