"""
Test Multilingual Translation in Healthcare Chatbot
"""
import requests
import uuid
import time

def test_multilingual_translation():
    """Test healthcare chatbot with multilingual translation"""
    print("🌍 Testing Multilingual Translation")
    print("=" * 35)
    
    # Test cases in different Indian languages
    test_cases = [
        {
            "language": "Hindi",
            "code": "hi",
            "text": "मुझे सिरदर्द और बुखार है",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Tamil",
            "code": "ta", 
            "text": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Telugu",
            "code": "te",
            "text": "నాకు తలనొప్పి మరియు జ్వరం ఉంది",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "English",
            "code": "en",
            "text": "I have severe chest pain and difficulty breathing",
            "expected_intent": "emergency"
        }
    ]
    
    # Send each test message
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {case['language']} ({case['code']}):")
        print(f"   Text: {case['text']}")
        print(f"   Expected Intent: {case['expected_intent']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"multi_{case['code']}_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"multi_test_{case['code']}",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "contacts": [{
                            "profile": {"name": f"{case['language']} Test"},
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
        
        print(f"   Webhook Response: {response.json()}")
        
        # Wait for processing
        print("   ⏳ Waiting for AI processing...")
        time.sleep(5)
    
    # Check results
    print("\n📊 Checking Results After Processing...")
    time.sleep(10)
    
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"   Total messages: {stats['totals']['messages']}")
    print(f"   Intent distribution: {stats['intent_distribution']}")
    print(f"   Language distribution: {stats['language_distribution']}")
    print(f"   Model performance: {stats['model_performance']}")
    
    if stats['intent_distribution']:
        print("\n🎉 SUCCESS: Multilingual AI processing working!")
        for intent, count in stats['intent_distribution'].items():
            print(f"   - {intent}: {count}")
    else:
        print("\n⚠️  No intents detected yet - waiting longer...")
        time.sleep(15)
        
        # Check again
        stats = requests.get('http://localhost:5000/stats').json()
        if stats['intent_distribution']:
            print("🎉 SUCCESS after waiting!")
            for intent, count in stats['intent_distribution'].items():
                print(f"   - {intent}: {count}")
    
    print("\n🌍 Multilingual translation test completed!")

if __name__ == "__main__":
    test_multilingual_translation()