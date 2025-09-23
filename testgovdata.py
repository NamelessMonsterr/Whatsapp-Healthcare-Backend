# Test script to verify Data.gov.in API
import requests
import os

API_KEY = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"
BASE_URL = "https://api.data.gov.in/resource/"

def test_datagov_api():
    """Test Data.gov.in API access"""
    
    # Example: Get hospital data (you'll need actual resource IDs)
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 5
    }
    
    try:
        # Test basic connectivity
        response = requests.get("https://api.data.gov.in/", 
                              headers=headers, 
                              params=params, 
                              timeout=30)
        
        print(f"API Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Data.gov.in API accessible!")
        else:
            print("❌ API access issue")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_datagov_api()