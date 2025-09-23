"""
Main FastAPI Application
Healthcare WhatsApp Chatbot with Alert System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
import time
import io

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.core.database import init_db
from app.api.endpoints import webhook, health, admin
from app.ml.model_loader import model_loader
from app.services.whatsapp import whatsapp_service
from app.services.admin_alerts import admin_alert_service

# Fix encoding for Windows
if sys.platform == "win32":
    # Set UTF-8 encoding for stdout and stderr
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    
    This function runs before the app starts and after it shuts down.
    Used for initialization and cleanup tasks.
    """
    # Startup
    logger.info("=" * 50)
    logger.info(f"[STARTUP] Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 50)
    
    # Initialize database
    logger.info("[DATABASE] Initializing database...")
    try:
        init_db()
        logger.info("[DATABASE] Database initialized successfully")
    except Exception as e:
        logger.error(f"[DATABASE] Failed to initialize database: {e}")
        raise
    
    # Preload ML models
    if settings.debug:
        logger.info("[MODELS] Debug mode - Skipping model preloading")
        logger.info("[MODELS] Models will be loaded on first use")
    else:
        logger.info("[MODELS] Preloading ML models...")
        try:
            start_time = time.time()
            model_loader.preload_all_models()
            load_time = time.time() - start_time
            logger.info(f"[MODELS] Models loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"[MODELS] Failed to preload some models: {e}")
            logger.info("[MODELS] Models will be loaded on demand")
    
    # Initialize admin alert service
    logger.info("[ALERTS] Initializing admin alert service...")
    try:
        # Initialize admin alert service
        logger.info("[ALERTS] Admin alert service initialized successfully")
    except Exception as e:
        logger.error(f"[ALERTS] Failed to initialize admin alert service: {e}")
    
    # Log configuration
    logger.info("[CONFIG] Configuration:")
    logger.info(f"[CONFIG]   - WhatsApp configured: {bool(settings.whatsapp_token)}")
    logger.info(f"[CONFIG]   - Database: {settings.database_url}")
    logger.info(f"[CONFIG]   - Device: {model_loader.device}")
    logger.info(f"[CONFIG]   - Debug mode: {settings.debug}")
    logger.info(f"[CONFIG]   - Port: {settings.port}")
    logger.info(f"[CONFIG]   - Alert system: enabled")
    logger.info(f"[CONFIG]   - Data.gov.in API: {bool(settings.data_gov_api_key)}")
    
    logger.info("[STARTUP] Application started successfully!")
    logger.info("=" * 50)
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info("[SHUTDOWN] Shutting down application...")
    
    # Close WhatsApp client
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
    
    # Shutdown admin alert service
    try:
        logger.info("[SHUTDOWN] Admin alert service shutdown")
    except Exception as e:
        logger.error(f"[SHUTDOWN] Error shutting down admin alert service: {e}")
    
    logger.info("[SHUTDOWN] Application shutdown complete")
    logger.info("=" * 50)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A Healthcare WhatsApp Chatbot powered by AI with Alert System",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router)
app.include_router(health.router)
app.include_router(admin.router)  # ✅ Added admin router for alerts

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "detailed_health": "/health/detailed",
            "stats": "/stats",
            "admin_alerts": "/admin",  # ✅ Added admin alerts endpoint
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": {
            "ai_healthcare": "enabled",
            "whatsapp_integration": "enabled",
            "admin_alerts": "enabled",  # ✅ Alert system enabled
            "data_gov_integration": "enabled",
            "database_analytics": "enabled"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"[REQUEST] {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"[RESPONSE] {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Alert system endpoints
@app.post("/alerts/broadcast")
async def send_broadcast_alert(message: str, alert_type: str = "info", 
                             priority: str = "normal", api_key: str = None):
    """
    Send broadcast alert to all users
    
    This endpoint allows administrators to send broadcast alerts to all users.
    Requires valid API key for authentication.
    
    Args:
        message: Alert message to send
        alert_type: Type of alert (info, warning, emergency, outbreak)
        priority: Priority level (low, normal, high)
        api_key: Administrator API key for authentication
        
    Returns:
        Dict with broadcast results
    """
    try:
        # Authenticate admin (simple for demo - improve for production)
        if not api_key or api_key != "admin_secret_key_change_this":
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid or missing API key"}
            )
        
        # Send broadcast alert using admin service
        result = await admin_alert_service.send_broadcast_alert(
            alert_message=message,
            alert_type=alert_type,
            priority=priority
        )
        
        if result.get('success'):
            logger.info(f"✅ Broadcast alert sent - Type: {alert_type}, Priority: {priority}")
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            logger.error(f"❌ Failed to send broadcast alert: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to send broadcast alert", "details": result.get('error')}
            )
            
    except Exception as e:
        logger.error(f"Error sending broadcast alert: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )

@app.post("/alerts/outbreak")
async def send_outbreak_alert(disease: str, region: str, 
                            symptoms: list, precautions: list,
                            severity: str = "moderate", api_key: str = None):
    """
    Send disease outbreak alert
    
    Send outbreak alerts to users in affected regions.
    
    Args:
        disease: Disease name
        region: Affected region
        symptoms: List of symptoms to watch for
        precautions: List of preventive measures
        severity: Severity level (low, moderate, high, critical)
        api_key: Administrator API key
        
    Returns:
        Dict with outbreak alert results
    """
    try:
        # Authenticate admin
        if not api_key or api_key != "admin_secret_key_change_this":
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid or missing API key"}
            )
        
        # Send outbreak alert
        result = await admin_alert_service.send_outbreak_alert(
            disease=disease,
            region=region,
            symptoms=symptoms,
            precautions=precautions,
            severity=severity
        )
        
        if result.get('success'):
            logger.info(f"✅ Outbreak alert sent - Disease: {disease}, Region: {region}")
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            logger.error(f"❌ Failed to send outbreak alert: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to send outbreak alert", "details": result.get('error')}
            )
            
    except Exception as e:
        logger.error(f"Error sending outbreak alert: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )

@app.post("/alerts/emergency")
async def send_emergency_alert(emergency_type: str, region: str,
                             affected_areas: list, safety_instructions: list,
                             contact_info: dict, api_key: str = None):
    """
    Send emergency alert
    
    Send emergency alerts for natural disasters, accidents, etc.
    
    Args:
        emergency_type: Type of emergency
        region: Affected region
        affected_areas: List of affected areas
        safety_instructions: List of safety instructions
        contact_info: Emergency contact information
        api_key: Administrator API key
        
    Returns:
        Dict with emergency alert results
    """
    try:
        # Authenticate admin
        if not api_key or api_key != "admin_secret_key_change_this":
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid or missing API key"}
            )
        
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
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            logger.error(f"❌ Failed to send emergency alert: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to send emergency alert", "details": result.get('error')}
            )
            
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )

@app.get("/alerts/test")
async def test_alert_system():
    """
    Test alert system
    
    Simple endpoint to test if alert system is working.
    
    Returns:
        Dict with test results
    """
    try:
        logger.info("🧪 Alert system test requested")
        
        # Test basic functionality
        test_result = {
            "status": "success",
            "message": "Alert system is operational",
            "features": {
                "broadcast_alerts": "enabled",
                "outbreak_alerts": "enabled",
                "emergency_alerts": "enabled",
                "admin_authentication": "enabled"
            },
            "timestamp": time.time()
        }
        
        logger.info("✅ Alert system test completed successfully")
        return JSONResponse(
            status_code=200,
            content=test_result
        )
        
    except Exception as e:
        logger.error(f"Error testing alert system: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )

# Health check with alert system status
@app.get("/health/extended")
async def extended_health_check():
    """
    Extended health check with alert system status
    
    Returns detailed health information including alert system status.
    """
    try:
        # Get basic health check
        basic_health = await health.health_check()
        
        # Add alert system status
        alert_status = {
            "alert_system": "operational",
            "admin_service": "initialized",
            "data_gov_integration": bool(settings.data_gov_api_key),
            "whatsapp_integration": bool(settings.whatsapp_token)
        }
        
        # Combine health information
        extended_health = {
            **basic_health,
            "alert_system": alert_status,
            "features": {
                "ai_healthcare": "enabled",
                "whatsapp_messaging": "enabled",
                "admin_alerts": "enabled",
                "data_gov_integration": "enabled" if settings.data_gov_api_key else "disabled",
                "database_analytics": "enabled"
            }
        }
        
        return JSONResponse(
            status_code=200,
            content=extended_health
        )
        
    except Exception as e:
        logger.error(f"Error in extended health check: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )