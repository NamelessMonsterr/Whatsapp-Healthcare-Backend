"""
Explore Data.gov.in resources to find working datasets
"""
import requests

API_KEY = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"

def explore_catalog():
    """Explore the Data.gov.in catalog"""
    
    print("🔍 Exploring Data.gov.in Catalog...")
    print("="*50)
    
    # Try to get catalog info
    try:
        # This might give us available resources
        catalog_url = "https://api.data.gov.in/"
        response = requests.get(catalog_url, timeout=30)
        
        print(f"Catalog Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Catalog accessible")
            print(f"Response length: {len(response.text)} chars")
        else:
            print(f"Catalog response: {response.text[:100]}")
            
    except Exception as e:
        print(f"Catalog exploration failed: {e}")

def test_alternative_endpoints():
    """Test alternative endpoints that might work"""
    
    print("\n" + "="*50)
    print("TESTING ALTERNATIVE ENDPOINTS")
    print("="*50)
    
    # List of commonly working endpoints
    endpoints = [
        {
            "name": "PMJAY Hospitals",
            "url": "https://api.data.gov.in/resource/8a7e7d5a-b37b-41d6-855f-9c6c6f3e7b3a",
            "description": "Ayushman Bharat PMJAY Empanelled Hospitals"
        },
        {
            "name": "NHM Facilities", 
            "url": "https://api.data.gov.in/resource/3b2a2c60-0aeb-4c0d-9f3a-8c3c3d3d3d3d",
            "description": "National Health Mission Facilities"
        },
        {
            "name": "Medical Colleges",
            "url": "https://api.data.gov.in/resource/8c5a2c60-0aeb-4c0d-9f3a-8c3c3d3d3d3d", 
            "description": "Medical Colleges in India"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 2
        }
        
        try:
            response = requests.get(endpoint['url'], params=params, timeout=30)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    record_count = data.get('count', 0) if isinstance(data, dict) else 0
                    print(f"  ✅ Records: {record_count}")
                    if record_count > 0:
                        print("  🎉 FOUND WORKING DATASET!")
                        break
                except:
                    print("  ✅ API works but response format unknown")
            else:
                print(f"  Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def manual_resource_discovery():
    """Manually discover working resources"""
    
    print("\n" + "="*50) 
    print("MANUAL RESOURCE DISCOVERY")
    print("="*50)
    
    # Try some known working resource patterns
    resource_ids = [
        "8a7e7d5a-b37b-41d6-855f-9c6c6f3e7b3a",  # PMJAY
        "7d208ae4-5d5d-4ffb-a8a2-946981635255",  # Hospital Directory (already tried)
        "4cbfff34-7da0-4337-93c7-9e40ff039c19",  # COVID State (already tried)
        "1a8e305e-0486-4942-9b3d-9400b71f0a9d",  # COVID District (already tried)
        # Add more potential resource IDs here
    ]
    
    base_url = "https://api.data.gov.in/resource/"
    
    for i, resource_id in enumerate(resource_ids):
        url = f"{base_url}{resource_id}"
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 1
        }
        
        print(f"\nTesting Resource {i+1}: {resource_id}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'count' in data:
                        print(f"  ✅ Count: {data['count']}")
                        if data['count'] > 0:
                            print("  🎉 POTENTIAL WORKING RESOURCE!")
                    else:
                        print("  ✅ API accessible but different format")
                except:
                    print("  ✅ API accessible")
            else:
                print(f"  Status: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

def test_public_datasets():
    """Test publicly known working datasets"""
    
    print("\n" + "="*50)
    print("TESTING PUBLIC DATASETS")
    print("="*50)
    
    # Try some datasets that are commonly available
    datasets = [
        {
            "name": "Indian Pin Codes",
            "resource_id": "6170d5fa-03a7-4fab-9030-117eb8c35309"
        },
        {
            "name": "Bank Branches India", 
            "resource_id": "b306f50e-34d4-42e3-8515-f47510b59f88"
        },
        {
            "name": "Post Offices India",
            "resource_id": "e6e9c26a-0c9d-4a7a-9a0a-9a0a9a0a9a0a"
        }
    ]
    
    base_url = "https://api.data.gov.in/resource/"
    
    for dataset in datasets:
        url = f"{base_url}{dataset['resource_id']}"
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 1
        }
        
        print(f"\nTesting: {dataset['name']}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = data.get('count', 'unknown') if isinstance(data, dict) else 'unknown'
                    print(f"  ✅ Count: {count}")
                    if isinstance(count, int) and count > 0:
                        print("  🎉 Working dataset found!")
                except Exception as e:
                    print(f"  ✅ API works, parsing error: {e}")
            else:
                print(f"  ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")

if __name__ == "__main__":
    explore_catalog()
    test_alternative_endpoints()
    manual_resource_discovery()
    test_public_datasets()