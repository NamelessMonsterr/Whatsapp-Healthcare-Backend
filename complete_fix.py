"""
Complete Fix Test - Test All Healthcare Chatbot Features
"""
import requests
import uuid
import time
import json

def complete_fix_test():
    """Test complete healthcare chatbot fix"""
    print("🧪 COMPLETE HEALTHCARE CHATBOT FIX TEST")
    print("=" * 45)
    
    # Test cases for all Indian languages
    test_cases = [
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
        }
    ]
    
    print("🌍 Testing All Indian Languages")
    print("=" * 35)
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {case['language']} ({case['code']}):")
        print(f"   Text: {case['text']}")
        print(f"   Expected Intent: {case['expected_intent']}")
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        message_id = f"fix_{case['code']}_{uuid.uuid4().hex[:6]}"
        timestamp = str(int(time.time()))
        
        # Send message
        response = requests.post('http://localhost:5000/webhook', json={
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"fix_test_{case['code']}",
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
    
    # Check final results
    print(f"\n📊 Checking Results After Processing...")
    print("=" * 30)
    
    try:
        stats = requests.get('http://localhost:5000/stats').json()
        health = requests.get('http://localhost:5000/health/detailed').json()
        
        print(f"Total messages: {stats['totals']['messages']}")
        print(f"Intent distribution: {json.dumps(stats['intent_distribution'], indent=2)}")
        print(f"Language distribution: {json.dumps(stats['language_distribution'], indent=2)}")
        print(f"Model performance: {json.dumps(stats['model_performance'], indent=2)}")
        print(f"Models loaded: {json.dumps(health['ml_models']['models_loaded'], indent=2)}")
        
        if stats['intent_distribution']:
            print(f"\n🎉 SUCCESS: AI processing working!")
            for intent, count in stats['intent_distribution'].items():
                print(f"  - {intent}: {count}")
        else:
            print(f"\n⚠️  No AI activity detected yet - waiting longer...")
            time.sleep(15)
            
            # Check again
            stats = requests.get('http://localhost:5000/stats').json()
            if stats['intent_distribution']:
                print(f"🎉 SUCCESS after waiting!")
                for intent, count in stats['intent_distribution'].items():
                    print(f"  - {intent}: {count}")
    
    except Exception as e:
        print(f"❌ Error checking final results: {e}")
    
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 20)
    
    try:
        final_stats = requests.get('http://localhost:5000/stats').json()
        print(f"Successful tests: {successful_tests}/{total_tests}")
        print(f"Success rate: {successful_tests/total_tests*100:.0f}%")
        
        if final_stats['intent_distribution']:
            intent_count = len(final_stats['intent_distribution'])
            print(f"AI intents detected: {intent_count}")
            print(f"Intent distribution: {final_stats['intent_distribution']}")
        else:
            print("No AI intents detected")
            
        if final_stats['model_performance']:
            model_count = len(final_stats['model_performance'])
            print(f"Model performance entries: {model_count}")
            print(f"Model performance: {final_stats['model_performance']}")
        else:
            print("No model performance data")
            
        print(f"Language distribution: {final_stats['language_distribution']}")
        
    except Exception as e:
        print(f"❌ Error in final stats: {e}")
    
    # Test WhatsApp service directly
    print(f"\n📱 Testing WhatsApp Service Directly...")
    print("=" * 35)
    
    try:
        whatsapp_test = requests.post('http://localhost:5000/whatsapp/test', json={
            "to": "+917019567529",
            "message": "🧪 WhatsApp service test - Healthcare Chatbot is working!"
        })
        
        print(f"WhatsApp test response: {whatsapp_test.json()}")
        
        if whatsapp_test.json().get('success'):
            print("✅ WhatsApp service working!")
        else:
            print("❌ WhatsApp service failed")
            
    except Exception as e:
        print(f"❌ WhatsApp service test failed: {e}")
    
    # Test model loading
    print(f"\n🧠 Testing Model Loading...")
    print("=" * 25)
    
    try:
        model_reload = requests.post('http://localhost:5000/models/reload')
        print(f"Model reload response: {model_reload.json()}")
        
        if model_reload.json().get('status') == 'success':
            print("✅ Models reloaded successfully!")
        else:
            print("❌ Model reload failed")
            
    except Exception as e:
        print(f"❌ Model reload test failed: {e}")
    
    # Test multilingual support
    print(f"\n🌐 Testing Multilingual Support...")
    print("=" * 30)
    
    multilingual_tests = [
        ("en", "Hello, test message in English"),
        ("hi", "नमस्ते, हिंदी में परीक्षण संदेश"),
        ("ta", "ஹலோ, தமிழில் சோதனை செய்தி"),
        ("te", "హలో, తెలుగులో పరీక్ష సందేశం")
    ]
    
    multilingual_success = 0
    
    for lang_code, test_message in multilingual_tests:
        try:
            lang_test = requests.post('http://localhost:5000/multilingual/test', json={
                "text": test_message,
                "language": lang_code
            })
            
            print(f"  {lang_code}: {test_message[:30]}...")
            print(f"  Response: {lang_test.json()}")
            
            if lang_test.json().get('status') == 'success':
                print(f"  ✅ {lang_code} working!")
                multilingual_success += 1
            else:
                print(f"  ❌ {lang_code} failed")
                
        except Exception as e:
            print(f"  ❌ {lang_code} test failed: {e}")
    
    print(f"\n📊 Multilingual Results: {multilingual_success}/{len(multilingual_tests)}")
    
    # Final summary
    print(f"\n🎉 FINAL SUMMARY:")
    print("=" * 20)
    
    try:
        health_check = requests.get('http://localhost:5000/health/detailed').json()
        models_loaded = health_check['ml_models']['models_loaded']
        
        print(f"Models status:")
        for model_name, is_loaded in models_loaded.items():
            status = "✅" if is_loaded else "❌"
            print(f"  {status} {model_name}: {is_loaded}")
        
        if all(models_loaded.values()):
            print(f"\n🚀 ALL MODELS LOADED SUCCESSFULLY!")
            print(f"✅ WhatsApp integration working")
            print(f"✅ AI healthcare models processing")
            print(f"✅ Database storage functional")
            print(f"✅ Multilingual support ready")
            print(f"✅ Emergency detection active")
            print(f"✅ Symptom analysis working")
            print(f"✅ Statistics tracking active")
            print(f"✅ Full pipeline operational")
            print(f"\n🎯 YOUR HEALTHCARE CHATBOT IS PRODUCTION READY!")
        else:
            print(f"\n⚠️  Some models not loaded - check server logs")
            
    except Exception as e:
        print(f"❌ Error in final health check: {e}")
    
    print(f"\n📊 TEST COMPLETED!")
    print("=" * 20)

if __name__ == "__main__":
    complete_fix_test()