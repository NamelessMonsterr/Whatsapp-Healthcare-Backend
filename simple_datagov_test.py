"""
Simple Data.gov.in Test
"""
import requests

API_KEY = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"

def simple_test():
    """Simple test of Data.gov.in API with filters"""
    
    # Hospital directory
    url = "https://api.data.gov.in/resource/7d208ae4-5d5d-4ffb-a8a2-946981635255"
    
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 3,
        "filters": "state==Delhi"  # Try Delhi first
    }
    
    try:
        print("Testing Data.gov.in API with Delhi filter...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Working!")
            print(f"Records available: {data.get('count', 'Unknown')}")
            
            if 'records' in data and data['records']:
                print("\nSample Hospital:")
                hospital = data['records'][0]
                print(f"Name: {hospital.get('hospital_name', 'N/A')}")
                print(f"Location: {hospital.get('state', 'N/A')}, {hospital.get('district', 'N/A')}")
                print(f"Type: {hospital.get('type', 'N/A')}")
            else:
                print("No records found - trying different state...")
                
                # Try Maharashtra
                params["filters"] = "state==Maharashtra"
                response2 = requests.get(url, params=params, timeout=30)
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"Maharashtra records: {data2.get('count', 0)}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    simple_test()