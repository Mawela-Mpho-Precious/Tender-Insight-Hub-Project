import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class OCDSService:
    def __init__(self):
        self.base_url = "https://ocds-api.etenders.gov.za"
        self.api_url = f"{self.base_url}/api/OCDSReleases"

    def search_tenders(self, keywords: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search tenders from the real OCDS eTenders API.
        Enhanced search that looks in multiple fields and handles government tender codes.
        """
        try:
            # Calculate date range (last 90 days as default)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            date_from = start_date.strftime("%Y-%m-%d")
            date_to = end_date.strftime("%Y-%m-%d")
            
            # Fetch ALL data
            params = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "pageSize": 200,
                "page": 1,
            }
            
            print(f"🔍 Fetching ALL tenders from: {date_from} to {date_to}")
            
            response = requests.get(
                self.api_url, 
                params=params,
                timeout=30,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "TenderInsightHub/1.0"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            all_releases = data.get('releases', [])
            
            print(f"✅ Found {len(all_releases)} total tenders")
            
            # Filter based on keywords
            if keywords.strip():
                filtered_releases = []
                keyword_lower = keywords.lower().strip()
                search_words = keyword_lower.split()
                
                for release in all_releases:
                    tender = release.get('tender', {})
                    title = tender.get('title', '').lower()
                    description = tender.get('description', '').lower()
                    items_text = ""
                    for item in tender.get('items', []):
                        items_text += item.get('description', '').lower() + " "
                        classification = item.get('classification', {})
                        items_text += classification.get('description', '').lower() + " "
                    
                    procuring_entity = tender.get('procuringEntity', {})
                    buyer_name = procuring_entity.get('name', '').lower()
                    buyer_id = procuring_entity.get('id', '').lower()
                    
                    searchable_text = f"{title} {description} {items_text} {buyer_name} {buyer_id}"
                    
                    if any(word in searchable_text for word in search_words):
                        filtered_releases.append(release)
                
                print(f"🔍 After enhanced filtering: {len(filtered_releases)} tenders match '{keywords}'")
                
                if not filtered_releases:
                    print("⚠️ No exact matches found. Showing sample tenders...")
                    return all_releases[:10]
                
                return filtered_releases
            
            return all_releases
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return []
        except Exception as e:
            print(f"❌ Error in search_tenders: {e}")
            return []

    def get_tender_details(self, ocid: str) -> Optional[Dict]:
        """
        Get detailed information for a specific tender by OCID.
        """
        try:
            endpoint = f"{self.base_url}/api/OCDSReleases/release/{ocid}"
            print(f"Fetching tender details from: {endpoint}")
            
            response = requests.get(
                endpoint,
                timeout=30,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "TenderInsightHub/1.0"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            print(f"✅ Tender details received for OCID: {ocid}")
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get tender details: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error getting tender details: {e}")
            return None

# Create global instance
ocds_service = OCDSService()
