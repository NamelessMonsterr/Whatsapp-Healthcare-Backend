"""
Check actual database content directly
"""
import sqlite3
import os

def check_actual_database():
    print("🔍 Checking Actual Database Content")
    print("=" * 35)
    
    try:
        # Connect to database
        conn = sqlite3.connect('./healthcare.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"Users: {user_count}")
        
        # Check conversations
        cursor.execute("SELECT COUNT(*) FROM conversations;")
        conv_count = cursor.fetchone()[0]
        print(f"Conversations: {conv_count}")
        
        # Check messages
        cursor.execute("SELECT COUNT(*) FROM messages;")
        msg_count = cursor.fetchone()[0]
        print(f"Messages: {msg_count}")
        
        # Check message details
        cursor.execute("SELECT id, detected_intent, detected_language, confidence_score FROM messages ORDER BY timestamp DESC LIMIT 5;")
        messages = cursor.fetchall()
        print(f"\nLatest messages:")
        for msg in messages:
            print(f"  - ID: {msg[0]}, Intent: {msg[1]}, Language: {msg[2]}, Confidence: {msg[3]}")
        
        conn.close()
        
        if msg_count > 0:
            print("\n🎉 Database is working and storing messages!")
            if any(msg[1] for msg in messages):  # Check if any message has intent
                print("✅ Intent detection is working and being stored!")
            else:
                print("⚠️  Messages stored but intents not detected")
        else:
            print("❌ No messages in database")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_actual_database()