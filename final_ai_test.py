import requests
import time
import uuid

def final_ai_test():
    print("🧪 Final AI Test After PyTorch Installation")
    
    # Test message
    user_id = f"user_{uuid.uuid4().hex[:6]}"
    message_id = f"final_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "I have severe chest pain and difficulty breathing"
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "final_ai_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "AI Test"},
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
    
    # Wait for AI processing (might take a few seconds first time)
    print("Waiting for AI processing...")
    time.sleep(10)
    
    # Check results
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"Messages: {stats['totals']['messages']}")
    print(f"Intents: {stats['intent_distribution']}")
    print(f"Model performance: {stats['model_performance']}")
    
    if stats['intent_distribution']:
        print("🎉 SUCCESS: AI is now working!")
        for intent, count in stats['intent_distribution'].items():
            print(f"  - {intent}: {count}")
    else:
        print("⚠️  Still no AI activity")

if __name__ == "__main__":
    final_ai_test()