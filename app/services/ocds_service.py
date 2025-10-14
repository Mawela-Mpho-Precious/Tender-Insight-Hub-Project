import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import random

load_dotenv()

class OCDSService:
    def __init__(self):
        self.base_url = "https://ocds-api.etenders.gov.za"
        self.api_url = f"{self.base_url}/api/OCDSReleases"
        self.timeout = 25  # Slightly increased but reasonable
        self.max_retries = 2

    def search_tenders(self, keywords: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search tenders from the real OCDS eTenders API with optimized requests
        """
        for attempt in range(self.max_retries):
            try:
                print(f"🔍 Attempt {attempt + 1}: Fetching tenders for '{keywords}'")
                
                # Use smaller date range and page size
                end_date = datetime.now()
                start_date = end_date - timedelta(days=60)  # Increased to 60 days for more results
                date_from = start_date.strftime("%Y-%m-%d")
                date_to = end_date.strftime("%Y-%m-%d")
                
                # Optimized parameters
                params = {
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "pageSize": 100,  # Increased to get more data
                    "page": 1,
                }
                
                print(f"📅 Date range: {date_from} to {date_to}")
                
                response = requests.get(
                    self.api_url, 
                    params=params,
                    timeout=self.timeout,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "TenderInsightHub/1.0"
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                all_releases = data.get('releases', [])
                
                print(f"✅ Found {len(all_releases)} total tenders from API")
                
                if not all_releases:
                    print("⚠️ No tenders found in response")
                    return []
                
                # If no keywords, return all tenders
                if not keywords.strip():
                    return all_releases
                
                # Use improved filtering
                filtered_releases = self._improved_filter_tenders(all_releases, keywords)
                print(f"🔍 After keyword filtering: {len(filtered_releases)} tenders match '{keywords}'")
                
                # If no matches, return some recent tenders anyway
                if not filtered_releases and len(all_releases) > 0:
                    print("⚠️ No keyword matches found, returning recent tenders")
                    return all_releases[:10]  # Return first 10 recent tenders
                
                return filtered_releases
                
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("❌ All retry attempts timed out")
                    return []  # Return empty instead of raising
                    
            except requests.exceptions.RequestException as e:
                print(f"🌐 Request error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return []  # Return empty instead of raising
                    
            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                return []  # Return empty instead of raising
        
        return []  # Should never reach here

    def _improved_filter_tenders(self, releases: List[Dict], keywords: str) -> List[Dict]:
        """Improved filtering with multiple strategies"""
        if not releases:
            return []
            
        filtered_releases = []
        keyword_lower = keywords.lower().strip()
        search_words = keyword_lower.split()
        
        print(f"🔍 Filtering {len(releases)} tenders with keywords: {search_words}")
        
        for release in releases:
            tender = release.get('tender', {})
            title = tender.get('title', '').lower()
            description = tender.get('description', '').lower()
            
            # Strategy 1: Exact word matching
            exact_match = any(word in title or word in description for word in search_words)
            
            # Strategy 2: Partial word matching (for related terms)
            related_terms = self._get_related_terms(keyword_lower)
            related_match = any(term in title or term in description for term in related_terms)
            
            # Strategy 3: Check if this looks like a relevant tender based on common patterns
            pattern_match = self._pattern_match(tender, keyword_lower)
            
            if exact_match or related_match or pattern_match:
                filtered_releases.append(release)
        
        print(f"✅ Found {len(filtered_releases)} matching tenders")
        return filtered_releases

    def _get_related_terms(self, keyword: str) -> List[str]:
        """Get related terms for better matching"""
        related_terms_map = {
            'construction': ['build', 'building', 'construct', 'contractor', 'civil', 'engineering', 
                            'renovation', 'maintenance', 'infrastructure', 'development'],
            'it': ['technology', 'software', 'hardware', 'computer', 'digital', 'system', 'network'],
            'security': ['guard', 'protection', 'safety', 'surveillance', 'access control'],
            'cleaning': ['clean', 'sanitation', 'hygiene', 'maintenance', 'janitorial'],
            'transport': ['logistics', 'shipping', 'delivery', 'fleet', 'vehicle'],
        }
        
        return related_terms_map.get(keyword, [])

    def _pattern_match(self, tender: Dict, keyword: str) -> bool:
        """Check if tender matches patterns for the keyword"""
        title = tender.get('title', '').lower()
        description = tender.get('description', '').lower()
        
        if keyword == 'construction':
            # Look for construction-related patterns
            patterns = [
                'tender' in title and len(title.split()) < 10,  # Simple tender titles
                'bid' in title,
                'rfp' in title.lower(),
                'request for proposal' in title.lower(),
                'supply' in title and ('material' in title or 'equipment' in title),
            ]
            return any(patterns)
        
        return False

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