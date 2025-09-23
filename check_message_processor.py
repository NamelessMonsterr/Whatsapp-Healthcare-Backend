"""
Check and fix message processor
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_message_processor():
    print("🔧 Checking Message Processor")
    print("=" * 35)
    
    try:
        from app.services.message_processor import MessageProcessor
        processor = MessageProcessor()
        print("✅ MessageProcessor created successfully")
        print(f"Processor attributes: {dir(processor)}")
        
        # Check if it has the healthcare service
        if hasattr(processor, 'healthcare'):
            healthcare = processor.healthcare
            print(f"✅ Healthcare service found: {type(healthcare)}")
            
            # Test if it can process
            if hasattr(healthcare, 'process_healthcare_query'):
                print("✅ Healthcare service has process_healthcare_query method")
                
                # Test direct call
                try:
                    result = healthcare.process_healthcare_query("Test query", "en")
                    print(f"✅ Direct healthcare call works: {type(result)}")
                except Exception as e:
                    print(f"❌ Direct healthcare call failed: {e}")
            else:
                print("❌ Healthcare service missing process_healthcare_query method")
        else:
            print("❌ No healthcare service in processor")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_message_processor()