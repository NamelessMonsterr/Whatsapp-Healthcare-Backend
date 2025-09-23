"""
Direct test to check if AI is working
"""
import requests
import time

def check_ai_direct():
    print("🔍 Direct AI Service Check")
    
    # Step 1: Check if models are actually loaded
    print("\n1. Checking model status...")
    try:
        health = requests.get('http://localhost:5000/health/detailed').json()
        models = health['ml_models']['models_loaded']
        print(f"Models status: {models}")
        
        if not any(models.values()):
            print("❌ Models not loaded - forcing reload...")
            reload_response = requests.post('http://localhost:5000/models/reload')
            print(f"Reload result: {reload_response.json()}")
            time.sleep(3)
            
            # Check again
            health = requests.get('http://localhost:5000/health/detailed').json()
            models = health['ml_models']['models_loaded']
            print(f"After reload: {models}")
        
    except Exception as e:
        print(f"Error checking health: {e}")
        return
    
    # Step 2: Test with a simple message to see what happens
    print("\n2. Testing message processing...")
    try:
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:6]}"
        message_id = f"test_{uuid.uuid4()}"
        timestamp = str(int(time.time()))
        
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "ai_test",
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
                            "text": {"body": "What are symptoms of fever?"},
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        })
        
        print(f"Webhook response: {response.json()}")
        
        # Wait and check results
        print("\n3. Checking results...")
        time.sleep(5)
        
        stats = requests.get('http://localhost:5000/stats').json()
        print(f"Messages: {stats['totals']['messages']}")
        print(f"Intents: {stats['intent_distribution']}")
        print(f"Model performance: {stats['model_performance']}")
        
        if stats['intent_distribution'] or stats['model_performance']:
            print("\n🎉 SUCCESS: AI is working!")
        else:
            print("\n⚠️  No AI activity detected")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    check_ai_direct()