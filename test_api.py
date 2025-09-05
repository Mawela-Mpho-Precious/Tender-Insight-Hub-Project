import requests
import json

# Test different possible endpoints
endpoints_to_test = [
    "https://ocds-api.etenders.gov.za/api/Release",
    "https://ocds-api.etenders.gov.za/api/OCDSReleases",  # This might be the correct one!
    "https://ocds-api.etenders.gov.za/api/releases",
    "https://ocds-api.etenders.gov.za/OCDSReleases",
    "https://ocds-api.etenders.gov.za/releases",
]

def test_endpoint(endpoint):
    print(f"\n🔍 Testing: {endpoint}")
    try:
        response = requests.get(
            endpoint,
            params={"searchText": "construction", "pageSize": 5},
            timeout=10,
            headers={"Accept": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Success! Response format:")
                print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2))
                return True, data
            except json.JSONDecodeError:
                print("❌ Response is not JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"❌ Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return False, None

# Test all endpoints
for endpoint in endpoints_to_test:
    success, data = test_endpoint(endpoint)
    if success:
        print(f"🎉 Found working endpoint: {endpoint}")
        break
else:
    print("\n❌ No endpoints worked. Let's check the Swagger UI...")
    
    # Try to access Swagger to see the correct endpoints
    swagger_url = "https://ocds-api.etenders.gov.za/swagger/v1/swagger.json"
    print(f"\n🔍 Checking Swagger documentation: {swagger_url}")
    
    try:
        response = requests.get(swagger_url, timeout=10)
        if response.status_code == 200:
            swagger_data = response.json()
            print("✅ Swagger found! Available paths:")
            for path in swagger_data.get("paths", {}).keys():
                print(f"  - {path}")
        else:
            print("❌ Could not access Swagger")
    except Exception as e:
        print(f"❌ Swagger check failed: {e}")