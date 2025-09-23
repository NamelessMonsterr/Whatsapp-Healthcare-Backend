import requests
import uuid
import time

def final_test():
    print("🧪 Final AI Test")
    
    # Test message
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"msg_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "I have severe chest pain and difficulty breathing"
    
    print(f"Testing: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": f"entry_{uuid.uuid4().hex[:8]}",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Final Test User"},
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
    
    print(f"Response: {response.json()}")
    
    # Wait and check results
    time.sleep(5)
    
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"Messages: {stats['totals']['messages']}")
    print(f"Intents: {stats['intent_distribution']}")
    print(f"Model perf: {stats['model_performance']}")

if __name__ == "__main__":
    final_test()