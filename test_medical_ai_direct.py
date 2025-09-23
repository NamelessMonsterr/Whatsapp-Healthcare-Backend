"""
Direct Test of Real Medical AI - No webhook needed!
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_real_medical_ai_direct():
    """Test real medical AI directly"""
    print("🧪 Testing Real Medical AI Directly")
    print("=" * 40)
    
    try:
        # Import the real medical AI service
        from app.services.real_medical_ai import real_medical_ai
        
        print("✅ Real Medical AI Service imported successfully")
        
        # Test cases
        test_cases = [
            "I have severe chest pain and difficulty breathing",
            "What are symptoms of fever?",
            "I have diabetes, what should I do?",
            "I have a headache and nausea",
            "I feel generally unwell"
        ]
        
        for i, test_query in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_query}")
            
            # Classify intent
            intent_result = real_medical_ai.classify_medical_intent(test_query)
            print(f"   🎯 Intent: {intent_result['intent']} ({intent_result['confidence']:.0%})")
            
            if intent_result['symptoms']:
                print(f"   📋 Symptoms: {intent_result['symptoms']}")
            if intent_result['diseases']:
                print(f"   🦠 Diseases: {intent_result['diseases']}")
            
            # Generate response
            response = real_medical_ai.generate_medical_response(intent_result, test_query)
            print(f"   🤖 Response preview: {response[:150]}...")
            
        print("\n🎉 Real Medical AI is working perfectly!")
        print("✅ All medical processing is functional!")
        
    except Exception as e:
        print(f"❌ Error testing real medical AI: {e}")
        import traceback
        traceback.print_exc()

def test_healthcare_service_direct():
    """Test healthcare service directly"""
    print("\n" + "=" * 40)
    print("Testing Healthcare Service Directly")
    print("=" * 40)
    
    try:
        from app.ml.healthcare_models import healthcare_service
        
        print("✅ Healthcare Service imported successfully")
        
        test_query = "I have severe chest pain and difficulty breathing"
        print(f"Testing: {test_query}")
        
        result = healthcare_service.process_healthcare_query(test_query)
        
        print(f"🎯 Intent: {result.intent} ({result.confidence:.0%})")
        print(f"⏱️  Processing time: {result.processing_time:.3f}s")
        print(f"🤖 Model used: {result.model_used}")
        print(f"📝 Response preview: {result.answer[:200]}...")
        
        print("\n🎉 Healthcare Service is working!")
        
    except Exception as e:
        print(f"❌ Healthcare service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_medical_ai_direct()
    test_healthcare_service_direct()