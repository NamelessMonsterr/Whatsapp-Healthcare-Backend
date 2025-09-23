"""
Test Indian Language Support in Healthcare Chatbot
"""
import requests
import uuid
import time

def test_indian_languages():
    """Test healthcare chatbot with Indian languages"""
    print("🇮🇳 Testing Indian Language Support")
    print("=" * 35)
    
    # Indian language test cases
    test_cases = [
        {
            "language": "Hindi",
            "code": "hi",
            "text": "मुझे सिरदर्द और बुखार है",
            "translation": "I have headache and fever"
        },
        {
            "language": "Tamil", 
            "code": "ta",
            "text": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு",
            "translation": "I have headache and fever"
        },
        {
            "language": "Telugu",
            "code": "te", 
            "text": "నాకు తలనొప్పి మరియు జ్వరం ఉంది",
            "translation": "I have headache and fever"
        },
        {
            "language": "Marathi",
            "code": "mr",
            "text": "मला डोकेदुखी आणि ताप आहे",
            "translation": "I have headache and fever"
        },
        {
            "language": "Bengali",
            "code": "bn",
            "text": "আমার মাথাব্যথা এবং জ্বর আছে",
            "translation": "I have headache and fever"
        },
        {
            "language": "English",
            "code": "en",
            "text": "I have severe chest pain and difficulty breathing",
            "translation": "Emergency case"
        }
    ]
    
    # Send each test message
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {case['language']} ({case['code']}):")
        print(f"   Text: {case['text']}")
        print(f"   Translation: {case['translation']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"lang_{case['code']}_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"lang_test_{case['code']}",
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
        
        print(f"   Response: {response.json()['status']}")
        
        # Wait for processing
        time.sleep(3)
    
    # Check results
    print("\n📊 Checking results after processing...")
    time.sleep(10)
    
    stats = requests.get('http://localhost:5000/stats').json()
    print(f"Total messages: {stats['totals']['messages']}")
    print(f"Intent distribution: {stats['intent_distribution']}")
    print(f"Language distribution: {stats['language_distribution']}")
    print(f"Model performance: {stats['model_performance']}")
    
    if stats['intent_distribution']:
        print("\n🎉 SUCCESS: AI processing working!")
        for intent, count in stats['intent_distribution'].items():
            print(f"  - {intent}: {count}")
    else:
        print("\n⚠️  No intents detected yet - waiting longer...")
        time.sleep(10)
        
        # Check again
        stats = requests.get('http://localhost:5000/stats').json()
        if stats['intent_distribution']:
            print("🎉 SUCCESS after waiting!")
            for intent, count in stats['intent_distribution'].items():
                print(f"  - {intent}: {count}")

if __name__ == "__main__":
    test_indian_languages()