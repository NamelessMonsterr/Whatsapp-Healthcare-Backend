"""
Full Pipeline Test - Test AI through complete webhook pipeline
"""
import requests
import time
import uuid

def full_pipeline_test():
    print("🧪 Full Pipeline Test")
    print("=" * 30)
    
    # Test message that should trigger AI
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"pipeline_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "What are the symptoms of diabetes mellitus?"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "pipeline_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Pipeline Test"},
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
    
    # Monitor for 30 seconds (models might be slow first time)
    print("\nMonitoring for AI activity (30 seconds)...")
    for i in range(30):
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
            print(f"Error checking stats: {e}")
    
    # Final check
    print("\nFinal Results:")
    try:
        final_stats = requests.get('http://localhost:5000/stats').json()
        print(f"Total messages: {final_stats['totals']['messages']}")
        print(f"Intent distribution: {final_stats['intent_distribution']}")
        print(f"Model performance: {final_stats['model_performance']}")
        
        if final_stats['intent_distribution']:
            print("\n🎉 SUCCESS: AI is working through the full pipeline!")
        else:
            print("\n⚠️  AI works directly but not through pipeline")
            print("This suggests the session fix isn't working properly")
            
    except Exception as e:
        print(f"❌ Final check failed: {e}")

if __name__ == "__main__":
    full_pipeline_test()