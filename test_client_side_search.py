# test_client_side_search.py
import requests
from datetime import datetime, timedelta

def test_client_side_search():
    # First, get all data from API
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    date_from = start_date.strftime("%Y-%m-%d")
    date_to = end_date.strftime("%Y-%m-%d")
    
    print("📦 Fetching all tenders from API...")
    response = requests.get(
        "https://ocds-api.etenders.gov.za/api/OCDSReleases",
        params={
            "dateFrom": date_from,
            "dateTo": date_to,
            "pageSize": 100
        },
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        all_releases = data.get('releases', [])
        print(f"✅ Found {len(all_releases)} total tenders")
        
        # Test client-side filtering
        search_terms = ["construction", "security", "education", "health", "IT"]
        
        for term in search_terms:
            print(f"\n🔍 Testing client-side search for: '{term}'")
            
            filtered = []
            term_lower = term.lower()
            
            for release in all_releases:
                tender = release.get('tender', {})
                title = tender.get('title', '').lower()
                description = tender.get('description', '').lower()
                
                if (term_lower in title or term_lower in description):
                    filtered.append(release)
            
            print(f"   Found {len(filtered)} matches")
            
            if filtered:
                titles = [r.get('tender', {}).get('title', 'No title') for r in filtered[:3]]
                for title in titles:
                    print(f"   - {title}")
            else:
                print("   No matches found")

if __name__ == "__main__":
    test_client_side_search()