"""
Simple AI Test - Direct test of healthcare service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simple_ai_test():
    print("🧪 Simple AI Test")
    print("=" * 30)
    
    try:
        # Try to import and test the healthcare service directly
        from app.ml.healthcare_models import HealthcareService
        
        print("✅ HealthcareService class imported")
        
        # Create service instance
        healthcare = HealthcareService()
        print("✅ Healthcare service created")
        
        # Test direct processing
        print("\nTesting direct query processing...")
        try:
            result = healthcare.process_healthcare_query("What are symptoms of diabetes?", "en")
            print(f"✅ Direct processing successful!")
            print(f"Result: {result}")
            print(f"Result type: {type(result)}")
            
            # Check if result has expected attributes
            if hasattr(result, 'intent'):
                print(f"Intent: {result.intent}")
            if hasattr(result, 'confidence'):
                print(f"Confidence: {result.confidence}")
            if hasattr(result, 'answer'):
                print(f"Answer: {result.answer}")
                
        except Exception as e:
            print(f"❌ Direct processing failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_ai_test()