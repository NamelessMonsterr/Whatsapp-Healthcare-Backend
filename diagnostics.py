from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
import httpx
import json
import os
from datetime import datetime
import asyncio

app = FastAPI(title="WhatsApp Bot Diagnostic Tool")

# Configuration
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAJeAB9cxNMBPRN7ZAScsJiisTJkVUKiKMD1KfgcYfbQadnMxvZAQP7uwykWp782Ltu3u7hmVwnpvAS1tVt2x66P3pKF7bB80xFE0zsRRfv3X5w0FZCJgQSx5h3AlOba0RlGN3m5McczgMxkvEGZBRN4h97F9rIwQRQZBzIHKgIKEewtyOWJd7oEgCzEyB9UBWCZBcWlSm6U2WNSZB7VTBOjxKUi8MBht9x1H8dEo3zWFhlFPEZD")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "742954942242352")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "healthcare_bot_verify_secure_123")

# Logging storage
logs = []
request_count = 0

def log_message(level: str, message: str, data: dict = None):
    global logs
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "data": data
    }
    logs.append(log_entry)
    
    # Console output with colors
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    
    color = colors.get(level, colors["RESET"])
    print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")
    
    if data:
        print(f"   Data: {json.dumps(data, indent=2)}")
    
    # Keep only last 100 logs
    if len(logs) > 100:
        logs = logs[-100:]

@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    global request_count
    request_count += 1
    
    # Log basic request info
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "none")
    
    log_message("INFO", f"Request #{request_count}: {request.method} {request.url.path}", {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "headers": dict(request.headers)
    })
    
    response = await call_next(request)
    
    # Add headers to prevent ngrok browser warning
    response.headers["ngrok-skip-browser-warning"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    return response

@app.get("/", response_class=HTMLResponse)
async def diagnostic_dashboard():
    """Diagnostic dashboard with real-time status"""
    
    token_status = "✅ SET" if WHATSAPP_TOKEN != "YOUR_TOKEN_HERE" else "❌ NOT SET"
    phone_status = "✅ SET" if WHATSAPP_PHONE_NUMBER_ID != "YOUR_PHONE_ID_HERE" else "❌ NOT SET"
    
    recent_logs = logs[-10:] if logs else []
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Bot Diagnostic Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .status-good {{ color: #28a745; }}
            .status-bad {{ color: #dc3545; }}
            .status-warning {{ color: #ffc107; }}
            .logs {{ background: #000; color: #00ff00; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto; }}
            .test-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; }}
            .btn {{ padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; }}
            .btn:hover {{ background: #0056b3; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 WhatsApp Bot Diagnostic Dashboard</h1>
            
            <div class="card">
                <h2>📊 System Status</h2>
                <p><strong>WhatsApp Token:</strong> <span class="{'status-good' if token_status == '✅ SET' else 'status-bad'}">{token_status}</span></p>
                <p><strong>Phone Number ID:</strong> <span class="{'status-good' if phone_status == '✅ SET' else 'status-bad'}">{phone_status}</span></p>
                <p><strong>Verify Token:</strong> <span class="status-good">{VERIFY_TOKEN}</span></p>
                <p><strong>Total Requests:</strong> {request_count}</p>
                <p><strong>Server Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="card">
                <h2>🧪 Test Tools</h2>
                <div class="test-buttons">
                    <a href="/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token={VERIFY_TOKEN}" class="btn">Test Verification</a>
                    <a href="/logs" class="btn">View All Logs</a>
                    <a href="/test-webhook" class="btn">Test Webhook POST</a>
                    <a href="/health" class="btn">Health Check</a>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>📝 Recent Logs (Last 10)</h2>
                    <div class="logs">
                        {"<br>".join([f"[{log['timestamp']}] {log['level']}: {log['message']}" for log in recent_logs[-10:]]) if recent_logs else "No logs yet..."}
                    </div>
                </div>
                
                <div class="card">
                    <h2>📋 Instructions</h2>
                    <ol>
                        <li><strong>Set your tokens</strong> in environment variables</li>
                        <li><strong>Test verification</strong> using the button above</li>
                        <li><strong>Configure webhook</strong> in Meta Business Manager</li>
                        <li><strong>Send WhatsApp message</strong> to <code>+1 (555) 181-8482</code></li>
                        <li><strong>Watch logs</strong> in real-time below</li>
                    </ol>
                    
                    <h3>📱 WhatsApp Business Number</h3>
                    <p><code>+1 (555) 181-8482</code></p>
                    
                    <h3>🔗 Webhook URL</h3>
                    <p>Use this URL in Meta Business Manager:</p>
                    <p><code>https://your-ngrok-url.ngrok-free.app/webhook</code></p>
                </div>
            </div>
        </div>
        
        <script>
            // Auto refresh every 5 seconds
            setTimeout(() => location.reload(), 5000);
        </script>
    </body>
    </html>
    """
    
    return html_content

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Webhook verification endpoint"""
    
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    log_message("INFO", "Webhook verification attempt", {
        "mode": mode,
        "token_received": token,
        "token_expected": VERIFY_TOKEN,
        "challenge": challenge,
        "match": token == VERIFY_TOKEN
    })
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        log_message("SUCCESS", f"✅ Webhook verification successful! Returning challenge: {challenge}")
        return Response(content=challenge, media_type="text/plain")
    else:
        log_message("ERROR", "❌ Webhook verification failed!")
        return Response(content="Verification failed", status_code=400, media_type="text/plain")

@app.post("/webhook")
async def receive_webhook(request: Request):
    """Main webhook endpoint for receiving messages"""
    
    log_message("SUCCESS", "🚨 WEBHOOK POST REQUEST RECEIVED!")
    
    try:
        # Get raw body for debugging
        body = await request.body()
        log_message("INFO", f"Raw body length: {len(body)} bytes")
        
        # Parse JSON
        data = await request.json()
        log_message("INFO", "📥 Webhook payload received", data)
        
        # Process the webhook data
        await process_webhook_data(data)
        
        return {"status": "success", "timestamp": datetime.now().isoformat()}
        
    except json.JSONDecodeError as e:
        log_message("ERROR", f"❌ JSON decode error: {e}")
        return {"status": "error", "message": "Invalid JSON"}
    
    except Exception as e:
        log_message("ERROR", f"💥 Unexpected error: {e}")
        import traceback
        log_message("ERROR", "Full traceback", {"traceback": traceback.format_exc()})
        return {"status": "error", "message": str(e)}

async def process_webhook_data(data: dict):
    """Process WhatsApp webhook data"""
    
    if 'entry' not in data:
        log_message("WARNING", "No 'entry' field in webhook data")
        return
    
    for entry in data.get('entry', []):
        entry_id = entry.get('id', 'unknown')
        log_message("INFO", f"Processing entry: {entry_id}")
        
        for change in entry.get('changes', []):
            field = change.get('field', 'unknown')
            value = change.get('value', {})
            
            log_message("INFO", f"Processing change - field: {field}", value)
            
            # Handle messages
            if 'messages' in value:
                await process_messages(value['messages'])
            
            # Handle statuses
            if 'statuses' in value:
                await process_statuses(value['statuses'])
            
            # Handle other webhook types
            for key in value:
                if key not in ['messages', 'statuses', 'contacts', 'metadata']:
                    log_message("INFO", f"Other webhook data: {key}", {key: value[key]})

async def process_messages(messages: list):
    """Process incoming messages"""
    
    log_message("SUCCESS", f"💬 Found {len(messages)} message(s)!")
    
    for message in messages:
        msg_id = message.get('id', 'unknown')
        sender = message.get('from', 'unknown')
        msg_type = message.get('type', 'unknown')
        timestamp = message.get('timestamp', 'unknown')
        
        log_message("INFO", f"📨 Message {msg_id} from {sender}", {
            "type": msg_type,
            "timestamp": timestamp,
            "full_message": message
        })
        
        # Handle text messages
        if msg_type == 'text':
            text_body = message.get('text', {}).get('body', '')
            log_message("SUCCESS", f"💭 Text message: '{text_body}'")
            
            # Try to send reply if tokens are configured
            if WHATSAPP_TOKEN != "YOUR_TOKEN_HERE":
                await send_whatsapp_reply(sender, f"Echo: {text_body}")
            else:
                log_message("WARNING", "Cannot send reply - WhatsApp token not configured")
        
        # Handle other message types
        else:
            log_message("INFO", f"Received {msg_type} message")

async def process_statuses(statuses: list):
    """Process message status updates"""
    
    log_message("INFO", f"📊 Found {len(statuses)} status update(s)")
    
    for status in statuses:
        status_type = status.get('status', 'unknown')
        recipient_id = status.get('recipient_id', 'unknown')
        message_id = status.get('id', 'unknown')
        
        log_message("INFO", f"Status update: {status_type} for message {message_id} to {recipient_id}")

async def send_whatsapp_reply(to: str, message: str):
    """Send WhatsApp message reply"""
    
    log_message("INFO", f"📤 Attempting to send reply to {to}: '{message}'")
    
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN == "YOUR_TOKEN_HERE":
        log_message("ERROR", "Cannot send message - WhatsApp token not set")
        return False
    
    if not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_PHONE_NUMBER_ID == "YOUR_PHONE_ID_HERE":
        log_message("ERROR", "Cannot send message - Phone number ID not set")
        return False
    
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            log_message("INFO", "Sending request to WhatsApp API", {
                "url": url,
                "payload": payload
            })
            
            response = await client.post(url, json=payload, headers=headers)
            
            log_message("INFO", f"WhatsApp API response: {response.status_code}", {
                "status_code": response.status_code,
                "response_text": response.text,
                "headers": dict(response.headers)
            })
            
            if response.status_code == 200:
                log_message("SUCCESS", "✅ Message sent successfully!")
                return True
            else:
                log_message("ERROR", f"❌ Failed to send message: {response.status_code}")
                return False
                
    except Exception as e:
        log_message("ERROR", f"💥 Exception sending message: {e}")
        return False

@app.get("/test-webhook")
async def test_webhook():
    """Send a test webhook POST to ourselves"""
    
    test_data = {
        "entry": [{
            "id": "test-entry",
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "test-message-123",
                        "from": "1234567890",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Test message from diagnostic tool"}
                    }]
                },
                "field": "messages"
            }]
        }],
        "object": "whatsapp_business_account"
    }
    
    log_message("INFO", "🧪 Sending test webhook data to ourselves")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/webhook",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
        log_message("SUCCESS", f"✅ Test webhook sent, response: {response.status_code}")
        return {"status": "test_sent", "response_code": response.status_code}
        
    except Exception as e:
        log_message("ERROR", f"❌ Test webhook failed: {e}")
        return {"status": "test_failed", "error": str(e)}

@app.get("/logs")
async def get_logs():
    """Get all diagnostic logs"""
    return {
        "total_logs": len(logs),
        "logs": logs,
        "system_info": {
            "token_configured": WHATSAPP_TOKEN != "YOUR_TOKEN_HERE",
            "phone_id_configured": WHATSAPP_PHONE_NUMBER_ID != "YOUR_PHONE_ID_HERE",
            "verify_token": VERIFY_TOKEN,
            "request_count": request_count
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "whatsapp_token": "configured" if WHATSAPP_TOKEN != "YOUR_TOKEN_HERE" else "missing",
            "phone_number_id": "configured" if WHATSAPP_PHONE_NUMBER_ID != "YOUR_PHONE_ID_HERE" else "missing",
            "verify_token": VERIFY_TOKEN
        },
        "stats": {
            "total_requests": request_count,
            "total_logs": len(logs)
        }
    }

@app.get("/clear-logs")
async def clear_logs():
    """Clear all diagnostic logs"""
    global logs, request_count
    logs = []
    request_count = 0
    log_message("INFO", "🗑️ All logs cleared")
    return {"status": "logs_cleared"}

# Catch any other requests
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all_requests(request: Request, path: str):
    """Catch all other requests for debugging"""
    
    log_message("WARNING", f"🔍 Unexpected request to /{path}", {
        "method": request.method,
        "path": path,
        "query_params": dict(request.query_params)
    })
    
    return {
        "message": f"Caught {request.method} request to /{path}",
        "path": path,
        "method": request.method,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting WhatsApp Bot Diagnostic Server...")
    print("📊 Visit http://localhost:8000 for diagnostic dashboard")
    print("🔧 Configure your tokens in environment variables or update the code")
    print("=" * 60)
    
    log_message("INFO", "🚀 Diagnostic server starting...")
    log_message("INFO", f"Configuration check - Token: {'SET' if WHATSAPP_TOKEN != 'YOUR_TOKEN_HERE' else 'NOT SET'}")
    log_message("INFO", f"Configuration check - Phone ID: {'SET' if WHATSAPP_PHONE_NUMBER_ID != 'YOUR_PHONE_ID_HERE' else 'NOT SET'}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )