import requests
import time

def quick_test_after_install():
    print("🚀 Quick Test After Installation")
    
    # Check if PyTorch works
    try:
        import torch
        print(f"✅ PyTorch installed: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch error: {e}")
        return
    
    # Force model reload to use PyTorch
    print("Reloading models...")
    reload = requests.post('http://localhost:5000/models/reload')
    print(f"Reload result: {reload.json()}")
    
    time.sleep(3)
    
    # Test message
    import uuid
    response = requests.post('http://localhost:5000/webhook', json={
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "install_test",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{
                        "profile": {"name": "Install Test"},
                        "wa_id": "install_test_user"
                    }],
                    "messages": [{
                        "from": "install_test_user",
                        "id": f"test_{uuid.uuid4()}",
                        "timestamp": str(int(time.time())),
                        "text": {"body": "What are symptoms of diabetes?"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    })
    
    print(f"Response: {response.json()}")
    time.sleep(5)
    
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"Results - Messages: {stats['totals']['messages']}, Intents: {stats['intent_distribution']}")

if __name__ == "__main__":
    quick_test_after_install()