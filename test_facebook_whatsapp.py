"""
Test Facebook WhatsApp Integration
"""
import requests
import uuid
import time

def test_facebook_whatsapp():
    """Test Facebook WhatsApp integration"""
    print("🧪 Testing Facebook WhatsApp Integration")
    print("=" * 40)
    
    # Test message
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"fb_{uuid.uuid4().hex[:6]}"
    timestamp = str(int(time.time()))
    
    test_message = "I have severe chest pain and difficulty breathing"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "fb_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "FB Test User"},
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
    
    # Wait for processing
    print("⏳ Waiting for processing...")
    time.sleep(10)
    
    # Check results
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"Messages: {stats['totals']['messages']}")
    print(f"Intents: {stats['intent_distribution']}")
    print(f"Model performance: {stats['model_performance']}")
    
    if stats['intent_distribution']:
        print("🎉 SUCCESS: Facebook WhatsApp is working!")
        for intent, count in stats['intent_distribution'].items():
            print(f"  - {intent}: {count}")
    else:
        print("⚠️  No intents detected yet - waiting longer...")
        time.sleep(15)
        
        # Check again
        stats = requests.get('http://localhost:5000/stats').json()
        if stats['intent_distribution']:
            print("🎉 SUCCESS after waiting!")
            for intent, count in stats['intent_distribution'].items():
                print(f"  - {intent}: {count}")

if __name__ == "__main__":
    test_facebook_whatsapp()