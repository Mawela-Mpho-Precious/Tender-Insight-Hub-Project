# app/models/mongodb/user_activity.py
from datetime import datetime
from typing import Dict, Any

class UserActivity:
    """Model for storing user activity logs in MongoDB"""
    
    @staticmethod
    def create_activity(user_id: str, activity_type: str, details: Dict) -> Dict:
        """Create a user activity entry"""
        return {
            "user_id": user_id,
            "activity_type": activity_type,  # search, summarize, match, save, etc.
            "details": details,
            
            # Context
            "tender_id": details.get("tender_id"),
            "search_terms": details.get("search_terms"),
            "action_result": details.get("result"),
            
            # Timestamps
            "created_at": datetime.utcnow(),
            "ip_address": details.get("ip_address", ""),
            "user_agent": details.get("user_agent", "")
        }
    
    @staticmethod
    def get_collection_name():
        return "user_activities"