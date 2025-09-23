"""
Database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session  # ✅ FIXED: Added Session import
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)

# Create engine with SQLite specific configurations
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.database_echo
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.database_echo
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

class DatabaseManager:
    """Database operations manager"""
    
    @staticmethod
    def create_user(db: Session, phone_number: str, name: str = None):
        """Create or get user"""
        from app.models.database import User
        
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {phone_number}")
        return user
    
    @staticmethod
    def create_conversation(db: Session, user_id: int):
        """Create new conversation"""
        from app.models.database import Conversation
        
        # Close any active conversations
        db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_active == True
        ).update({"is_active": False})
        
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Created new conversation for user {user_id}")
        return conversation
    
    @staticmethod
    def get_or_create_active_conversation(db: Session, user_id: int):
        """Get active conversation or create new one"""
        from app.models.database import Conversation
        from datetime import datetime, timedelta
        
        # Get active conversation created within last 30 minutes
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_active == True,
            Conversation.started_at >= datetime.utcnow() - timedelta(minutes=30)
        ).first()
        
        if not conversation:
            conversation = DatabaseManager.create_conversation(db, user_id)
        
        return conversation
    
    @staticmethod
    def save_message(db: Session, conversation_id: int, message_id: str, 
                     sender_type: str, content: str, **kwargs):
        """Save message to database"""
        from app.models.database import Message
        
        message = Message(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            **kwargs
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.info(f"Saved message {message_id} from {sender_type}")
        return message
    
    @staticmethod
    def update_message_ml_data(db: Session, message_id: str, **ml_data):
        """Update message with ML processing results"""
        from app.models.database import Message
        
        message = db.query(Message).filter(Message.message_id == message_id).first()
        if message:
            for key, value in ml_data.items():
                setattr(message, key, value)
            message.is_processed = True
            db.commit()
            logger.info(f"Updated ML data for message {message_id}")
        return message
    
    # ✅ ADDED MISSING METHODS:
    
    @staticmethod
    def get_all_users(db: Session):
        """Get all users from database"""
        try:
            from app.models.database import User
            users = db.query(User).all()
            logger.info(f"Retrieved {len(users)} users from database")
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    @staticmethod
    def get_all_active_users(db: Session):
        """Get all active users from database"""
        try:
            from app.models.database import User
            users = db.query(User).filter(User.is_active == True).all()
            logger.info(f"Retrieved {len(users)} active users from database")
            return users
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    @staticmethod
    def get_users_by_region(db: Session, region: str):
        """Get users by region/location"""
        try:
            from app.models.database import User
            users = db.query(User).filter(
                User.location.like(f"%{region}%")
            ).all()
            logger.info(f"Retrieved {len(users)} users from region {region}")
            return users
        except Exception as e:
            logger.error(f"Error getting users by region: {e}")
            return []
    
    @staticmethod
    def get_recent_users(db: Session, hours: int = 24):
        """Get users who interacted recently"""
        try:
            from app.models.database import User
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            users = db.query(User).filter(
                User.last_interaction >= cutoff_time
            ).all()
            logger.info(f"Retrieved {len(users)} recent users (last {hours} hours)")
            return users
        except Exception as e:
            logger.error(f"Error getting recent users: {e}")
            return []

# Create database manager instance
db_manager = DatabaseManager()