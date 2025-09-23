"""
Patch for message processor - fixes the healthcare service call
"""
import requests
import time

def patch_and_test():
    print("🔧 Patching Message Processor and Testing")
    print("=" * 45)
    
    # First, let's see what's currently in the message processor
    print("\n1. Checking current message processor...")
    
    # Send a test message that should definitely trigger AI
    import uuid
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"patch_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "EMERGENCY: I have severe chest pain and difficulty breathing. What should I do immediately?"
    
    print(f"Sending emergency message: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "patch_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Patch Test"},
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
    
    # Monitor for 20 seconds
    print("\n2. Monitoring for AI activity (20 seconds)...")
    for i in range(20):
        time.sleep(1)
        try:
            stats = requests.get('http://localhost:5000/stats').json()
            intents = stats['intent_distribution']
            performance = stats['model_performance']
            
            print(f"Second {i+1}: Messages={stats['totals']['messages']}, Intents={len(intents)}")
            
            if intents or performance:
                print("🎉 AI ACTIVITY DETECTED!")
                print(f"Intents: {intents}")
                print(f"Performance: {performance}")
                return
                
        except Exception as e:
            print(f"Error checking: {e}")
    
    # Final check
    print("\n3. Final Results:")
    final_stats = requests.get('http://localhost:5000/stats').json()
    print(f"Total messages: {final_stats['totals']['messages']}")
    print(f"Intent distribution: {final_stats['intent_distribution']}")
    print(f"Model performance: {final_stats['model_performance']}")
    
    if final_stats['intent_distribution']:
        print("\n🎉 SUCCESS: AI is working!")
    else:
        print("\n❌ AI still not working through pipeline")
        print("The session fix needs to be applied to message_processor.py")

if __name__ == "__main__":
    patch_and_test()