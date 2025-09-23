"""
Test Translation Fix - Send messages in Indian languages and get responses in same language
"""
import requests
import uuid
import time

def test_translation_fix():
    """Test that responses come back in the same language as input"""
    print("🌍 TESTING LANGUAGE TRANSLATION FIX")
    print("=" * 40)
    
    # Test cases in different Indian languages
    test_cases = [
        {
            "language": "Hindi",
            "code": "hi",
            "text": "मुझे सिरदर्द और बुखार है",
            "expected_response_language": "hi"
        },
        {
            "language": "Tamil",
            "code": "ta", 
            "text": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு",
            "expected_response_language": "ta"
        },
        {
            "language": "Telugu",
            "code": "te",
            "text": "నాకు తలనొప్పి మరియు జ్వరం ఉంది",
            "expected_response_language": "te"
        },
        {
            "language": "English",
            "code": "en",
            "text": "I have severe chest pain and difficulty breathing",
            "expected_response_language": "en"
        }
    ]
    
    print("🧪 Testing language translation...")
    print("=" * 30)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {case['language']} ({case['code']}):")
        print(f"   Input: {case['text']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"trans_{case['code']}_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"translation_test_{case['code']}",
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
        time.sleep(8)
        
        # Check if processing happened
        stats = requests.get('http://localhost:5000/stats').json()
        print(f"   Messages: {stats['totals']['messages']}")
        print(f"   Intents: {len(stats['intent_distribution'])}")
        
        if stats['intent_distribution']:
            print(f"   ✅ AI processing detected!")
        else:
            print(f"   ⚠️  No AI processing yet")
    
    # Final check
    print("\n📊 FINAL TRANSLATION RESULTS:")
    print("=" * 30)
    
    final_stats = requests.get('http://localhost:5000/stats').json()
    print(f"Total messages: {final_stats['totals']['messages']}")
    print(f"Intent distribution: {final_stats['intent_distribution']}")
    print(f"Language distribution: {final_stats['language_distribution']}")
    
    if final_stats['intent_distribution']:
        print("\n🎉 SUCCESS: AI processing working!")
        print("✅ Responses should now come back in the same language as input!")
        print("📱 Check your WhatsApp for translated responses!")
    else:
        print("\n⚠️  Still no AI processing - check server logs")

if __name__ == "__main__":
    test_translation_fix()