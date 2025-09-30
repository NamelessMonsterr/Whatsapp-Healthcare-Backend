"""
Send Admin Alerts to Users - COMPLETE FIXED VERSION with Enhanced Features
"""
import requests
import json
import urllib.parse
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append('.')

def send_alert_with_retry(url: str, method: str = "POST", max_retries: int = 3, timeout: int = 120) -> Optional[requests.Response]:
    """Send alert with retry logic and increased timeout"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
            
            if method.upper() == "POST":
                response = requests.post(url, timeout=timeout)
            else:
                response = requests.get(url, timeout=timeout)
                
            return response

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                print("⏳ Retrying...")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
                continue
            else:
                print("❌ All retry attempts failed due to timeout")
                return None

        except requests.exceptions.ConnectionError as conn_error:
            print(f"🔗 Connection error on attempt {attempt + 1}: {conn_error}")
            if attempt < max_retries - 1:
                print("⏳ Retrying...")
                time.sleep(3 * (attempt + 1))
                continue
            else:
                print("❌ All retry attempts failed due to connection error")
                return None

        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("⏳ Retrying...")
                time.sleep(2 * (attempt + 1))
                continue
            else:
                print("❌ All retry attempts failed")
                return None

def check_server_health() -> bool:
    """Check if server is healthy before sending alerts"""
    try:
        health_url = "http://localhost:5000/health/detailed"
        print("🔍 Checking server health...")
        
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   WhatsApp: {'enabled' if health_data.get('features', {}).get('whatsapp_integration') else 'disabled'}")
            print(f"   Admin Alerts: {'enabled' if health_data.get('features', {}).get('admin_alerts') else 'disabled'}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_alert_system():
    """Test alert system with proper timeout and health checks"""
    print("🧪 Testing Alert System with Enhanced Features")
    print("=" * 55)
    
    # Check server health first
    if not check_server_health():
        print("❌ Cannot proceed - server is not healthy")
        return False

    # Test health endpoint
    try:
        print("\n1️⃣ Testing health endpoint...")
        health_url = "http://localhost:5000/health/extended"
        
        response = send_alert_with_retry(health_url, method="GET", timeout=60)
        if response and response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Status: {health_data.get('status', 'unknown')}")
            
            # Check specific components
            system_status = health_data.get('system_status', {})
            print(f"   Database: {system_status.get('database', 'unknown')}")
            print(f"   WhatsApp: {'connected' if system_status.get('whatsapp_service') else 'disconnected'}")
            print(f"   Admin Alerts: {'available' if system_status.get('admin_alerts') else 'unavailable'}")
            print(f"   ML Models: {system_status.get('ml_models', {}).get('loaded', 0)} loaded")
        else:
            print(f"❌ Health test failed: {response.status_code if response else 'no response'}")
            return False

    except Exception as e:
        print(f"❌ Health test error: {e}")
        return False

    # Test alert system endpoints
    print("\n2️⃣ Testing alert system endpoints...")
    try:
        alert_url = "http://localhost:5000/alerts/test"
        response = send_alert_with_retry(alert_url, method="GET", timeout=60)
        
        if response and response.status_code == 200:
            alert_data = response.json()
            print(f"✅ Alert system test passed")
            print(f"   Service available: {alert_data.get('service_available', False)}")
            print(f"   Features: {', '.join([k for k, v in alert_data.get('features', {}).items() if v])}")
        else:
            print(f"❌ Alert test failed: {response.status_code if response else 'no response'}")
            return False
            
    except Exception as e:
        print(f"❌ Alert test error: {e}")
        return False

    return True

def send_broadcast_alert(message_type: str = "emergency"):
    """Send broadcast alert with enhanced features"""
    print(f"\n📢 Sending {message_type.upper()} Broadcast Alert...")
    
    # Different message templates for different scenarios
    messages = {
        "emergency": {
            "text": "🚨 HEALTH EMERGENCY ALERT\n\n⚠️ Dengue Outbreak Reported in Your Area\n\n📋 SYMPTOMS TO WATCH FOR:\n• High fever (101°F+)\n• Severe headache behind eyes\n• Joint and muscle pain\n• Skin rash (3-4 days after fever)\n• Nausea and vomiting\n• Mild bleeding (nose/gums)\n\n🛡️ IMMEDIATE PREVENTIVE MEASURES:\n• Use EPA-approved mosquito repellent\n• Wear long-sleeved clothing\n• Eliminate standing water around home\n• Install window screens\n• Avoid outdoor activities at dawn/dusk\n\n🏥 SEEK MEDICAL CARE IF:\n• Fever persists >3 days\n• Severe abdominal pain\n• Persistent vomiting\n• Bleeding symptoms\n• Difficulty breathing\n\n📞 EMERGENCY CONTACTS:\n• Government Helpline: 1075\n• Local Health Dept: [Your Local Number]\n• Hospital Emergency: 108\n\n💡 This is an official health advisory. Please share with family and neighbors!",
            "type": "emergency",
            "priority": "high"
        },
        "health_tip": {
            "text": "💡 DAILY HEALTH TIP - Immune System Boost\n\n✅ NATURAL IMMUNITY BOOSTERS:\n• Citrus fruits (Vitamin C): Oranges, lemons, guava\n• Yogurt (Probiotics): Supports gut health\n• Almonds (Vitamin E): 8-10 daily\n• Green tea (Antioxidants): 2-3 cups daily\n• Garlic (Allicin): Raw or lightly cooked\n• Ginger (Anti-inflammatory): Tea or cooking\n\n🛡️ DAILY PREVENTION HABITS:\n• Wash hands for 20 seconds frequently\n• Get 7-8 hours quality sleep\n• Exercise 30 minutes daily\n• Manage stress through meditation\n• Stay hydrated (8-10 glasses water)\n• Maintain healthy weight\n\n⚠️ WHEN TO BE CONCERNED:\n• Frequent infections (>4/year)\n• Persistent fatigue\n• Slow wound healing\n• Unexplained weight loss\n\n📅 REMINDER: Schedule annual health check-up\n\n🏥 HEALTHY LIVING: Small daily habits = Big health benefits!",
            "type": "health_advisory",
            "priority": "normal"
        },
        "outbreak": {
            "text": "🦠 DISEASE OUTBREAK ALERT 🟡\n\n⚠️ INFLUENZA (FLU) OUTBREAK - REGIONAL ALERT\n\n📊 CURRENT SITUATION:\n• 150+ cases reported in last 7 days\n• Affecting all age groups\n• Peak season: December-February\n\n🌡️ SYMPTOMS TO WATCH:\n• Sudden fever (100°F+)\n• Dry cough and sore throat\n• Body aches and headaches\n• Extreme fatigue and weakness\n• Chills and sweats\n\n🛡️ PROTECTION MEASURES:\n• Get flu vaccine (if not done)\n• Avoid crowded places\n• Cover coughs/sneezes\n• Wash hands frequently\n• Don't touch face with unwashed hands\n• Stay home if sick\n\n💊 HOME CARE:\n• Rest and stay hydrated\n• Use fever reducers (paracetamol)\n• Warm salt water gargles\n• Humidifier for congestion\n• Light, nutritious meals\n\n🏥 SEEK CARE IF:\n• Difficulty breathing\n• Persistent high fever >3 days\n• Severe muscle pain\n• Confusion or dizziness\n• Underlying conditions worsen\n\n📞 Vaccination Info: Contact local health center\n\n💡 Together we can prevent spread - Stay safe!",
            "type": "outbreak",
            "priority": "high"
        }
    }
    
    if message_type not in messages:
        print(f"❌ Unknown message type: {message_type}")
        return False
    
    message_data = messages[message_type]
    encoded_message = urllib.parse.quote(message_data["text"])
    
    # Build URL with all parameters
    url = (
        f"http://localhost:5000/alerts/broadcast"
        f"?api_key=admin_secret_key_change_this"
        f"&message={encoded_message}"
        f"&alert_type={message_data['type']}"
        f"&priority={message_data['priority']}"
    )
    
    try:
        print(f"📤 Sending {message_data['priority']} priority {message_data['type']} alert...")
        print(f"Message length: {len(message_data['text'])} characters")
        
        response = send_alert_with_retry(url, method="POST", timeout=120)
        
        if response and response.status_code == 200:
            response_data = response.json()
            print(f"✅ Broadcast alert sent successfully!")
            print(f"   Users targeted: {response_data.get('total_users', 'unknown')}")
            print(f"   Successful deliveries: {response_data.get('results', {}).get('success', 0)}")
            print(f"   Failed deliveries: {response_data.get('results', {}).get('failed', 0)}")
            
            if response_data.get('results', {}).get('failed', 0) > 0:
                failed_numbers = response_data.get('results', {}).get('failed_numbers', [])
                print(f"   Failed numbers: {len(failed_numbers)} numbers")
                
            return True
        else:
            print(f"❌ Broadcast failed: {response.status_code if response else 'no response'}")
            if response:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending broadcast alert: {e}")
        return False

def send_outbreak_alert():
    """Send disease outbreak alert"""
    print("\n🦠 Sending Disease Outbreak Alert...")
    
    outbreak_data = {
        "disease": "Influenza",
        "region": "Mumbai Metropolitan Region",
        "symptoms": ["Fever 100°F+", "Dry cough", "Body aches", "Fatigue", "Headache"],
        "precautions": ["Get vaccinated", "Wash hands frequently", "Avoid crowds", "Cover coughs", "Stay home if sick"],
        "severity": "moderate"
    }
    
    # Build URL for outbreak alert
    base_url = "http://localhost:5000/alerts/outbreak"
    params = {
        "api_key": "admin_secret_key_change_this",
        "disease": outbreak_data["disease"],
        "region": outbreak_data["region"],
        "symptoms": json.dumps(outbreak_data["symptoms"]),
        "precautions": json.dumps(outbreak_data["precautions"]),
        "severity": outbreak_data["severity"]
    }
    
    # Convert lists to proper format
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        print(f"📤 Sending {outbreak_data['severity']} severity outbreak alert...")
        print(f"Disease: {outbreak_data['disease']}")
        print(f"Region: {outbreak_data['region']}")
        
        response = send_alert_with_retry(url, method="POST", timeout=120)
        
        if response and response.status_code == 200:
            result = response.json()
            print(f"✅ Outbreak alert sent successfully!")
            print(f"   Disease: {result.get('disease')}")
            print(f"   Region: {result.get('region')}")
            print(f"   Severity: {result.get('severity')}")
            print(f"   Users notified: {result.get('total_users', 'unknown')}")
            return True
        else:
            print(f"❌ Outbreak alert failed: {response.status_code if response else 'no response'}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending outbreak alert: {e}")
        return False

def send_emergency_alert():
    """Send emergency alert"""
    print("\n🚨 Sending Emergency Alert...")
    
    emergency_data = {
        "emergency_type": "Severe Weather Warning",
        "region": "Pune District",
        "affected_areas": ["Pune City", "Pimpri-Chinchwad", "Hinjewadi", "Magarpatta"],
        "safety_instructions": [
            "Stay indoors and avoid travel",
            "Keep emergency kit ready (flashlight, water, medications)",
            "Monitor weather updates on TV/radio",
            "Charge mobile devices",
            "Secure outdoor objects",
            "Avoid flooded areas"
        ],
        "contact_info": {
            "Emergency Services": "108",
            "District Control Room": "020-25506800",
            "Police": "100",
            "Fire Brigade": "101"
        }
    }
    
    # Build URL for emergency alert
    base_url = "http://localhost:5000/alerts/emergency"
    params = {
        "api_key": "admin_secret_key_change_this",
        "emergency_type": emergency_data["emergency_type"],
        "region": emergency_data["region"],
        "affected_areas": json.dumps(emergency_data["affected_areas"]),
        "safety_instructions": json.dumps(emergency_data["safety_instructions"]),
        "contact_info": json.dumps(emergency_data["contact_info"])
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        print(f"📤 Sending {emergency_data['emergency_type']} alert...")
        print(f"Region: {emergency_data['region']}")
        print(f"Affected areas: {', '.join(emergency_data['affected_areas'])}")
        
        response = send_alert_with_retry(url, method="POST", timeout=120)
        
        if response and response.status_code == 200:
            result = response.json()
            print(f"✅ Emergency alert sent successfully!")
            print(f"   Emergency Type: {result.get('emergency_type')}")
            print(f"   Region: {result.get('region')}")
            print(f"   Users notified: {result.get('total_users', 'unknown')}")
            return True
        else:
            print(f"❌ Emergency alert failed: {response.status_code if response else 'no response'}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending emergency alert: {e}")
        return False

def display_alert_menu():
    """Display interactive alert menu"""
    print("\n" + "="*60)
    print("🏥 HEALTHCARE ADMIN ALERT SYSTEM - CONTROL PANEL")
    print("="*60)
    print("\n📋 Available Alert Types:")
    print("1. 🚨 Emergency Broadcast (High Priority)")
    print("2. 🦠 Disease Outbreak Alert") 
    print("3. ⚡ Health Advisory/Tips (Normal Priority)")
    print("4. 🧪 Test Alert System")
    print("5. 📊 Check System Health")
    print("6. ❌ Exit")
    print("\n" + "-"*60)

def main():
    """Main function with interactive menu"""
    print("🚀 ADMIN ALERT SYSTEM - COMPLETE FIXED VERSION")
    print("=" * 60)
    print("This tool sends administrative alerts to all users via WhatsApp")
    print("Ensure the server is running on http://localhost:5000")
    print("=" * 60)
    
    while True:
        display_alert_menu()
        
        try:
            choice = input("\n👉 Enter your choice (1-6): ").strip()
            
            if choice == "1":
                send_broadcast_alert("emergency")
                
            elif choice == "2":
                send_outbreak_alert()
                
            elif choice == "3":
                send_broadcast_alert("health_tip")
                
            elif choice == "4":
                if test_alert_system():
                    print("\n✅ All system tests passed!")
                else:
                    print("\n❌ Some system tests failed!")
                    
            elif choice == "5":
                check_server_health()
                
            elif choice == "6":
                print("\n👋 Thank you for using Healthcare Admin Alert System!")
                print("Stay safe and keep helping others! 🏥")
                break
                
            else:
                print("\n❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or check server logs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Stay healthy! 🏥")
