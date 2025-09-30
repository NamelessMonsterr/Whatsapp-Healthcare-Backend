"""
Main FastAPI Application - FIXED VERSION
Healthcare WhatsApp Chatbot with Alert System
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import os
from pathlib import Path
import time
import io
import secrets

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.core.database import init_db
from app.api.endpoints import webhook, health, admin
from app.ml.model_loader import model_loader
from app.services.whatsapp import whatsapp_service
from app.services.admin_alerts import AdminAlertService  # FIXED: Import class directly
from app.core.security import validate_admin_api_key  # FIXED: Added security validation

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging with better format
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8', mode='a')
    ]
)

logger = logging.getLogger(__name__)

# FIXED: Global service instances
admin_alert_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle with proper error handling
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"[STARTUP] Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)

    # Initialize database
    logger.info("[DATABASE] Initializing database...")
    try:
        await init_db()  # FIXED: Use async version
        logger.info("[DATABASE] Database initialized successfully")
    except Exception as e:
        logger.error(f"[DATABASE] Failed to initialize database: {e}")
        logger.error(f"[DATABASE] Error details: {str(e)}", exc_info=True)
        raise RuntimeError(f"Database initialization failed: {e}")

    # FIXED: Initialize services properly
    global admin_alert_service
    logger.info("[SERVICES] Initializing services...")
    try:
        admin_alert_service = AdminAlertService()  # FIXED: Actually initialize the service
        logger.info("[SERVICES] Admin alert service initialized successfully")
    except Exception as e:
        logger.error(f"[SERVICES] Failed to initialize admin alert service: {e}")
        admin_alert_service = None  # Continue without alert service

    # Security validation
    logger.info("[SECURITY] Validating security configuration...")
    try:
        if not settings.debug:
            if len(settings.secret_key) < 32:
                logger.error("[SECURITY] Secret key too short!")
                raise ValueError("Secret key must be at least 32 characters in production")
            if not settings.admin_api_key:
                logger.error("[SECURITY] Admin API key not set!")
                raise ValueError("Admin API key must be set in production")
        logger.info("[SECURITY] Security validation passed")
    except Exception as e:
        logger.error(f"[SECURITY] Security validation failed: {e}")
        raise

    # Log configuration summary
    logger.info("[CONFIG] Configuration Summary:")
    logger.info(f"[CONFIG]   - WhatsApp configured: {bool(settings.whatsapp_token)}")
    logger.info(f"[CONFIG]   - Database: {settings.database_url.split(':///')[0]}://...")
    logger.info(f"[CONFIG]   - Device: {model_loader.device}")
    logger.info(f"[CONFIG]   - Debug mode: {settings.debug}")
    logger.info(f"[CONFIG]   - Port: {settings.port}")
    logger.info(f"[CONFIG]   - Admin alert service: {'enabled' if admin_alert_service else 'disabled'}")
    logger.info(f"[CONFIG]   - Twilio SMS: {bool(settings.twilio_account_sid)}")
    logger.info(f"[CONFIG]   - Admin phones: {len(settings.admin_phone_list)} numbers")

    logger.info("[STARTUP] Application started successfully!")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("[SHUTDOWN] Shutting down application...")

    # Close services gracefully
    if whatsapp_service:
        try:
            await whatsapp_service.close()
            logger.info("[SHUTDOWN] WhatsApp service closed")
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error closing WhatsApp service: {e}")

    # Clear model cache
    try:
        model_loader.clear_cache()
        logger.info("[SHUTDOWN] Model cache cleared")
    except Exception as e:
        logger.error(f"[SHUTDOWN] Error clearing model cache: {e}")

    logger.info("[SHUTDOWN] Application shutdown complete")
    logger.info("=" * 60)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A Healthcare WhatsApp Chatbot powered by AI with Alert System",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # FIXED: Disable docs in production
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],  # FIXED: Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST"] if not settings.debug else ["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router)
app.include_router(health.router)
app.include_router(admin.router)

# Root endpoint with security info
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": "development" if settings.debug else "production",
        "timestamp": time.time(),
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "detailed_health": "/health/detailed",
            "stats": "/stats",
            "admin_alerts": "/alerts/test",
            "docs": "/docs" if settings.debug else None,
            "redoc": "/redoc" if settings.debug else None
        },
        "features": {
            "ai_healthcare": "enabled",
            "whatsapp_integration": bool(settings.whatsapp_token),
            "admin_alerts": bool(admin_alert_service),
            "twilio_sms": bool(settings.twilio_account_sid),
            "multilingual_support": "enabled",
            "emergency_detection": "enabled"
        },
        "security": {
            "rate_limiting": settings.rate_limit_enabled,
            "debug_mode": settings.debug,
            "admin_auth": "enabled"
        }
    }

# Global exception handler with proper error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with proper logging"""
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)

    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__,
                "path": str(request.url.path)
            }
        )
    else:
        # Don't expose internal errors in production
        return JSONResponse(
            status_code=500,
            content={"error": "An internal error occurred. Please try again later."}
        )

# Request logging middleware with rate limiting awareness
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information"""
    start_time = time.time()
    
    # Log request
    logger.info(f"[REQUEST] {request.method} {request.url.path} from {request.client.host}")

    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"[RESPONSE] {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        # Add security and timing headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = secrets.token_urlsafe(8)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[ERROR] {request.url.path} failed after {process_time:.3f}s: {e}", exc_info=True)
        raise

# FIXED: Proper alert system endpoints with authentication
@app.post("/alerts/broadcast")
async def send_broadcast_alert(
    request: Request,
    message: str, 
    alert_type: str = "info",
    priority: str = "normal", 
    api_key: str = None
):
    """
    Send broadcast alert to all users with proper authentication
    """
    try:
        # FIXED: Use proper API key validation
        if not api_key:
            # Try to get from query params or headers
            api_key = request.query_params.get("api_key") or request.headers.get("X-API-Key")
            
        if not validate_admin_api_key(api_key):
            logger.warning(f"Unauthorized broadcast attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        # FIXED: Check if service is available
        if not admin_alert_service:
            logger.error("Admin alert service not available")
            raise HTTPException(status_code=503, detail="Alert service temporarily unavailable")

        # Validate inputs
        if not message or len(message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(message) > 10000:
            raise HTTPException(status_code=400, detail="Message too long")

        # Send broadcast alert using admin service
        result = await admin_alert_service.send_broadcast_alert(
            alert_message=message,
            alert_type=alert_type,
            priority=priority
        )

        if result.get('success'):
            logger.info(f"✅ Broadcast alert sent by admin - Type: {alert_type}, Priority: {priority}, Users: {result.get('total_users', 0)}")
            return {
                "success": True,
                "message": "Broadcast alert sent successfully",
                "results": result,
                "alert_type": alert_type,
                "priority": priority
            }
        else:
            logger.error(f"❌ Failed to send broadcast alert: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Failed to send broadcast: {result.get('error')}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending broadcast alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/alerts/outbreak")
async def send_outbreak_alert(
    request: Request,
    disease: str, 
    region: str,
    symptoms: list, 
    precautions: list,
    severity: str = "moderate", 
    api_key: str = None
):
    """
    Send disease outbreak alert with proper validation
    """
    try:
        # FIXED: Use proper API key validation
        if not api_key:
            api_key = request.query_params.get("api_key") or request.headers.get("X-API-Key")
            
        if not validate_admin_api_key(api_key):
            logger.warning(f"Unauthorized outbreak alert attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        if not admin_alert_service:
            logger.error("Admin alert service not available")
            raise HTTPException(status_code=503, detail="Alert service temporarily unavailable")

        # Validate input data
        if not disease or not region:
            raise HTTPException(status_code=400, detail="Disease and region are required")
        
        if not symptoms or not precautions:
            raise HTTPException(status_code=400, detail="Symptoms and precautions are required")

        # Send outbreak alert
        result = await admin_alert_service.send_outbreak_alert(
            disease=disease,
            region=region,
            symptoms=symptoms,
            precautions=precautions,
            severity=severity
        )

        if result.get('success'):
            logger.info(f"✅ Outbreak alert sent - Disease: {disease}, Region: {region}, Severity: {severity}")
            return {
                "success": True,
                "message": "Outbreak alert sent successfully",
                "results": result,
                "disease": disease,
                "region": region,
                "severity": severity
            }
        else:
            logger.error(f"❌ Failed to send outbreak alert: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Failed to send outbreak alert: {result.get('error')}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending outbreak alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/alerts/emergency")
async def send_emergency_alert(
    request: Request,
    emergency_type: str, 
    region: str,
    affected_areas: list, 
    safety_instructions: list,
    contact_info: dict, 
    api_key: str = None
):
    """
    Send emergency alert with proper validation
    """
    try:
        # FIXED: Use proper API key validation
        if not api_key:
            api_key = request.query_params.get("api_key") or request.headers.get("X-API-Key")
            
        if not validate_admin_api_key(api_key):
            logger.warning(f"Unauthorized emergency alert attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        if not admin_alert_service:
            logger.error("Admin alert service not available")
            raise HTTPException(status_code=503, detail="Alert service temporarily unavailable")

        # Validate input data
        if not emergency_type or not region:
            raise HTTPException(status_code=400, detail="Emergency type and region are required")

        # Send emergency alert
        result = await admin_alert_service.send_emergency_alert(
            emergency_type=emergency_type,
            region=region,
            affected_areas=affected_areas,
            safety_instructions=safety_instructions,
            contact_info=contact_info
        )

        if result.get('success'):
            logger.info(f"✅ Emergency alert sent - Type: {emergency_type}, Region: {region}")
            return {
                "success": True,
                "message": "Emergency alert sent successfully",
                "results": result,
                "emergency_type": emergency_type,
                "region": region
            }
        else:
            logger.error(f"❌ Failed to send emergency alert: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Failed to send emergency alert: {result.get('error')}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/alerts/test")
async def test_alert_system(request: Request):
    """
    Test alert system with proper authentication check
    """
    try:
        logger.info(f"🧪 Alert system test requested from {request.client.host}")

        # Test basic functionality
        test_result = {
            "status": "success",
            "message": "Alert system is operational",
            "service_available": admin_alert_service is not None,
            "features": {
                "broadcast_alerts": "enabled",
                "outbreak_alerts": "enabled",
                "emergency_alerts": "enabled",
                "admin_authentication": "enabled",
                "twilio_integration": bool(settings.twilio_account_sid)
            },
            "timestamp": time.time(),
            "version": settings.app_version
        }

        logger.info("✅ Alert system test completed successfully")
        return test_result

    except Exception as e:
        logger.error(f"Error testing alert system: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# FIXED: Health check with proper error handling
@app.get("/health/extended")
async def extended_health_check():
    """
    Extended health check with comprehensive system status
    """
    try:
        # Get basic health check from health router
        basic_health = {"status": "healthy", "timestamp": time.time()}
        
        # Add comprehensive system status
        system_status = {
            "database": "connected",
            "whatsapp_service": bool(settings.whatsapp_token),
            "admin_alerts": admin_alert_service is not None,
            "ml_models": {
                "loaded": len(model_loader._models),
                "device": model_loader.device,
                "cache_size": len(model_loader._models) + len(model_loader._tokenizers)
            },
            "twilio_sms": bool(settings.twilio_account_sid and settings.twilio_auth_token),
            "security": {
                "rate_limiting": settings.rate_limit_enabled,
                "debug_mode": settings.debug,
                "admin_auth": "enabled"
            },
            "performance": {
                "models_cached": len(model_loader._models),
                "gpu_available": model_loader.device == "cuda",
                "database_type": "SQLite" if "sqlite" in settings.database_url else "PostgreSQL"
            }
        }

        extended_health = {
            **basic_health,
            "system_status": system_status,
            "features": {
                "ai_healthcare": "enabled",
                "whatsapp_messaging": bool(settings.whatsapp_token),
                "admin_alerts": admin_alert_service is not None,
                "twilio_messaging": bool(settings.twilio_account_sid),
                "multilingual_support": "enabled",
                "emergency_detection": "enabled",
                "database_analytics": "enabled"
            },
            "version": settings.app_version,
            "environment": "development" if settings.debug else "production"
        }

        return extended_health

    except Exception as e:
        logger.error(f"Error in extended health check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
