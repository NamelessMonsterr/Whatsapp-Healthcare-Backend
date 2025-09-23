"""
WhatsApp Webhook Endpoint
"""
from fastapi import APIRouter, Request, Response, Query, HTTPException, BackgroundTasks
import logging
import json
from typing import Optional

from app.config import settings
from app.services.message_processor import message_processor

logger = logging.getLogger(__name__)

# ✅ CRITICAL: Define router at module level
router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.get("")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
):
    """
    Webhook verification endpoint for WhatsApp
    
    This endpoint is called by WhatsApp to verify the webhook URL.
    It must return the challenge value if the verify token matches.
    """
    logger.info(f"🔍 Webhook verification request")
    logger.info(f"Mode: {hub_mode}, Token: {hub_verify_token}, Challenge: {hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        logger.info("✅ Webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.error(f"❌ Webhook verification failed")
        logger.error(f"Expected token: {settings.verify_token}, Got: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive webhook events from WhatsApp
    
    This endpoint receives all webhook events including:
    - Incoming messages
    - Message status updates
    - Other WhatsApp events
    """
    try:
        # Get request body
        data = await request.json()
        
        # Log incoming webhook
        logger.info("="*50)
        logger.info("📥 INCOMING WEBHOOK DATA:")
        logger.info(json.dumps(data, indent=2))
        logger.info("="*50)
        
        # Process webhook in background to return quickly
        background_tasks.add_task(process_webhook_async, data)
        
        # Return success immediately
        return {"status": "received"}
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}", exc_info=True)
        # Still return 200 to avoid WhatsApp retries
        return {"status": "error", "message": str(e)}

async def process_webhook_async(data: dict):
    """
    Process webhook data asynchronously
    
    This function runs in the background to process incoming messages
    without blocking the webhook response.
    """
    try:
        # Check if it's a status update
        if is_status_update(data):
            logger.info("📊 Status update received")
            await handle_status_update(data)
            return
        
        # Process message
        result = await message_processor.process_webhook(data)
        
        if result.get("status") == "success":
            logger.info(f"✅ Message processed successfully: {result}")
        elif result.get("status") == "no_message":
            logger.info("ℹ️ No message to process in webhook")
        else:
            logger.warning(f"⚠️ Message processing result: {result}")
            
    except Exception as e:
        logger.error(f"Error processing webhook asynchronously: {e}", exc_info=True)

def is_status_update(data: dict) -> bool:
    """Check if webhook data is a status update"""
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'statuses' in value:
                    return True
        return False
    except:
        return False

async def handle_status_update(data: dict):
    """Handle message status updates"""
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                statuses = value.get('statuses', [])
                
                for status in statuses:
                    message_id = status.get('id')
                    status_type = status.get('status')
                    timestamp = status.get('timestamp')
                    recipient = status.get('recipient_id')
                    
                    logger.info(f"Message {message_id} status: {status_type} for {recipient}")
                    
                    # You can add database updates here to track message delivery
                    # For example: mark messages as delivered, read, etc.
                    
    except Exception as e:
        logger.error(f"Error handling status update: {e}")

# ✅ CRITICAL: Export router for main.py
__all__ = ["router"]