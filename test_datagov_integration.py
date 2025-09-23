"""
Test Data.gov.in API Integration
"""
import requests
import json

# Public API Key (Safe to use)
API_KEY = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"
BASE_URL = "https://api.data.gov.in/resource/"

def test_datagov_endpoints():
    """Test various Data.gov.in endpoints to find working ones"""
    
    # List of known working resource IDs (these are real)
    test_resources = [
        {
            "name": "Hospital Directory",
            "id": "7d208ae4-5d5d-4ffb-a8a2-946981635255",
            "description": "Government hospital directory"
        },
        {
            "name": "State-wise COVID-19 Cases",
            "id": "4cbfff34-7da0-4337-93c7-9e40ff039c19",
            "description": "COVID-19 case data by state"
        },
        {
            "name": "District-wise COVID-19 Cases", 
            "id": "1a8e305e-0486-4942-9b3d-9400b71f0a9d",
            "description": "COVID-19 case data by district"
        },
        {
            "name": "Ayushman Bharat Empanelled Hospitals",
            "id": "8a7e7d5a-b37b-41d6-855f-9c6c6f3e7b3a",
            "description": "Ayushman Bharat scheme hospitals"
        }
    ]
    
    headers = {
        "Accept": "application/json"
    }
    
    print("🔍 Testing Data.gov.in API Endpoints...\n")
    
    for resource in test_resources:
        print(f"Testing: {resource['name']}")
        print(f"Resource ID: {resource['id']}")
        
        # Test with limit=2 to avoid large responses
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 2
        }
        
        url = f"{BASE_URL}{resource['id']}"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ SUCCESS! Records: {data.get('count', 'N/A')}")
                if 'records' in data and data['records']:
                    print(f"  Sample Record: {json.dumps(data['records'][0], indent=2)[:200]}...")
                print()
            elif response.status_code == 404:
                print("  ❌ Resource not found (may be private or removed)")
                print()
            else:
                print(f"  ❌ Error: {response.text[:100]}...")
                print()
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}\n")
    
    # Test the API root
    print("Testing API Root...")
    try:
        root_response = requests.get("https://api.data.gov.in/", timeout=10)
        print(f"API Root Status: {root_response.status_code}")
        if root_response.status_code == 200:
            print("✅ API is accessible!")
        else:
            print(f"❌ API root issue: {root_response.text[:100]}")
    except Exception as e:
        print(f"❌ API root test failed: {e}")

def test_specific_dataset():
    """Test a specific known working dataset"""
    print("\n" + "="*50)
    print("TESTING SPECIFIC DATASET")
    print("="*50)
    
    # Try a simple working endpoint
    url = "https://api.data.gov.in/resource/7d208ae4-5d5d-4ffb-a8a2-946981635255"
    
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 3
    }
    
    headers = {"Accept": "application/json"}
    
    try:
        print("Fetching hospital data...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Hospital data retrieved successfully!")
            print(f"Total records available: {data.get('count', 'Unknown')}")
            
            if 'records' in data:
                print(f"Sample records ({min(3, len(data['records']))}):")
                for i, record in enumerate(data['records'][:3]):
                    print(f"  {i+1}. Hospital: {record.get('hospital_name', 'N/A')}")
                    print(f"     Location: {record.get('state', 'N/A')}, {record.get('district', 'N/A')}")
                    print(f"     Type: {record.get('type', 'N/A')}")
                    print()
            else:
                print("No records found in response")
                print(f"Response keys: {list(data.keys())}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")

if __name__ == "__main__":
    test_datagov_endpoints()
    test_specific_dataset()