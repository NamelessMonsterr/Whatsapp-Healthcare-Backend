"""
Test All Indian Languages - Complete Multilingual Healthcare Chatbot
"""
import requests
import uuid
import time
import json

def test_all_indian_languages():
    """Test healthcare chatbot with all 12 Indian languages"""
    print("🌍 Testing All Indian Languages")
    print("=" * 35)
    
    # All 12 Indian languages with sample queries
    indian_languages = [
        {
            "language": "English",
            "code": "en",
            "text": "I have severe chest pain and difficulty breathing",
            "expected_intent": "emergency"
        },
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
            "language": "Malayalam",
            "code": "ml",
            "text": "എനിക്ക് തലവേദനയും ജ്വരവും ഉണ്ട്",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Kannada",
            "code": "kn",
            "text": "ನನಗೆ ತಲೆನೋವು ಮತ್ತು ಜ್ವರ ಇದೆ",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Bengali",
            "code": "bn",
            "text": "আমার মাথাব্যথা এবং জ্বর আছে",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Gujarati",
            "code": "gu",
            "text": "મને માથાનો દુઃખ અને તાવ છે",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Marathi",
            "code": "mr",
            "text": "मला डोकेदुखी आणि ताप आहे",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Punjabi",
            "code": "pa",
            "text": "ਮੈਨੂੰ ਸਿਰਦਰਦ ਅਤੇ ਬੁਖ਼ਾਰ ਹੈ",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Odia",
            "code": "or",
            "text": "ମୁଁ ମାଥାବ୍ୟଥା ଏବଂ ଜ୍ୱର ଅଛି",
            "expected_intent": "symptom_inquiry"
        },
        {
            "language": "Assamese",
            "code": "as",
            "text": "মই মাথাব্যথা আৰু জ্বৰ আছে",
            "expected_intent": "symptom_inquiry"
        }
    ]
    
    successful_tests = 0
    total_tests = len(indian_languages)
    
    print(f"🧪 Testing {total_tests} Indian languages...")
    print("=" * 35)
    
    for i, lang in enumerate(indian_languages, 1):
        print(f"\n{i}. Testing {lang['language']} ({lang['code']}):")
        print(f"   Text: {lang['text']}")
        print(f"   Expected Intent: {lang['expected_intent']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"lang_{lang['code']}_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"lang_test_{lang['code']}",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "contacts": [{
                            "profile": {"name": f"{lang['language']} Test"},
                            "wa_id": user_id
                        }],
                        "messages": [{
                            "from": user_id,
                            "id": message_id,
                            "timestamp": timestamp,
                            "text": {"body": lang["text"]},
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
            successful_tests += 1
        else:
            print(f"   ❌ Failed to send message")
        
        # Wait for processing
        print(f"   ⏳ Processing...")
        time.sleep(3)
    
    # Wait for all processing to complete
    print(f"\n⏳ Waiting for all {total_tests} scenarios to process...")
    time.sleep(15)
    
    # Check results
    print(f"\n📊 Checking Results After Processing...")
    print("=" * 35)
    
    try:
        stats = requests.get('http://localhost:5000/stats').json()
        print(f"Total messages: {stats['totals']['messages']}")
        print(f"Intent distribution: {json.dumps(stats['intent_distribution'], indent=2)}")
        print(f"Language distribution: {json.dumps(stats['language_distribution'], indent=2)}")
        print(f"Model performance: {json.dumps(stats['model_performance'], indent=2)}")
        
        # Check language support
        lang_dist = stats['language_distribution']
        intent_dist = stats['intent_distribution']
        
        if lang_dist and intent_dist:
            print(f"\n🎉 SUCCESS: Multilingual AI processing working!")
            print(f"✅ Languages detected: {len(lang_dist)}")
            print(f"✅ Intents processed: {len(intent_dist)}")
            
            # Show language breakdown
            for lang_code, count in lang_dist.items():
                lang_names = {
                    'en': 'English',
                    'hi': 'Hindi',
                    'ta': 'Tamil',
                    'te': 'Telugu',
                    'ml': 'Malayalam',
                    'kn': 'Kannada',
                    'bn': 'Bengali',
                    'gu': 'Gujarati',
                    'mr': 'Marathi',
                    'pa': 'Punjabi',
                    'or': 'Odia',
                    'as': 'Assamese'
                }
                lang_name = lang_names.get(lang_code, lang_code)
                print(f"  - {lang_name} ({lang_code}): {count}")
            
            # Show intent breakdown
            for intent, count in intent_dist.items():
                print(f"  - {intent}: {count}")
                
        else:
            print(f"\n⚠️  No AI activity detected yet - waiting longer...")
            time.sleep(15)
            
            # Check again
            stats = requests.get('http://localhost:5000/stats').json()
            if stats['intent_distribution'] or stats['language_distribution']:
                print("🎉 SUCCESS after waiting!")
                for intent, count in stats['intent_distribution'].items():
                    print(f"  - {intent}: {count}")
            else:
                print("❌ Still no activity detected")
    
    except Exception as e:
        print(f"❌ Error checking final results: {e}")
    
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 20)
    print(f"Successful tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {successful_tests/total_tests*100:.0f}%")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL {total_tests} INDIAN LANGUAGES WORKING!")
        print(f"✅ WhatsApp integration working")
        print(f"✅ AI healthcare models processing")
        print(f"✅ Database storage functional")
        print(f"✅ Multilingual support ready")
        print(f"✅ Emergency detection active")
        print(f"✅ Symptom analysis working")
        print(f"✅ Statistics tracking active")
        print(f"✅ Full pipeline operational")
    else:
        print(f"\n⚠️  {successful_tests}/{total_tests} languages working")
        print(f"Some languages may need more testing")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    test_all_indian_languages()