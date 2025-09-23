"""
Admin API Endpoints - For sending broadcast alerts and managing system
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from app.services.admin_alerts import admin_alert_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin authentication (simplified for demo)
ADMIN_API_KEY = "your-admin-api-key-change-this-in-production"

class AdminAuth:
    """Simple admin authentication"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def verify(self) -> bool:
        """Verify admin API key"""
        return self.api_key == ADMIN_API_KEY

# Request models
class BroadcastAlertRequest(BaseModel):
    """Request model for broadcast alerts"""
    message: str
    alert_type: str = "info"
    target_users: Optional[List[str]] = None
    target_regions: Optional[List[str]] = None
    priority: str = "normal"

class OutbreakAlertRequest(BaseModel):
    """Request model for outbreak alerts"""
    disease: str
    region: str
    symptoms: List[str]
    precautions: List[str]
    severity: str = "moderate"

class EmergencyAlertRequest(BaseModel):
    """Request model for emergency alerts"""
    emergency_type: str
    region: str
    affected_areas: List[str]
    safety_instructions: List[str]
    contact_info: Dict[str, str]

class HealthAdvisoryRequest(BaseModel):
    """Request model for health advisories"""
    topic: str
    recommendations: List[str]
    target_audience: str = "general"

# Admin endpoints
@router.post("/alerts/broadcast")
async def send_broadcast_alert(request: BroadcastAlertRequest, api_key: str):
    """Send broadcast alert to users"""
    try:
        # Authenticate admin
        auth = AdminAuth(api_key)
        if not auth.verify():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Send broadcast alert
        result = await admin_alert_service.send_broadcast_alert(
            alert_message=request.message,
            alert_type=request.alert_type,
            target_users=request.target_users,
            target_regions=request.target_regions,
            priority=request.priority
        )
        
        if result.get('success'):
            logger.info(f"✅ Admin broadcast alert sent - Type: {request.alert_type}")
            return result
        else:
            logger.error(f"❌ Admin broadcast alert failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin broadcast alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/outbreak")
async def send_outbreak_alert(request: OutbreakAlertRequest, api_key: str):
    """Send disease outbreak alert"""
    try:
        # Authenticate admin
        auth = AdminAuth(api_key)
        if not auth.verify():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Send outbreak alert
        result = await admin_alert_service.send_outbreak_alert(
            disease=request.disease,
            region=request.region,
            symptoms=request.symptoms,
            precautions=request.precautions,
            severity=request.severity
        )
        
        if result.get('success'):
            logger.info(f"✅ Admin outbreak alert sent - Disease: {request.disease}")
            return result
        else:
            logger.error(f"❌ Admin outbreak alert failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin outbreak alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/emergency")
async def send_emergency_alert(request: EmergencyAlertRequest, api_key: str):
    """Send emergency alert"""
    try:
        # Authenticate admin
        auth = AdminAuth(api_key)
        if not auth.verify():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Send emergency alert
        result = await admin_alert_service.send_emergency_alert(
            emergency_type=request.emergency_type,
            region=request.region,
            affected_areas=request.affected_areas,
            safety_instructions=request.safety_instructions,
            contact_info=request.contact_info
        )
        
        if result.get('success'):
            logger.info(f"✅ Admin emergency alert sent - Type: {request.emergency_type}")
            return result
        else:
            logger.error(f"❌ Admin emergency alert failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin emergency alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/advisory")
async def send_health_advisory(request: HealthAdvisoryRequest, api_key: str):
    """Send health advisory"""
    try:
        # Authenticate admin
        auth = AdminAuth(api_key)
        if not auth.verify():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Send health advisory
        result = await admin_alert_service.send_health_advisory(
            topic=request.topic,
            recommendations=request.recommendations,
            target_audience=request.target_audience
        )
        
        if result.get('success'):
            logger.info(f"✅ Admin health advisory sent - Topic: {request.topic}")
            return result
        else:
            logger.error(f"❌ Admin health advisory failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin health advisory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/history")
async def get_broadcast_history(limit: int = 50, api_key: str = None):
    """Get broadcast alert history"""
    try:
        # Authenticate admin
        if api_key:
            auth = AdminAuth(api_key)
            if not auth.verify():
                raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Get history
        result = await admin_alert_service.get_broadcast_history(limit)
        
        if result.get('success'):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting broadcast history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/alerts/{broadcast_id}")
async def cancel_scheduled_broadcast(broadcast_id: str, api_key: str):
    """Cancel scheduled broadcast"""
    try:
        # Authenticate admin
        auth = AdminAuth(api_key)
        if not auth.verify():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Cancel broadcast
        result = await admin_alert_service.cancel_scheduled_broadcast(broadcast_id)
        
        if result.get('success'):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling broadcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def admin_health_check():
    """Admin health check"""
    return {
        "status": "healthy",
        "service": "admin_alerts",
        "timestamp": "2025-09-14T16:00:00Z"
    }

# Test endpoint
@router.get("/test")
async def test_admin_endpoint():
    """Test admin endpoint"""
    return {"message": "Admin endpoint working", "status": "success"}