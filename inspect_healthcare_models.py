"""
Inspect healthcare_models to see what's actually there
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def inspect_healthcare_models():
    print("🔍 Inspecting healthcare_models.py")
    print("=" * 40)
    
    try:
        import app.ml.healthcare_models as hm
        print(f"✅ Module imported successfully")
        print(f"Module file: {hm.__file__}")
        print(f"Module attributes: {dir(hm)}")
        
        # Check what's available
        available_items = [item for item in dir(hm) if not item.startswith('_')]
        print(f"\nAvailable items: {available_items}")
        
        # Look for service instances or classes
        service_candidates = [item for item in available_items if 'service' in item.lower() or 'processor' in item.lower() or 'model' in item.lower()]
        print(f"Service candidates: {service_candidates}")
        
        # Try to access the healthcare service
        if hasattr(hm, 'healthcare_service'):
            service = getattr(hm, 'healthcare_service')
            print(f"\n✅ Found healthcare_service: {service}")
            print(f"Type: {type(service)}")
            
            # Check if it has the processing method
            if hasattr(service, 'process_healthcare_query'):
                print("✅ Has process_healthcare_query method")
                
                # Try to call it
                print("\nTesting direct call...")
                try:
                    result = service.process_healthcare_query("What are symptoms of diabetes?", "en")
                    print(f"✅ Direct call successful: {result}")
                except Exception as e:
                    print(f"❌ Direct call failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Missing process_healthcare_query method")
        else:
            print("❌ No healthcare_service found")
            
    except Exception as e:
        print(f"❌ Error importing module: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_healthcare_models()