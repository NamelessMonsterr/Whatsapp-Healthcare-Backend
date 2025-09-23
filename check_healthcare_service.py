"""
Check what's in the healthcare service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.ml.healthcare_models import healthcare_service
    print("🏥 Healthcare Service Check")
    print(f"Service: {healthcare_service}")
    print(f"Type: {type(healthcare_service)}")
    print(f"Attributes: {dir(healthcare_service)}")
    
    # Try to call the method directly
    if hasattr(healthcare_service, 'process_healthcare_query'):
        print("\n✅ process_healthcare_query method exists")
        try:
            result = healthcare_service.process_healthcare_query("What are symptoms of diabetes?", "en")
            print(f"Direct call result: {result}")
        except Exception as e:
            print(f"❌ Direct call failed: {e}")
    else:
        print("❌ process_healthcare_query method missing")
        
except Exception as e:
    print(f"❌ Error: {e}")