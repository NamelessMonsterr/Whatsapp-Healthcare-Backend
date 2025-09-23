"""
Health Check and Status Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any
import torch
import psutil
import platform
from datetime import datetime, timedelta

from app.config import settings
from app.core.database import get_db
from app.ml.model_loader import model_loader

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns the current status of the application and its components.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": {
            "debug": settings.debug,
            "whatsapp_configured": bool(settings.whatsapp_token and settings.whatsapp_phone_number_id),
            "database_configured": bool(settings.database_url),
            "ml_models_path": settings.model_cache_dir
        }
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with system information
    
    Returns comprehensive information about system resources,
    database connectivity, and model status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "checks": {}
    }
    
    # System Information
    try:
        health_status["system"] = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }
        health_status["checks"]["system"] = "ok"
    except Exception as e:
        health_status["checks"]["system"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Database Check
    try:
        # FIXED: Using text() wrapper for raw SQL query
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
        
        # Get table counts
        from app.models.database import User, Message, Conversation
        health_status["database_stats"] = {
            "users": db.query(User).count(),
            "conversations": db.query(Conversation).count(),
            "messages": db.query(Message).count()
        }
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # WhatsApp Configuration Check
    health_status["checks"]["whatsapp"] = {
        "token_configured": bool(settings.whatsapp_token),
        "phone_number_configured": bool(settings.whatsapp_phone_number_id),
        "verify_token_configured": bool(settings.verify_token)
    }
    
    if not all(health_status["checks"]["whatsapp"].values()):
        health_status["status"] = "degraded"
    
    # ML Models Check
    try:
        health_status["ml_models"] = {
            "device": str(model_loader.device),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "models_loaded": {
                "multilingual": model_loader.models.get('multilingual') is not None,
                "biomedical": model_loader.models.get('biomedical') is not None,
                "chatdoctor": model_loader.models.get('chatdoctor') is not None
            }
        }
        
        if torch.cuda.is_available():
            health_status["ml_models"]["cuda_device_name"] = torch.cuda.get_device_name(0)
            health_status["ml_models"]["cuda_memory"] = {
                "allocated": torch.cuda.memory_allocated(),
                "reserved": torch.cuda.memory_reserved()
            }
        
        health_status["checks"]["ml_models"] = "ok"
    except Exception as e:
        health_status["checks"]["ml_models"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get application statistics
    
    Returns statistics about messages processed, users, and model performance.
    """
    from app.models.database import User, Message, Conversation, ModelPerformance
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Time ranges
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(days=1)
    last_week = now - timedelta(weeks=1)
    
    stats = {
        "timestamp": now.isoformat(),
        "totals": {
            "users": db.query(User).count(),
            "conversations": db.query(Conversation).count(),
            "messages": db.query(Message).count()
        },
        "recent_activity": {
            "last_hour": {
                "messages": db.query(Message).filter(Message.timestamp >= last_hour).count(),
                "new_users": db.query(User).filter(User.created_at >= last_hour).count()
            },
            "last_day": {
                "messages": db.query(Message).filter(Message.timestamp >= last_day).count(),
                "new_users": db.query(User).filter(User.created_at >= last_day).count(),
                "conversations": db.query(Conversation).filter(Conversation.started_at >= last_day).count()
            },
            "last_week": {
                "messages": db.query(Message).filter(Message.timestamp >= last_week).count(),
                "new_users": db.query(User).filter(User.created_at >= last_week).count(),
                "conversations": db.query(Conversation).filter(Conversation.started_at >= last_week).count()
            }
        }
    }
    
    # Intent distribution
    intent_counts = db.query(
        Message.detected_intent,
        func.count(Message.id)
    ).filter(
        Message.detected_intent.isnot(None)
    ).group_by(Message.detected_intent).all()
    
    stats["intent_distribution"] = {intent: count for intent, count in intent_counts}
    
    # Language distribution
    language_counts = db.query(
        Message.detected_language,
        func.count(Message.id)
    ).filter(
        Message.detected_language.isnot(None)
    ).group_by(Message.detected_language).all()
    
    stats["language_distribution"] = {lang: count for lang, count in language_counts}
    
    # Model performance
    model_stats = db.query(ModelPerformance).all()
    stats["model_performance"] = [
        {
            "model": m.model_name,
            "requests": m.request_count,
            "avg_time_ms": m.total_processing_time / m.request_count if m.request_count > 0 else 0,
            "errors": m.error_count,
            "last_used": m.last_used.isoformat() if m.last_used else None
        }
        for m in model_stats
    ]
    
    # Average confidence scores by intent
    avg_confidence = db.query(
        Message.detected_intent,
        func.avg(Message.confidence_score)
    ).filter(
        Message.detected_intent.isnot(None),
        Message.confidence_score.isnot(None)
    ).group_by(Message.detected_intent).all()
    
    stats["average_confidence_by_intent"] = {intent: float(conf) for intent, conf in avg_confidence}
    
    return stats

@router.post("/models/reload")
async def reload_models():
    """
    Reload ML models
    
    Forces a reload of all ML models. Useful for updating models
    or recovering from errors.
    """
    try:
        model_loader.clear_cache()
        model_loader.preload_all_models()
        
        return {
            "status": "success",
            "message": "Models reloaded successfully",
            "models_loaded": {
                "multilingual": model_loader.models.get('multilingual') is not None,
                "biomedical": model_loader.models.get('biomedical') is not None,
                "chatdoctor": model_loader.models.get('chatdoctor') is not None
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to reload models: {str(e)}"
        }

@router.get("/config")
async def get_configuration():
    """
    Get current configuration (non-sensitive)
    
    Returns the current application configuration excluding sensitive values.
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "host": settings.host,
        "port": settings.port,
        "use_gpu": settings.use_gpu,
        "model_device": settings.model_device,
        "max_length": settings.max_length,
        "batch_size": settings.batch_size,
        "rate_limit_enabled": settings.rate_limit_enabled,
        "rate_limit_per_minute": settings.rate_limit_per_minute,
        "model_cache_dir": settings.model_cache_dir,
        "whatsapp_configured": bool(settings.whatsapp_token),
        "database_type": "sqlite" if "sqlite" in settings.database_url else "other"
    }

# ✅ CRITICAL: Export router for main.py
__all__ = ["router"]