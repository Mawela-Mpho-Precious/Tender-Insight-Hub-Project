import requests
from datetime import datetime, timedelta

# Test different search terms
search_terms = ["construction", "security", "education", "health", "IT"]

end_date = datetime.now()
start_date = end_date - timedelta(days=30)
date_from = start_date.strftime("%Y-%m-%d")
date_to = end_date.strftime("%Y-%m-%d")

for term in search_terms:
    print(f"\n🔍 Testing search term: '{term}'")
    
    response = requests.get(
        "https://ocds-api.etenders.gov.za/api/OCDSReleases",
        params={
            "searchText": term,
            "dateFrom": date_from,
            "dateTo": date_to,
            "pageSize": 5
        },
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        count = len(data.get('releases', []))
        print(f"   Found {count} results")
        
        if count > 0:
            titles = [r.get('tender', {}).get('title', 'No title') for r in data['releases'][:3]]
            for title in titles:
                print(f"   - {title}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")