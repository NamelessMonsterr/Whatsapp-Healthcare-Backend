"""
Inspect the healthcare service to see what's available
"""
import sys
import os

# Add the project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try to import and inspect the healthcare service
    from app.ml.healthcare_models import healthcare_service
    
    print("🏥 Healthcare Service Inspection")
    print(f"Service object: {healthcare_service}")
    print(f"Service type: {type(healthcare_service)}")
    
    # Check if it has the expected methods
    if hasattr(healthcare_service, 'process_healthcare_query'):
        print("✅ process_healthcare_query method exists")
    else:
        print("❌ process_healthcare_query method missing")
        
    # Try to call it directly
    try:
        result = healthcare_service.process_healthcare_query("What are symptoms of diabetes?", "en")
        print(f"Direct call result: {result}")
        print(f"Result type: {type(result)}")
    except Exception as e:
        print(f"Direct call failed: {e}")
        
except Exception as e:
    print(f"Error importing healthcare service: {e}")
    
    # Let's check what's in the healthcare_models module
    try:
        import app.ml.healthcare_models as hm
        print(f"\nHealthcare models module: {hm}")
        print(f"Module attributes: {dir(hm)}")
    except Exception as e2:
        print(f"Error importing module: {e2}")