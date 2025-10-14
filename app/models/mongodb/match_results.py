# app/models/mongodb/match_results.py
from datetime import datetime
from typing import Dict, List, Any

class MatchResult:
    """Model for storing tender-company match results in MongoDB"""
    
    @staticmethod
    def create_match(tender_id: str, company_profile_id: str, match_data: Dict) -> Dict:
        """Create a match result entry"""
        return {
            "tender_id": tender_id,
            "company_profile_id": company_profile_id,
            
            # Match Scores
            "suitability_score": match_data.get("suitability_score", 0),
            "matched_criteria": match_data.get("matched_criteria", 0),
            "total_criteria": match_data.get("total_criteria", 0),
            
            # Detailed Analysis
            "checklist": match_data.get("checklist", []),
            "recommendation": match_data.get("recommendation", ""),
            "strengths": match_data.get("strengths", []),
            "gaps": match_data.get("gaps", []),
            
            # Company Context
            "company_industry": match_data.get("company_industry", ""),
            "company_experience": match_data.get("company_experience", 0),
            
            # Timestamps
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # Metadata
            "match_algorithm_version": "1.0",
            "calculation_time_ms": 0
        }
    
    @staticmethod
    def get_collection_name():
        return "match_results"