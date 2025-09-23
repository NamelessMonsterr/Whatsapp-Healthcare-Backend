"""
Complete AI Fix - Fixes session issues and ensures all models work
"""
import requests
import time
import uuid

def complete_ai_fix():
    print("🔧 COMPLETE AI FIX")
    print("=" * 40)
    
    # Step 1: Force complete model reload
    print("\n1. Forcing complete model reload...")
    try:
        reload_response = requests.post('http://localhost:5000/models/reload')
        print(f"Reload result: {reload_response.json()}")
    except Exception as e:
        print(f"❌ Reload failed: {e}")
        return
    
    # Wait for models to load
    print("Waiting for models to load...")
    time.sleep(5)
    
    # Step 2: Check model status
    print("\n2. Checking model status...")
    health = requests.get('http://localhost:5000/health/detailed').json()
    models = health['ml_models']['models_loaded']
    print(f"Models status: {models}")
    
    # Step 3: Test with a message that triggers biomedical model (most reliable)
    print("\n3. Testing with biomedical query...")
    
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    message_id = f"fix_{uuid.uuid4()}"
    timestamp = str(int(time.time()))
    
    # Use a query that should trigger the biomedical model
    test_message = "What are the symptoms of myocardial infarction?"
    
    print(f"Sending: {test_message}")
    
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "complete_fix",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Complete Fix Test"},
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
    
    # Monitor for 20 seconds (models might be slow first time)
    print("\n4. Monitoring for AI activity (20 seconds)...")
    for i in range(20):
        time.sleep(1)
        stats = requests.get('http://localhost:5000/stats').json()
        intents = stats['intent_distribution']
        performance = stats['model_performance']
        
        print(f"Second {i+1}: Intents={len(intents)}, Performance={len(performance)}")
        
        if intents or performance:
            print("🎉 AI ACTIVITY DETECTED!")
            print(f"Intents: {intents}")
            print(f"Performance: {performance}")
            return
    
    # Final check
    print("\n5. Final Results:")
    final_stats = requests.get('http://localhost:5000/stats').json()
    print(f"Total messages: {final_stats['totals']['messages']}")
    print(f"Intent distribution: {final_stats['intent_distribution']}")
    print(f"Model performance: {final_stats['model_performance']}")
    
    if final_stats['intent_distribution']:
        print("\n🎉 SUCCESS: AI is working!")
    else:
        print("\n❌ AI still not working")
        print("Possible issues:")
        print("1. Session management fix not applied properly")
        print("2. Healthcare service not working")
        print("3. Model loading issues")

if __name__ == "__main__":
    complete_ai_fix()