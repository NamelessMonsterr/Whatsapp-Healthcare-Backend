"""
Check what's actually in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_database_stats():
    print("🔍 Checking Database Statistics")
    print("=" * 35)
    
    try:
        import requests
        
        # Get stats directly from API
        stats = requests.get('http://localhost:5000/stats').json()
        print(f"API Stats - Messages: {stats['totals']['messages']}")
        print(f"API Stats - Intents: {stats['intent_distribution']}")
        print(f"API Stats - Performance: {stats['model_performance']}")
        
        # Get health info
        health = requests.get('http://localhost:5000/health/detailed').json()
        print(f"Models loaded: {health['ml_models']['models_loaded']}")
        
        # Check if there are any messages at all
        print(f"\nTotal messages in system: {stats['totals']['messages']}")
        
        if stats['totals']['messages'] > 0:
            print("✅ Messages are being processed!")
            if stats['intent_distribution']:
                print("✅ Intent distribution populated!")
            else:
                print("⚠️  Intent distribution empty - checking why...")
        else:
            print("❌ No messages processed")
            
    except Exception as e:
        print(f"❌ Error checking stats: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_stats()