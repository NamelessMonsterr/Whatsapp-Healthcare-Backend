"""
Create test users for admin alert testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import DatabaseManager, get_db_context
from app.models.database import User

def create_test_users():
    """Create test users for alert system"""
    print("🔧 Creating Test Users for Admin Alerts")
    print("=" * 40)
    
    db_manager = DatabaseManager()
    
    # Test users data
    test_users = [
        {
            "phone_number": "917019567529",  # Your WhatsApp number
            "name": "Main Admin User",
            "language_preference": "en",
            "is_active": True,
            "location": "Delhi"
        },
        {
            "phone_number": "918234567890",
            "name": "Test User 1", 
            "language_preference": "en",
            "is_active": True,
            "location": "Mumbai"
        },
        {
            "phone_number": "919876543210",
            "name": "Test User 2",
            "language_preference": "en",
            "is_active": True,
            "location": "Bangalore"
        }
    ]
    
    created_count = 0
    
    with get_db_context() as db:
        for user_data in test_users:
            try:
                # Check if user already exists
                existing_user = db.query(User).filter(
                    User.phone_number == user_data["phone_number"]
                ).first()
                
                if existing_user:
                    print(f"✅ User {user_data['phone_number']} already exists")
                    # Update existing user if needed
                    existing_user.name = user_data["name"]
                    existing_user.language_preference = user_data["language_preference"]
                    existing_user.is_active = user_data["is_active"]
                    existing_user.location = user_data.get("location", "")
                    db.commit()
                    db.refresh(existing_user)
                    continue
                
                # Create new user
                user = User(
                    phone_number=user_data["phone_number"],
                    name=user_data["name"],
                    language_preference=user_data["language_preference"],
                    is_active=user_data["is_active"],
                    location=user_data.get("location", "")
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                print(f"✅ Created user: {user.phone_number} - {user.name}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating user {user_data['phone_number']}: {e}")
                db.rollback()
    
    print(f"\n🎉 Created/Updated {created_count} test users!")
    return created_count

def list_all_users():
    """List all users in database"""
    print("\n📋 Listing All Users in Database")
    print("=" * 35)
    
    db_manager = DatabaseManager()
    
    with get_db_context() as db:
        try:
            users = db_manager.get_all_users(db)
            print(f"Total users in database: {len(users)}")
            
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user.phone_number}")
                print(f"     Name: {user.name}")
                print(f"     Active: {user.is_active}")
                print(f"     Language: {user.language_preference}")
                print(f"     Location: {user.location or 'Not set'}")
                print(f"     Last interaction: {user.last_interaction or 'Never'}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")

def test_user_queries():
    """Test different user query methods"""
    print("\n🧪 Testing User Query Methods")
    print("=" * 30)
    
    db_manager = DatabaseManager()
    
    with get_db_context() as db:
        try:
            # Test get_all_users
            all_users = db_manager.get_all_users(db)
            print(f"✅ get_all_users: {len(all_users)} users")
            
            # Test get_all_active_users
            active_users = db_manager.get_all_active_users(db)
            print(f"✅ get_all_active_users: {len(active_users)} users")
            
            # Test get_users_by_region
            delhi_users = db_manager.get_users_by_region(db, "Delhi")
            print(f"✅ get_users_by_region(Delhi): {len(delhi_users)} users")
            
            # Test get_recent_users
            recent_users = db_manager.get_recent_users(db, 24)
            print(f"✅ get_recent_users(24h): {len(recent_users)} users")
            
        except Exception as e:
            print(f"❌ Error testing user queries: {e}")

if __name__ == "__main__":
    create_test_users()
    list_all_users()
    test_user_queries()