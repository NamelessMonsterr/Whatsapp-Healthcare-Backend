"""
Send Admin Alerts to Users - COMPLETE FIXED VERSION
"""
import requests
import json
import urllib.parse
import time

# Increase timeout and add retry logic
def send_alert_with_retry(url, method="POST", max_retries=3, timeout=120):
    """Send alert with retry logic and increased timeout"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            if method == "POST":
                response = requests.post(url, timeout=timeout)
            else:
                response = requests.get(url, timeout=timeout)
                
            return response
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)  # Wait before retry
                continue
            else:
                raise
                
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)  # Wait before retry
                continue
            else:
                raise

def test_alert_system():
    """Test alert system with proper timeout"""
    print("🧪 Testing Alert System with Increased Timeout")
    print("=" * 45)
    
    # Test health endpoint first
    try:
        health_url = "http://localhost:5000/health/detailed"
        print("Testing health endpoint...")
        response = requests.get(health_url, timeout=30)
        print(f"Health Status: {response.status_code}")
        health_data = response.json()
        print(f"Models loaded: {health_data['ml_models']['models_loaded']}")
        
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return
    
    # Test alert with increased timeout
    print("\nTesting alert system...")
    try:
        alert_url = "http://localhost:5000/alerts/test"
        response = send_alert_with_retry(alert_url, method="GET", timeout=60)
        print(f"Alert Test Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ Alert test failed: {e}")
        return

def send_broadcast_alert():
    """Send broadcast alert with proper timeout"""
    print("\n📢 Sending Broadcast Alert with Increased Timeout...")
    
    # Simple emergency message
    message = "🚨 HEALTH EMERGENCY ALERT\n\n⚠️  Dengue Outbreak Reported in Your Area\n\n📋 SYMPTOMS TO WATCH FOR:\n• High fever\n• Severe headache\n• Joint pain\n• Rash\n• Nausea\n• Vomiting\n\n🛡️  PREVENTIVE MEASURES:\n• Use mosquito repellent\n• Wear long sleeves\n• Eliminate standing water\n• Seek medical care early\n\n🏠 STAY HOME RECOMMENDATION:\n• Avoid crowded places\n• Practice social distancing\n• Wash hands frequently\n• Wear mask in public\n• Monitor your health\n\n📞 EMERGENCY CONTACTS:\n• Local Health Authority: [Contact Info]\n• Hospital Hotline: [Phone Number]\n• Government Helpline: 1075\n\n💡 This is an official health advisory. Please follow preventive measures and seek medical attention if symptoms develop."
    encoded_message = urllib.parse.quote(message)
    
    # URL with increased timeout
    url = f"http://localhost:5000/alerts/broadcast?api_key=admin_secret_key_change_this&message={encoded_message}&alert_type=emergency&priority=high"
    
    try:
        print("Sending alert (this may take 30-60 seconds)...")
        response = send_alert_with_retry(url, method="POST", timeout=120)
        print(f"Alert Status: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Broadcast alert sent successfully!")
            return response_data
        else:
            print("❌ Failed to send broadcast alert")
            return None
            
    except Exception as e:
        print(f"❌ Error sending broadcast alert: {e}")
        return None

def send_simple_health_alert():
    """Send simple health alert"""
    print("\n💊 Sending Simple Health Alert...")
    
    message = "💡 DAILY HEALTH TIP\n\n✅ HEALTHY LIFESTYLE TIPS:\n• Stay hydrated (8 glasses daily)\n• Exercise 30 minutes daily\n• Eat balanced nutritious meals\n• Get 7-8 hours quality sleep\n• Wash hands frequently\n• Take breaks from screens\n\n⚠️  WHEN TO CONSULT HEALTHCARE PROVIDER:\n• Persistent symptoms > 3 days\n• Unexplained weight changes\n• Chronic pain or discomfort\n• Abnormal vital signs\n• Concerning test results\n\n📞 Emergency: Call 108\n🏥 Routine Care: Contact your doctor\n💊 Pharmacy: For minor ailments\n\n💡 This is general guidance - individual needs vary!"
    encoded_message = urllib.parse.quote(message)
    
    url = f"http://localhost:5000/alerts/broadcast?api_key=admin_secret_key_change_this&message={encoded_message}&alert_type=health_tip&priority=normal"
    
    try:
        print("Sending health tip...")
        response = send_alert_with_retry(url, method="POST", timeout=120)
        print(f"Health Tip Status: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health tip sent successfully!")
            return response_data
        else:
            print("❌ Failed to send health tip")
            return None
            
    except Exception as e:
        print(f"❌ Error sending health tip: {e}")
        return None

if __name__ == "__main__":
    print("🚀 ADMIN ALERT SYSTEM - COMPLETE FIXED VERSION")
    print("=" * 50)
    
    # Test system first
    test_alert_system()
    
    # Send alerts
    send_broadcast_alert()
    send_simple_health_alert()
    
    print("\n🎉 Alert system test completed!")
    print("Check your WhatsApp for the alerts!")