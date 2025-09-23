"""
Test update_message_ml_data method directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_update_ml_data():
    print("🧪 Testing update_message_ml_data Method")
    print("=" * 40)
    
    try:
        from app.core.database import DatabaseManager, get_db_context
        import uuid
        
        db_manager = DatabaseManager()
        
        # Create test data
        user_id = f"test_user_{uuid.uuid4().hex[:6]}"
        message_id = f"test_msg_{uuid.uuid4().hex[:6]}"
        
        with get_db_context() as db:
            # Create user
            user = db_manager.create_user(db, user_id, "Test User")
            
            # Create conversation
            conversation = db_manager.get_or_create_active_conversation(db, user.id)
            
            # Save initial message
            message = db_manager.save_message(
                db,
                conversation.id,
                message_id,
                'user',
                "Test message for ML data",
                message_type='text'
            )
            
            print(f"✅ Initial message saved: {message_id}")
            print(f"   Before update - Intent: {message.detected_intent}")
            print(f"   Before update - Confidence: {message.confidence_score}")
            
            # Test update_message_ml_data
            print("\nTesting update_message_ml_data...")
            db_manager.update_message_ml_data(
                db,
                message_id,
                detected_language='en',
                detected_intent='test_intent',
                confidence_score=0.95
            )
            
            print("✅ update_message_ml_data called successfully")
            
            # Verify the update
            updated_message = db.query(message.__class__).filter(message.__class__.message_id == message_id).first()
            print(f"   After update - Intent: {updated_message.detected_intent}")
            print(f"   After update - Language: {updated_message.detected_language}")
            print(f"   After update - Confidence: {updated_message.confidence_score}")
            
            if updated_message.detected_intent == 'test_intent':
                print("🎉 ML data update working correctly!")
            else:
                print("❌ ML data update not working")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_ml_data()