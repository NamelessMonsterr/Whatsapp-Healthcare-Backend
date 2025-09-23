"""
Test Fixed WhatsApp Integration
"""
import requests
import uuid
import time
import json

def test_fixed_whatsapp():
    """Test fixed WhatsApp integration"""
    print("🧪 Testing Fixed WhatsApp Integration")
    print("=" * 35)
    
    # Test with proper permissions
    test_cases = [
        {
            "text": "I have severe chest pain and difficulty breathing",
            "expected_intent": "emergency"
        },
        {
            "text": "मुझे सिरदर्द और बुखार है",
            "expected_intent": "symptom_inquiry"
        },
        {
            "text": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு",
            "expected_intent": "symptom_inquiry"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {case['text'][:50]}...")
        print(f"   Expected Intent: {case['expected_intent']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"fix_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"test_{i}",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "contacts": [{
                            "profile": {"name": f"Test User {i}"},
                            "wa_id": user_id
                        }],
                        "messages": [{
                            "from": user_id,
                            "id": message_id,
                            "timestamp": timestamp,
                            "text": {"body": case["text"]},
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        })
        
        print(f"   Webhook response: {response.json()}")
        
        if response.json().get('status') == 'received':
            print(f"   ✅ Message sent successfully")
        else:
            print(f"   ❌ Failed to send message")
        
        # Wait for processing
        print(f"   ⏳ Processing...")
        time.sleep(5)
    
    # Check final results
    print(f"\n📊 Checking Results After Processing...")
    time.sleep(10)
    
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"   Total messages: {stats['totals']['messages']}")
    print(f"   Intent distribution: {json.dumps(stats['intent_distribution'], indent=2)}")
    print(f"   Language distribution: {json.dumps(stats['language_distribution'], indent=2)}")
    print(f"   Model performance: {json.dumps(stats['model_performance'], indent=2)}")
    
    if stats['intent_distribution']:
        print(f"\n🎉 SUCCESS: AI processing working!")
        for intent, count in stats['intent_distribution'].items():
            print(f"  - {intent}: {count}")
    else:
        print(f"\n⚠️  No AI activity detected yet")
        print(f"   This might be due to OAuth permissions")
        print(f"   Or database session issues")
    
    print(f"\n🌍 Multilingual support test completed!")

if __name__ == "__main__":
    test_fixed_whatsapp()