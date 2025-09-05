import requests
import json
from datetime import datetime, timedelta

# Calculate date range (last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
date_from = start_date.strftime("%Y-%m-%d")
date_to = end_date.strftime("%Y-%m-%d")

print(f"Using date range: {date_from} to {date_to}")

# Test the correct endpoint with required parameters
endpoint = "https://ocds-api.etenders.gov.za/api/OCDSReleases"

def test_endpoint(endpoint):
    print(f"\n🔍 Testing: {endpoint}")
    try:
        response = requests.get(
            endpoint,
            params={
                "searchText": "construction",
                "dateFrom": date_from,
                "dateTo": date_to,
                "pageSize": 5
            },
            timeout=15,
            headers={"Accept": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Success! Response format:")
                print(f"Found {len(data.get('releases', []))} releases")
                
                if data.get('releases'):
                    print("\nSample release:")
                    sample = data['releases'][0]
                    print(f"OCID: {sample.get('ocid')}")
                    print(f"Title: {sample.get('tender', {}).get('title')}")
                    print(f"Buyer: {sample.get('buyer', {}).get('name')}")
                
                return True, data
            except json.JSONDecodeError:
                print("❌ Response is not JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return False, None

# Test the endpoint
success, data = test_endpoint(endpoint)

if success:
    print(f"\n🎉 API is working! Now you can integrate it into your FastAPI application.")
else:
    print(f"\n❌ Still not working. Let's check what's wrong...")
    
    # Try to see the Swagger docs for required parameters
    print(f"\n🔍 Checking Swagger documentation...")
    try:
        swagger_url = "https://ocds-api.etenders.gov.za/swagger/v1/swagger.json"
        response = requests.get(swagger_url, timeout=10)
        if response.status_code == 200:
            swagger_data = response.json()
            ocds_path = swagger_data["paths"]["/api/OCDSReleases"]
            get_params = ocds_path["get"]["parameters"]
            print("Required parameters for /api/OCDSReleases:")
            for param in get_params:
                print(f"  - {param['name']} ({param.get('required', False)}): {param.get('description', 'No description')}")
    except Exception as e:
        print(f"❌ Could not get Swagger details: {e}")