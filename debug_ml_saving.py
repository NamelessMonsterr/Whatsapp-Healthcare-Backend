"""
Debug ML data saving issue
"""
import requests
import time
import uuid

def debug_ml_saving():
    print("🔍 Debugging ML Data Saving")
    print("=" * 30)
    
    # Send a test message
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"debug_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "What are symptoms of fever?"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "debug_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Debug Test"},
                        "wa_id": user_id
                    }],
                    "messages": [{
                        "from": user_id,
                        "id": message_id,
                        "timestamp": timestamp,
                        "text": {"body": test_message},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    })
    
    print(f"Webhook response: {response.json()}")
    
    # Wait and check database directly
    print("\nWaiting 5 seconds...")
    time.sleep(5)
    
    # Check database directly
    import sqlite3
    try:
        conn = sqlite3.connect('./healthcare.db')
        cursor = conn.cursor()
        
        # Check the specific message we just sent
        cursor.execute("SELECT detected_intent, detected_language, confidence_score FROM messages WHERE message_id = ?", (message_id,))
        result = cursor.fetchone()
        
        if result:
            intent, language, confidence = result
            print(f"✅ Message found in database!")
            print(f"   Intent: {intent}")
            print(f"   Language: {language}")  
            print(f"   Confidence: {confidence}")
        else:
            print("❌ Message not found in database")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    debug_ml_saving()