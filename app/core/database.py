"""
Database connection and session management - FIXED VERSION
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime

from app.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)

# Create async engine for modern async support
if settings.database_url.startswith("sqlite"):
    # Use aiosqlite for async SQLite support
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL or other databases
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True
    )

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Keep sync engine for migrations
sync_engine = None
if settings.database_url.startswith("sqlite"):
    sync_engine = create_engine(
        settings.database_url.replace("sqlite+aiosqlite", "sqlite"),
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.database_echo
    )
else:
    sync_engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.database_echo
    )

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def init_db_sync():
    """Initialize database tables synchronously (for migrations)"""
    try:
        if sync_engine:
            Base.metadata.create_all(bind=sync_engine)
            logger.info("Database tables created successfully (sync)")
    except Exception as e:
        logger.error(f"Error creating database tables (sync): {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# For backward compatibility with sync code
@contextmanager
def get_db_context_sync() -> Generator[Session, None, None]:
    """Sync context manager for database session"""
    if not sync_engine:
        raise RuntimeError("Sync engine not available for async database")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
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
    """Database operations manager with async support"""

    @staticmethod
    async def create_user(db: AsyncSession, phone_number: str, name: str = None):
        """Create or get user"""
        from app.models.database import User
        from sqlalchemy import select
        
        result = await db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(phone_number=phone_number, name=name)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user: {phone_number}")
        else:
            # Update last interaction
            user.last_interaction = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            
        return user

    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: int):
        """Create new conversation"""
        from app.models.database import Conversation
        from sqlalchemy import select

        # Close any active conversations
        result = await db.execute(
            select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            )
        )
        active_conversations = result.scalars().all()
        
        for conv in active_conversations:
            conv.is_active = False
        
        if active_conversations:
            await db.commit()

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        logger.info(f"Created new conversation for user {user_id}")
        return conversation

    @staticmethod
    async def get_or_create_active_conversation(db: AsyncSession, user_id: int):
        """Get active conversation or create new one"""
        from app.models.database import Conversation
        from sqlalchemy import select
        from datetime import datetime, timedelta

        # Get active conversation created within last 30 minutes
        result = await db.execute(
            select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.is_active == True,
                Conversation.started_at >= datetime.utcnow() - timedelta(minutes=30)
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await DatabaseManager.create_conversation(db, user_id)

        return conversation

    @staticmethod
    async def save_message(db: AsyncSession, conversation_id: int, message_id: str,
                     sender_type: str, content: str, **kwargs):
        """Save message to database"""
        from app.models.database import Message

        message = Message(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            content_length=len(content),
            **kwargs
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        logger.info(f"Saved message {message_id} from {sender_type}")
        return message

    @staticmethod
    async def update_message_ml_data(db: AsyncSession, message_id: str, **ml_data):
        """Update message with ML processing results"""
        from app.models.database import Message
        from sqlalchemy import select

        result = await db.execute(
            select(Message).where(Message.message_id == message_id)
        )
        message = result.scalar_one_or_none()
        
        if message:
            for key, value in ml_data.items():
                setattr(message, key, value)
            message.is_processed = True
            await db.commit()
            logger.info(f"Updated ML data for message {message_id}")
        return message

    # FIXED: Added missing methods and fixed naming inconsistencies
    @staticmethod
    async def get_all_users(db: AsyncSession):
        """Get all users from database"""
        try:
            from app.models.database import User
            from sqlalchemy import select
            
            result = await db.execute(select(User))
            users = result.scalars().all()
            logger.info(f"Retrieved {len(users)} users from database")
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    @staticmethod
    async def get_all_active_users(db: AsyncSession):
        """Get all active users from database"""
        try:
            from app.models.database import User
            from sqlalchemy import select
            
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()
            logger.info(f"Retrieved {len(users)} active users from database")
            return users
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []

    @staticmethod
    async def get_users_by_region(db: AsyncSession, region: str):
        """Get users by region/location - FIXED METHOD NAME"""
        try:
            from app.models.database import User
            from sqlalchemy import select
            
            result = await db.execute(
                select(User).where(User.location.like(f"%{region}%"))
            )
            users = result.scalars().all()
            logger.info(f"Retrieved {len(users)} users from region {region}")
            return users
        except Exception as e:
            logger.error(f"Error getting users by region: {e}")
            return []

    @staticmethod
    async def get_recent_users(db: AsyncSession, hours: int = 24):
        """Get users who interacted recently"""
        try:
            from app.models.database import User
            from sqlalchemy import select
            from datetime import datetime, timedelta

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            result = await db.execute(
                select(User).where(User.last_interaction >= cutoff_time)
            )
            users = result.scalars().all()
            logger.info(f"Retrieved {len(users)} recent users (last {hours} hours)")
            return users
        except Exception as e:
            logger.error(f"Error getting recent users: {e}")
            return []

    # FIXED: Added method to log broadcast alerts
    @staticmethod
    async def log_broadcast_alert(db: AsyncSession, alert_data: dict) -> bool:
        """Log broadcast alert for analytics"""
        try:
            from app.models.database import BroadcastAlert
            
            alert = BroadcastAlert(**alert_data)
            db.add(alert)
            await db.commit()
            logger.info(f"Logged broadcast alert: {alert_data.get('alert_id')}")
            return True
        except Exception as e:
            logger.error(f"Error logging broadcast alert: {e}")
            return False

    # FIXED: Added method to update user
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, **update_data):
        """Update user information"""
        from app.models.database import User
        from sqlalchemy import select

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            logger.info(f"Updated user {user_id}")
            return user
        return None

# Create database manager instance
db_manager = DatabaseManager()

# FIXED: Added select import for async queries
from sqlalchemy import select
