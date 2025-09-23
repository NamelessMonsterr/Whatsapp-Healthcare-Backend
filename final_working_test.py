import requests
import time
import uuid

def final_working_test():
    print("🎉 FINAL WORKING TEST")
    print("=" * 30)
    
    # Test message
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"final_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "What are the symptoms of diabetes?"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "final_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Final Test"},
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
    
    # Monitor for 15 seconds
    print("\nMonitoring for AI activity...")
    for i in range(15):
        time.sleep(1)
        try:
            stats = requests.get('http://localhost:5000/stats').json()
            intents = stats['intent_distribution']
            
            if intents:
                print("🎉 SUCCESS! AI IS WORKING!")
                print(f"Intents: {intents}")
                return
        except Exception as e:
            print(f"Error checking stats: {e}")
    
    # Final check
    try:
        final_stats = requests.get('http://localhost:5000/stats').json()
        print(f"\nFinal results: {final_stats['intent_distribution']}")
        
        if final_stats['intent_distribution']:
            print("🎉 YOUR AI HEALTHCARE CHATBOT IS WORKING!")
        else:
            print("❌ Still not working - check server logs for errors")
    except Exception as e:
        print(f"Final check failed: {e}")

if __name__ == "__main__":
    final_working_test()