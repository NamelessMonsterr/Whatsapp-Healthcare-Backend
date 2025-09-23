"""
Test Data.gov.in API with filters to get actual data
"""
import requests
import json

API_KEY = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"

def test_with_state_filters():
    """Test API with state filters to get actual data"""
    
    # Hospital directory resource
    resource_id = "7d208ae4-5d5d-4ffb-a8a2-946981635255"
    url = f"https://api.data.gov.in/resource/{resource_id}"
    
    # Common Indian states to test
    test_states = ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh"]
    
    headers = {"Accept": "application/json"}
    
    for state in test_states:
        print(f"\n🔍 Testing hospitals in {state}...")
        
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 3,
            "filters": f"state=={state}"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                record_count = data.get('count', 0)
                print(f"  ✅ Found {record_count} hospitals in {state}")
                
                if record_count > 0 and 'records' in data:
                    print("  Sample hospitals:")
                    for i, record in enumerate(data['records'][:2]):
                        name = record.get('hospital_name', 'N/A')
                        district = record.get('district', 'N/A')
                        print(f"    - {name} ({district})")
                elif record_count > 0:
                    print("  Data available but no records in response")
                else:
                    print("  No hospitals found in this state")
            else:
                print(f"  ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Failed: {e}")

def test_common_filters():
    """Test common filters that usually work"""
    
    print("\n" + "="*60)
    print("TESTING COMMON FILTERS")
    print("="*60)
    
    resource_id = "7d208ae4-5d5d-4ffb-a8a2-946981635255"
    url = f"https://api.data.gov.in/resource/{resource_id}"
    
    # Test filters
    test_filters = [
        {"name": "Government Hospitals", "filter": "type==Government"},
        {"name": "Delhi Hospitals", "filter": "state==Delhi"},
        {"name": "Maharashtra Hospitals", "filter": "state==Maharashtra"},
        {"name": "Karnataka Hospitals", "filter": "state==Karnataka"}
    ]
    
    headers = {"Accept": "application/json"}
    
    for test_filter in test_filters:
        print(f"\n🔍 Testing: {test_filter['name']}")
        
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 2,
            "filters": test_filter["filter"]
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                record_count = data.get('count', 0)
                print(f"  ✅ Records found: {record_count}")
                
                if record_count > 0:
                    print("  ✅ Data available!")
                    break  # Found working filter
            else:
                print(f"  ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n🎉 Filter testing completed!")

def test_covid_data():
    """Test COVID data specifically"""
    
    print("\n" + "="*60)
    print("TESTING COVID DATA")
    print("="*60)
    
    # COVID state data
    resource_id = "4cbfff34-7da0-4337-93c7-9e40ff039c19"
    url = f"https://api.data.gov.in/resource/{resource_id}"
    
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 5
    }
    
    headers = {"Accept": "application/json"}
    
    try:
        print("Fetching COVID data...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            record_count = data.get('count', 0)
            print(f"✅ COVID data accessible! Records: {record_count}")

            if record_count > 0 and 'records' in data:
                print("Sample COVID data:")
                for i, record in enumerate(data['records'][:2]):
                    state = record.get('state_name', 'N/A')
                    confirmed = record.get('confirmed', 'N/A')
                    print(f"  - {state}: {confirmed} confirmed cases")
        else:
            print(f"❌ COVID data error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ COVID data test failed: {e}")

if __name__ == "__main__":
    test_with_state_filters()
    test_common_filters()
    test_covid_data()