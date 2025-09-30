"""
Main FastAPI Application - COMPLETELY FIXED
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
import time
import io
import asyncio
import signal
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.core.database import init_db, db_manager
from app.api.endpoints import webhook, health, admin
from app.ml.model_loader import model_loader
from app.services.whatsapp import whatsapp_service
from app.services.admin_alerts import admin_alert_service
from app.core.security import add_security_headers, mask_sensitive_data

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.FileHandler('logs/error.log', encoding='utf-8', level=logging.ERROR)
    ]
)

logger = logging.getLogger(__name__)

# Global shutdown flag
shutdown_flag = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle with proper initialization and cleanup
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"[STARTUP] Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)

    startup_errors = []
    
    # Initialize database
    logger.info("[DATABASE] Initializing database...")
    try:
        init_db()
        logger.info("[DATABASE] ✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"[DATABASE] ❌ Failed to initialize database: {e}")
        startup_errors.append(f"Database: {e}")

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
            logger.info(f"[MODELS] ✅ Models loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"[MODELS] ❌ Failed to preload some models: {e}")
            logger.info("[MODELS] Models will be loaded on demand")
            startup_errors.append(f"ML Models: {e}")

    # Initialize services
    logger.info("[SERVICES] Initializing services...")
    try:
        # Test WhatsApp service
        if whatsapp_service:
            logger.info("[SERVICES] ✅ WhatsApp service available")
        else:
            logger.warning("[SERVICES] ⚠️ WhatsApp service not available")
            startup_errors.append("WhatsApp service initialization failed")
        
        # Test admin alert service
        if admin_alert_service:
            logger.info("[SERVICES] ✅ Admin alert service available")
        else:
            logger.warning("[SERVICES] ⚠️ Admin alert service not available")
            
    except Exception as e:
        logger.error(f"[SERVICES] ❌ Service initialization error: {e}")
        startup_errors.append(f"Services: {e}")

    # Log configuration
    logger.info("[CONFIG] Configuration Summary:")
    logger.info(f"[CONFIG]   - WhatsApp configured: {settings.is_whatsapp_configured}")
    logger.info(f"[CONFIG]   - Twilio configured: {settings.is_twilio_configured}")
    logger.info(f"[CONFIG]   - Database: {mask_sensitive_data(settings.database_url)}")
    logger.info(f"[CONFIG]   - Device: {model_loader.device}")
    logger.info(f"[CONFIG]   - Debug mode: {settings.debug}")
    logger.info(f"[CONFIG]   - Port: {settings.port}")
    logger.info(f"[CONFIG]   - Alert system: enabled")
    logger.info(f"[CONFIG]   - Rate limiting: {settings.rate_limit_enabled}")
    logger.info(f"[CONFIG]   - GPU available: {model_loader.device == 'cuda'}")

    # Check for startup errors
    if startup_errors:
        logger.error(f"[STARTUP] ⚠️ Startup completed with errors: {startup_errors}")
        if not settings.debug:
            logger.error("[STARTUP] ❌ Critical startup errors in production mode")
            raise RuntimeError(f"Startup errors: {startup_errors}")
    else:
        logger.info("[STARTUP] ✅ Application started successfully!")
    
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("[SHUTDOWN] Initiating graceful shutdown...")

    # Set shutdown flag
    global shutdown_flag
    shutdown_flag = True

    # Close WhatsApp service
    try:
        if whatsapp_service:
            await whatsapp_service.close()
            logger.info("[SHUTDOWN] ✅ WhatsApp service closed")
    except Exception as e:
        logger.error(f"[SHUTDOWN] ❌ Error closing WhatsApp service: {e}")

    # Clear model cache
    try:
        model_loader.clear_cache()
        logger.info("[SHUTDOWN] ✅ Model cache cleared")
    except Exception as e:
        logger.error(f"[SHUTDOWN] ❌ Error clearing model cache: {e}")

    # Close database connections
    try:
        db_manager.engine.dispose()
        logger.info("[SHUTDOWN] ✅ Database connections closed")
    except Exception as e:
        logger.error(f"[SHUTDOWN] ❌ Error closing database connections: {e}")

    logger.info("[SHUTDOWN] ✅ Application shutdown complete")
    logger.info("=" * 60)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A Healthcare WhatsApp Chatbot powered by AI with Alert System",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)

# Include routers
try:
    app.include_router(webhook.router)
    app.include_router(health.router)
    app.include_router(admin.router)
    logger.info("✅ All routers included successfully")
except Exception as e:
    logger.error(f"❌ Error including routers: {e}")
    raise

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with application information"""
    try:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "timestamp": time.time(),
            "environment": {
                "debug": settings.debug,
                "production": settings.is_production,
                "gpu_available": model_loader.device == "cuda"
            },
            "endpoints": {
                "webhook": "/webhook",
                "health": "/health",
                "detailed_health": "/health/detailed",
                "stats": "/stats",
                "admin_alerts": "/admin",
                "docs": "/docs" if settings.debug else "disabled",
                "redoc": "/redoc" if settings.debug else "disabled"
            },
            "features": {
                "ai_healthcare": "enabled",
                "whatsapp_integration": "enabled" if settings.is_whatsapp_configured else "disabled",
                "admin_alerts": "enabled",
                "data_gov_integration": "enabled" if settings.data_gov_api_key else "disabled",
                "database_analytics": "enabled",
                "rate_limiting": "enabled" if settings.rate_limit_enabled else "disabled",
                "twilio_integration": "enabled" if settings.is_twilio_configured else "disabled"
            },
            "limits": {
                "max_message_length": 4096,
                "max_buttons": 3,
                "rate_limit_per_minute": settings.rate_limit_per_minute,
                "session_timeout_minutes": 30
            }
        }
    except Exception as e:
        logger.error(f"❌ Error in root endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "timestamp": time.time()}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with proper logging and response"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Generate error ID for tracking
    error_id = str(uuid.uuid4())
    
    error_details = {
        "error_id": error_id,
        "message": "Internal server error",
        "timestamp": time.time()
    }
    
    if settings.debug:
        error_details.update({
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url),
            "method": request.method
        })
        logger.error(f"Debug error response: {error_details}")
    else:
        logger.error(f"Production error ID: {error_id}")
    
    return JSONResponse(
        status_code=500,
        content=error_details,
        headers={"X-Error-ID": error_id}
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing and error handling"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Skip health checks from logging in production
    if not settings.debug and request.url.path in ["/health", "/health/detailed"]:
        response = await call_next(request)
        return response

    # Log request
    logger.info(f"[{request_id}] 📥 {request.method} {request.url.path} from {request.client.host}")
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        status_code = response.status_code
        status_emoji = "✅" if status_code < 400 else "⚠️" if status_code < 500 else "❌"
        
        logger.info(f"[{request_id}] {status_emoji} {request.method} {request.url.path} - Status: {status_code} - Time: {process_time:.3f}s")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[{request_id}] ❌ {request.method} {request.url.path} failed after {process_time:.3f}s: {e}", exc_info=True)
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "timestamp": time.time()
            },
            headers={"X-Request-ID": request_id}
        )

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Add security headers and handle security-related tasks"""
    response = await call_next(request)
    
    # Add security headers
    response = add_security_headers(response)
    
    # Add request ID if not already present
    if "X-Request-ID" not in response.headers:
        response.headers["X-Request-ID"] = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    return response

# Rate limiting middleware (basic implementation)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basic rate limiting by IP address"""
    if not settings.rate_limit_enabled:
        return await call_next(request)
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/health/detailed", "/"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host
    
    # Simple in-memory rate limiting (use Redis for production)
    # This is a basic implementation - consider using redis or database for production
    import time
    from collections import defaultdict
    
    if not hasattr(app, '_rate_limit_storage'):
        app._rate_limit_storage = defaultdict(list)
    
    now = time.time()
    window_start = now - 60  # 1 minute window
    
    # Clean old entries
    app._rate_limit_storage[client_ip] = [
        timestamp for timestamp in app._rate_limit_storage[client_ip]
        if timestamp > window_start
    ]
    
    # Check rate limit
    if len(app._rate_limit_storage[client_ip]) >= settings.rate_limit_per_minute:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Maximum {settings.rate_limit_per_minute} requests per minute allowed"
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    # Add current request
    app._rate_limit_storage[client_ip].append(now)
    
    # Add rate limit headers
    response = await call_next(request)
    remaining = settings.rate_limit_per_minute - len(app._rate_limit_storage[client_ip])
    
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(int(now + 60))
    
    return response

# Alert system endpoints (moved from main.py to separate file for better organization)
@app.post("/alerts/broadcast")
async def send_broadcast_alert(message: str, alert_type: str = "info",
                             priority: str = "normal", api_key: str = None):
    """
    Send broadcast alert to all users
    
    This endpoint allows administrators to send broadcast alerts to all users.
    Requires valid API key for authentication.
    """
    try:
        # FIXED: Use proper API key validation from security module
        from app.core.security import validate_admin_api_key
        
        if not api_key or not validate_admin_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid or missing API key"}
            )

        # Validate inputs
        if not message or len(message.strip()) == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "Bad Request", "message": "Message cannot be empty"}
            )
        
        if len(message) > 2000:  # Reasonable limit for broadcast messages
            return JSONResponse(
                status_code=400,
                content={"error": "Bad Request", "message": "Message too long (max 2000 characters)"}
            )

        # Send broadcast alert using admin service
        result = await admin_alert_service.send_broadcast_alert(
            alert_message=message.strip(),
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
            "admin_service": "initialized" if admin_alert_service else "not_available",
            "data_gov_integration": bool(settings.data_gov_api_key),
            "whatsapp_integration": settings.is_whatsapp_configured,
            "twilio_integration": settings.is_twilio_configured,
            "rate_limiting": settings.rate_limit_enabled,
            "gpu_available": model_loader.device == "cuda"
        }

        # Get database health
        try:
            with get_db_context() as db:
                db_health = db_manager.get_database_health(db)
                alert_status["database"] = db_health
        except Exception as e:
            alert_status["database"] = {"status": "unhealthy", "error": str(e)}

        # Get system resources
        try:
            import psutil
            alert_status["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            alert_status["system"] = {"error": f"Could not get system stats: {e}"}

        # Combine health information
        extended_health = {
            **basic_health,
            "alert_system": alert_status,
            "features": {
                "ai_healthcare": "enabled",
                "whatsapp_messaging": "enabled" if settings.is_whatsapp_configured else "disabled",
                "admin_alerts": "enabled",
                "data_gov_integration": "enabled" if settings.data_gov_api_key else "disabled",
                "database_analytics": "enabled",
                "rate_limiting": "enabled" if settings.rate_limit_enabled else "disabled",
                "twilio_integration": "enabled" if settings.is_twilio_configured else "disabled",
                "gpu_acceleration": "enabled" if model_loader.device == "cuda" else "disabled"
            },
            "limits": {
                "rate_limit_per_minute": settings.rate_limit_per_minute,
                "max_message_length": 4096,
                "max_buttons": 3,
                "session_timeout_minutes": 30
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

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    global shutdown_flag
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    import uvicorn
    
    # Validate configuration before starting
    if not settings.is_whatsapp_configured:
        logger.warning("⚠️ WhatsApp not fully configured, messaging features may not work")
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.debug,
        timeout_keep_alive=30,
        timeout_notify=30,
        limit_max_requests=1000 if not settings.debug else None
    )
