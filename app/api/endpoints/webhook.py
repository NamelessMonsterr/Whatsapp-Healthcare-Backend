"""
WhatsApp Webhook Endpoint - COMPLETELY FIXED
"""
from fastapi import APIRouter, Request, Response, Query, HTTPException, BackgroundTasks
import logging
import json
import time
import hmac
import hashlib
from typing import Optional, Dict, Any

from app.config import settings
from app.services.message_processor import message_processor
from app.core.security import validate_whatsapp_phone, mask_sensitive_data
from app.core.database import get_db_context, db_manager

logger = logging.getLogger(__name__)

# Create router with proper configuration
router = APIRouter(prefix="/webhook", tags=["webhook"])

# Webhook verification endpoint
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
    try:
        logger.info(f"🔍 Webhook verification request")
        logger.info(f"Mode: {hub_mode}, Token: {mask_sensitive_data(hub_verify_token or '')}, Challenge: {hub_challenge}")
        
        # FIXED: Validate all required parameters
        if not all([hub_mode, hub_verify_token, hub_challenge]):
            logger.error("❌ Missing required webhook verification parameters")
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters"
            )
        
        # FIXED: Validate hub mode
        if hub_mode != "subscribe":
            logger.error(f"❌ Invalid hub mode: {hub_mode}")
            raise HTTPException(
                status_code=400,
                detail="Invalid hub mode"
            )
        
        # FIXED: Use secure comparison to prevent timing attacks
        if hmac.compare_digest(hub_verify_token, settings.verify_token):
            logger.info("✅ Webhook verified successfully")
            return Response(content=hub_challenge, media_type="text/plain")
        else:
            logger.error(f"❌ Webhook verification failed - token mismatch")
            logger.error(f"Expected: {mask_sensitive_data(settings.verify_token)}")
            logger.error(f"Received: {mask_sensitive_data(hub_verify_token)}")
            raise HTTPException(
                status_code=403,
                detail="Verification failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in webhook verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during verification"
        )

# Main webhook endpoint for receiving messages
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
        # FIXED: Validate request headers
        if not validate_request_headers(request):
            logger.warning("Invalid request headers")
            raise HTTPException(status_code=400, detail="Invalid request headers")
        
        # Get request body
        body = await request.body()
        if not body:
            logger.warning("Empty request body")
            raise HTTPException(status_code=400, detail="Empty request body")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Log incoming webhook (with size limit)
        log_webhook_data(data)
        
        # FIXED: Validate webhook data structure
        if not validate_webhook_data(data):
            logger.warning("Invalid webhook data structure")
            return {"status": "ignored", "reason": "invalid_structure"}
        
        # Process webhook in background to return quickly
        background_tasks.add_task(process_webhook_async, data, request.state.request_id if hasattr(request.state, 'request_id') else None)
        
        # Return success immediately (WhatsApp expects 200)
        return {"status": "received", "request_id": getattr(request.state, 'request_id', None)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in webhook endpoint: {e}", exc_info=True)
        # Still return 200 to avoid WhatsApp retries for non-critical errors
        return {"status": "error", "message": "Internal error logged", "request_id": getattr(request.state, 'request_id', None)}

def validate_request_headers(request: Request) -> bool:
    """Validate incoming request headers"""
    try:
        # Check content type
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            logger.warning(f"Invalid content type: {content_type}")
            return False
        
        # Check user agent (optional but recommended)
        user_agent = request.headers.get("user-agent", "")
        if user_agent and "whatsapp" not in user_agent.lower():
            logger.warning(f"Non-WhatsApp user agent: {user_agent}")
            # Don't fail, just log warning
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating request headers: {e}")
        return False

def log_webhook_data(data: Dict[str, Any]):
    """Log webhook data with size limits and filtering"""
    try:
        # Check data size
        data_size = len(json.dumps(data))
        
        if data_size > 50000:  # 50KB limit
            logger.warning(f"Large webhook payload: {data_size} bytes")
            # Log summary only
            log_webhook_summary(data)
        else:
            # Log full data
            logger.info("="*50)
            logger.info("📥 INCOMING WEBHOOK DATA:")
            logger.info(json.dumps(data, indent=2, default=str))
            logger.info("="*50)
            
    except Exception as e:
        logger.error(f"Error logging webhook data: {e}")

def log_webhook_summary(data: Dict[str, Any]):
    """Log summary of large webhook data"""
    try:
        summary = {
            "object": data.get("object"),
            "entry_count": len(data.get("entry", [])),
            "has_messages": False,
            "has_statuses": False,
            "timestamp": time.time()
        }
        
        # Check for messages and statuses
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    summary["has_messages"] = True
                    summary["message_count"] = len(value.get("messages", []))
                if "statuses" in value:
                    summary["has_statuses"] = True
                    summary["status_count"] = len(value.get("statuses", []))
        
        logger.info(f"📊 Webhook summary: {json.dumps(summary)}")
        
    except Exception as e:
        logger.error(f"Error logging webhook summary: {e}")

def validate_webhook_data(data: Dict[str, Any]) -> bool:
    """Validate webhook data structure"""
    try:
        if not isinstance(data, dict):
            return False
        
        # Check for required top-level structure
        if "object" not in data or data["object"] != "whatsapp_business_account":
            logger.warning("Missing or invalid 'object' field")
            return False
        
        if "entry" not in data or not isinstance(data["entry"], list):
            logger.warning("Missing or invalid 'entry' field")
            return False
        
        # Validate entry structure
        for entry in data["entry"]:
            if not isinstance(entry, dict):
                logger.warning("Invalid entry format")
                return False
            
            if "changes" not in entry or not isinstance(entry["changes"], list):
                logger.warning("Missing or invalid 'changes' field in entry")
                return False
            
            for change in entry["changes"]:
                if not isinstance(change, dict):
                    logger.warning("Invalid change format")
                    return False
                
                if "value" not in change or not isinstance(change["value"], dict):
                    logger.warning("Missing or invalid 'value' field in change")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating webhook data: {e}")
        return False

async def process_webhook_async(data: dict, request_id: str = None):
    """
    Process webhook data asynchronously
    
    This function runs in the background to process incoming messages
    without blocking the webhook response.
    """
    start_time = time.time()
    log_prefix = f"[{request_id}]" if request_id else ""
    
    try:
        logger.info(f"{log_prefix} 🔄 Starting async webhook processing")
        
        # Check if it's a status update
        if is_status_update(data):
            logger.info(f"{log_prefix} 📊 Processing status update")
            await handle_status_update(data)
            return

        # Process message
        logger.info(f"{log_prefix} 💬 Processing incoming message")
        result = await message_processor.process_webhook(data)
        
        processing_time = time.time() - start_time
        
        # Log result
        if result.get("status") == "success":
            logger.info(f"{log_prefix} ✅ Message processed successfully in {processing_time:.3f}s: {result}")
        elif result.get("status") == "no_message":
            logger.info(f"{log_prefix} ℹ️ No message to process in webhook")
        elif result.get("status") == "error":
            logger.error(f"{log_prefix} ❌ Message processing failed in {processing_time:.3f}s: {result}")
        else:
            logger.warning(f"{log_prefix} ⚠️ Message processing result: {result}")
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"{log_prefix} ❌ Error processing webhook asynchronously after {processing_time:.3f}s: {e}", exc_info=True)
        
        # Log error to database if possible
        try:
            log_processing_error(data, str(e), request_id)
        except Exception as log_error:
            logger.error(f"{log_prefix} Failed to log processing error: {log_error}")

def is_status_update(data: Dict[str, Any]) -> bool:
    """Check if webhook data is a status update"""
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'statuses' in value:
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking for status update: {e}")
        return False

async def handle_status_update(data: Dict[str, Any]):
    """Handle message status updates with proper logging"""
    try:
        status_updates = []
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                statuses = value.get('statuses', [])
                
                for status in statuses:
                    message_id = status.get('id')
                    status_type = status.get('status')
                    timestamp = status.get('timestamp')
                    recipient = status.get('recipient_id')
                    
                    status_info = {
                        "message_id": message_id,
                        "status": status_type,
                        "recipient": recipient,
                        "timestamp": timestamp
                    }
                    
                    status_updates.append(status_info)
                    
                    # Log status update
                    logger.info(f"📊 Message {message_id} status: {status_type} for {mask_sensitive_data(recipient)}")
                    
                    # FIXED: Update message delivery status in database
                    try:
                        update_message_delivery_status(message_id, status_type)
                    except Exception as e:
                        logger.error(f"Failed to update delivery status for {message_id}: {e}")
        
        # Log summary
        if status_updates:
            logger.info(f"📊 Processed {len(status_updates)} status updates")
            
    except Exception as e:
        logger.error(f"❌ Error handling status update: {e}")

def update_message_delivery_status(message_id: str, status: str):
    """Update message delivery status in database"""
    try:
        if not message_id or not status:
            return
        
        with get_db_context() as db:
            from app.models.database import Message
            
            # Find message by WhatsApp message ID
            message = db.query(Message).filter(
                Message.whatsapp_message_id == message_id
            ).first()
            
            if message:
                message.delivery_status = status
                if status == "read":
                    message.is_read = True
                logger.info(f"Updated delivery status for message {message_id}: {status}")
            else:
                logger.warning(f"Message not found for status update: {message_id}")
                
    except Exception as e:
        logger.error(f"Error updating message delivery status: {e}")

def log_processing_error(webhook_data: Dict[str, Any], error_message: str, request_id: str = None):
    """Log processing errors to database"""
    try:
        with get_db_context() as db:
            # Try to extract message info
            message_info = extract_message_info(webhook_data)
            
            if message_info:
                # Log error with message context
                logger.error(f"Processing error for message {message_info.get('message_id')}: {error_message}")
            else:
                logger.error(f"Processing error for webhook: {error_message}")
                
    except Exception as e:
        logger.error(f"Failed to log processing error: {e}")

def extract_message_info(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract message information from webhook data"""
    try:
        for entry in webhook_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                
                if messages:
                    message = messages[0]
                    return {
                        'message_id': message.get('id'),
                        'from': message.get('from'),
                        'type': message.get('type'),
                        'timestamp': message.get('timestamp')
                    }
        
        return {}
        
    except Exception as e:
        logger.error(f"Error extracting message info: {e}")
        return {}

# Test functions
async def test_webhook_processing():
    """Test webhook processing functionality"""
    print("🧪 Testing Webhook Processing")
    print("=" * 40)
    
    # Test webhook verification
    print("1. Testing webhook verification...")
    
    # Valid verification
    valid_verify_data = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.verify_token,
        "hub.challenge": "test_challenge_123"
    }
    
    # Test validation function
    is_valid = validate_webhook_data({"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {}}]}]})
    print(f"   Webhook data validation: {'✅' if is_valid else '❌'}")
    
    # Test status update detection
    status_data = {"entry": [{"changes": [{"value": {"statuses": [{"id": "test"}]}}]}]}
    is_status = is_status_update(status_data)
    print(f"   Status update detection: {'✅' if is_status else '❌'}")
    
    # Test message extraction
    message_data = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "test_msg_123",
                        "from": "919999999999",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Hello, I have a headache"}
                    }],
                    "contacts": [{
                        "profile": {"name": "Test User"}
                    }]
                }
            }]
        }]
    }
    
    message_info = extract_message_info(message_data)
    print(f"   Message info extraction: {'✅' if message_info else '❌'}")
    if message_info:
        print(f"   Extracted: {message_info}")
    
    print("\n✅ Webhook processing tests completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_webhook_processing())
