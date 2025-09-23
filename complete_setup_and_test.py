"""
Final Debug Test - Shows exactly what's happening with AI processing
"""
import requests
import time
import uuid

def final_debug_test():
    print("🔍 FINAL DEBUG TEST - Checking AI Processing")
    print("=" * 50)
    
    # Check current status
    print("\n1. Current System Status:")
    health = requests.get('http://localhost:5000/health/detailed').json()
    stats = requests.get('http://localhost:5000/stats').json()
    
    print(f"Models loaded: {health['ml_models']['models_loaded']}")
    print(f"Current messages: {stats['totals']['messages']}")
    print(f"Current intents: {stats['intent_distribution']}")
    
    # Test with detailed monitoring
    print("\n2. Testing with detailed monitoring...")
    
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"debug_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    test_message = "I have severe chest pain and difficulty breathing. What should I do?"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "final_debug",
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
    
    # Monitor closely for 15 seconds
    print("\n3. Monitoring processing (15 seconds)...")
    for i in range(15):
        time.sleep(1)
        stats = requests.get('http://localhost:5000/stats').json()
        print(f"Second {i+1}: Messages={stats['totals']['messages']}, Intents={len(stats['intent_distribution'])}")
        
        if stats['intent_distribution'] or stats['model_performance']:
            print("🎉 AI ACTIVITY DETECTED!")
            print(f"Intents: {stats['intent_distribution']}")
            print(f"Performance: {stats['model_performance']}")
            break
    
    # Final check
    print("\n4. Final Results:")
    final_stats = requests.get('http://localhost:5000/stats').json()
    print(f"Total messages: {final_stats['totals']['messages']}")
    print(f"Intent distribution: {final_stats['intent_distribution']}")
    print(f"Model performance: {final_stats['model_performance']}")
    
    if final_stats['intent_distribution']:
        print("\n🎉 SUCCESS: AI is working!")
        for intent, count in final_stats['intent_distribution'].items():
            print(f"  - {intent}: {count}")
    else:
        print("\n⚠️  No AI activity detected")
        print("The models are loaded but not processing")
        print("This might be due to the session error we fixed earlier")

if __name__ == "__main__":
    final_debug_test()