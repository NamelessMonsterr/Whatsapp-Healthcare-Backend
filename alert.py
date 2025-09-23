"""
Remove All Users EXCEPT Specified Phone Numbers
Keep only 7019567529 and 8341366211, remove everyone else
"""
import requests
import json
import time

def get_all_users():
    """Get list of all users in the system"""
    try:
        url = "http://localhost:5000/users/list?api_key=admin_secret_key_change_this"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json().get('users', [])
        else:
            print(f"❌ Failed to get user list: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting user list: {e}")
        return None

def remove_user_with_retry(phone_number, max_retries=3, timeout=60):
    """Remove user with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries} to remove {phone_number}...")
            
            # API endpoint to remove user
            url = f"http://localhost:5000/users/remove?api_key=admin_secret_key_change_this&phone={phone_number}"
            
            response = requests.delete(url, timeout=timeout)
            return response
            
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                print("  Retrying...")
                time.sleep(3)
                continue
            else:
                raise
                
        except Exception as e:
            print(f"  ❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("  Retrying...")
                time.sleep(3)
                continue
            else:
                raise

def remove_all_except_specified():
    """Remove all users except the two specified phone numbers"""
    print("🗑️  REMOVING ALL USERS EXCEPT SPECIFIED NUMBERS")
    print("=" * 55)
    
    # Numbers to KEEP (not remove)
    numbers_to_keep = [
        "7019567529",
        "8341366211"
    ]
    
    print(f"📱 Numbers to KEEP: {', '.join(numbers_to_keep)}")
    print("🗑️  All other numbers will be REMOVED")
    print("-" * 55)
    
    # Get all current users
    print("\n📋 Getting current user list...")
    all_users = get_all_users()
    
    if all_users is None:
        print("❌ Could not retrieve user list. Aborting.")
        return []
    
    print(f"📊 Total users in system: {len(all_users)}")
    
    # Filter users to remove (everyone except the numbers to keep)
    users_to_remove = []
    users_to_keep_found = []
    
    for user in all_users:
        user_phone = user.get('phone', '').strip()
        if user_phone in numbers_to_keep:
            users_to_keep_found.append(user_phone)
            print(f"✅ KEEPING: {user_phone}")
        else:
            users_to_remove.append(user_phone)
    
    print(f"\n📊 Users to KEEP: {len(users_to_keep_found)}")
    print(f"📊 Users to REMOVE: {len(users_to_remove)}")
    
    # Show which numbers we're keeping
    for kept_number in numbers_to_keep:
        if kept_number in users_to_keep_found:
            print(f"  ✅ {kept_number} - Found and will be kept")
        else:
            print(f"  ⚠️  {kept_number} - Not found in current users")
    
    if not users_to_remove:
        print("\n🎉 No users need to be removed!")
        return []
    
    print(f"\n🗑️  Removing {len(users_to_remove)} users...")
    print("-" * 40)
    
    removal_results = []
    successful_removals = 0
    
    for i, phone_number in enumerate(users_to_remove, 1):
        print(f"\n[{i}/{len(users_to_remove)}] Removing: {phone_number}")
        
        try:
            response = remove_user_with_retry(phone_number)
            
            if response.status_code == 200:
                print(f"  ✅ Successfully removed {phone_number}")
                successful_removals += 1
                removal_results.append({
                    "phone": phone_number,
                    "status": "removed",
                    "response": response.json() if response.content else {}
                })
            elif response.status_code == 404:
                print(f"  ⚠️  {phone_number} not found (already removed?)")
                removal_results.append({
                    "phone": phone_number,
                    "status": "not_found"
                })
            else:
                print(f"  ❌ Failed to remove {phone_number} - Status: {response.status_code}")
                removal_results.append({
                    "phone": phone_number,
                    "status": "failed",
                    "error": response.text
                })
                
        except Exception as e:
            print(f"  ❌ Error removing {phone_number}: {e}")
            removal_results.append({
                "phone": phone_number,
                "status": "error",
                "error": str(e)
            })
    
    print(f"\n📊 REMOVAL COMPLETED")
    print(f"✅ Successfully removed: {successful_removals}")
    print(f"❌ Failed to remove: {len(users_to_remove) - successful_removals}")
    
    return removal_results

def verify_final_state():
    """Verify that only the specified numbers remain"""
    print("\n🔍 VERIFYING FINAL STATE")
    print("=" * 30)
    
    try:
        users = get_all_users()
        if users is None:
            print("❌ Could not verify final state")
            return
        
        print(f"📊 Total users remaining: {len(users)}")
        
        numbers_to_keep = ["7019567529", "8341366211"]
        
        remaining_phones = [user.get('phone', '').strip() for user in users]
        
        print("\n📱 Remaining users:")
        for phone in remaining_phones:
            if phone in numbers_to_keep:
                print(f"  ✅ {phone} (SHOULD BE KEPT)")
            else:
                print(f"  ⚠️  {phone} (UNEXPECTED - should have been removed)")
        
        # Check if all numbers to keep are present
        print("\n🎯 Verification Results:")
        for number in numbers_to_keep:
            if number in remaining_phones:
                print(f"  ✅ {number} - Present (CORRECT)")
            else:
                print(f"  ❌ {number} - Missing (ERROR)")
        
        # Check for unexpected users
        unexpected_users = [phone for phone in remaining_phones if phone not in numbers_to_keep]
        if unexpected_users:
            print(f"\n⚠️  Found {len(unexpected_users)} unexpected users still in system:")
            for phone in unexpected_users:
                print(f"    {phone}")
        else:
            print("\n✅ Perfect! Only the specified numbers remain in the system.")
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")

def batch_remove_except_specified():
    """Alternative batch removal method if available"""
    print("\n🔄 TRYING BATCH REMOVAL METHOD")
    print("=" * 35)
    
    try:
        # Get all users first
        all_users = get_all_users()
        if not all_users:
            print("❌ Could not get user list for batch removal")
            return
        
        numbers_to_keep = ["7019567529", "8341366211"]
        users_to_remove = [
            user.get('phone', '').strip() 
            for user in all_users 
            if user.get('phone', '').strip() not in numbers_to_keep
        ]
        
        if not users_to_remove:
            print("✅ No users need to be removed!")
            return
        
        url = "http://localhost:5000/users/batch-remove?api_key=admin_secret_key_change_this"
        
        payload = {
            "phone_numbers": users_to_remove,
            "reason": "Keep only specified admin numbers"
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            print("✅ Batch removal successful!")
            print(f"Removed {len(users_to_remove)} users")
            return True
        else:
            print(f"❌ Batch removal failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Batch removal not available: {e}")
        return False

if __name__ == "__main__":
    print("🚀 REMOVE ALL USERS EXCEPT SPECIFIED NUMBERS")
    print("=" * 50)
    print("📱 KEEPING ONLY: 7019567529 and 8341366211")
    print("🗑️  REMOVING: All other users")
    print("=" * 50)
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will remove ALL users except the two specified numbers!")
    confirm = input("Type 'YES' to proceed with removal: ").strip().upper()
    
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        exit()
    
    # Try batch removal first
    print("\n🔄 Attempting batch removal...")
    batch_success = batch_remove_except_specified()
    
    if not batch_success:
        print("\n🔄 Batch removal failed or unavailable. Using individual removal...")
        # Individual removal
        results = remove_all_except_specified()
    
    # Verify final state
    time.sleep(2)
    verify_final_state()
    
    print("\n🎉 USER CLEANUP COMPLETED!")
    print("📱 Only 7019567529 and 8341366211 should remain in the system.")
    print("🔔 These two numbers will continue to receive all alerts.")