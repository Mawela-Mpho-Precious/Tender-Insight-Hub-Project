# app/services/mongodb_service.py
from app.Mongodatabase.mongodb import mongodb
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class MongoDBService:
    """Simple MongoDB service that actually works"""
    
    async def store_ai_analysis(self, tender_id: str, summary_data: Dict, match_data: Dict = None) -> bool:
        """Store AI analysis results in MongoDB"""
        try:
            print(f"💾 Storing AI analysis for tender: {tender_id}")
            
            analysis_doc = {
                "tender_id": tender_id,
                "analysis_type": "document_summary",
                
                # Summary data
                "summary": {
                    "overall_summary": summary_data.get("summary", ""),
                    "highlights": summary_data.get("highlights", []),
                    "documents_processed": summary_data.get("documents_processed", 0),
                    "tender_title": summary_data.get("tender_title", ""),
                },
                
                # Match data if available
                "match_results": match_data or {},
                
                # Metadata
                "processing_time_ms": 0,
                "ai_model_used": "transformers",
                "status": "completed",
                
                # Timestamps
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            collection = mongodb.get_collection("ai_analysis_results")
            result = await collection.insert_one(analysis_doc)
            
            print(f"✅ AI analysis stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store AI analysis: {e}")
            return False
    
    async def store_match_result(self, tender_id: str, company_profile_id: str, match_data: Dict) -> bool:
        """Store match results in MongoDB"""
        try:
            print(f"💾 Storing match result for tender: {tender_id}")
            
            match_doc = {
                "tender_id": tender_id,
                "company_profile_id": company_profile_id,
                
                # Match scores
                "suitability_score": match_data.get("suitability_score", 0),
                "matched_criteria": match_data.get("matched_criteria", 0),
                "total_criteria": match_data.get("total_criteria", 0),
                
                # Analysis details
                "checklist": match_data.get("checklist", []),
                "recommendation": match_data.get("recommendation", ""),
                "tender_requirements": match_data.get("tender_requirements", {}),
                
                # Metadata
                "match_algorithm_version": "1.0",
                "calculation_time_ms": 0,
                
                # Timestamps
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            collection = mongodb.get_collection("match_results")
            result = await collection.insert_one(match_doc)
            
            print(f"✅ Match result stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store match result: {e}")
            return False
    
    async def log_user_activity(self, user_id: str, activity_type: str, details: Dict) -> bool:
        """Log user activity in MongoDB"""
        try:
            activity_doc = {
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details,
                "created_at": datetime.utcnow()
            }
            
            collection = mongodb.get_collection("user_activities")
            await collection.insert_one(activity_doc)
            
            print(f"✅ User activity logged: {activity_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log user activity: {e}")
            return False
    
    async def get_tender_analysis_history(self, tender_id: str) -> List[Dict]:
        """Get analysis history for a tender"""
        try:
            collection = mongodb.get_collection("ai_analysis_results")
            
            cursor = collection.find({"tender_id": tender_id}).sort("created_at", -1)
            results = await cursor.to_list(length=10)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                result["_id"] = str(result["_id"])
            
            return results
            
        except Exception as e:
            print(f"❌ Error getting analysis history: {e}")
            return []
    
    async def get_company_match_history(self, company_profile_id: str) -> List[Dict]:
        """Get match history for a company"""
        try:
            collection = mongodb.get_collection("match_results")
            
            cursor = collection.find({"company_profile_id": company_profile_id}).sort("created_at", -1)
            results = await cursor.to_list(length=20)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                result["_id"] = str(result["_id"])
            
            return results
            
        except Exception as e:
            print(f"❌ Error getting match history: {e}")
            return []
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary from MongoDB"""
        try:
            # Total analyses count
            analysis_collection = mongodb.get_collection("ai_analysis_results")
            total_analyses = await analysis_collection.count_documents({})
            
            # Total matches count
            match_collection = mongodb.get_collection("match_results")
            total_matches = await match_collection.count_documents({})
            
            # Recent activities count (last 7 days)
            week_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = week_ago.replace(day=week_ago.day-7)
            
            activity_collection = mongodb.get_collection("user_activities")
            recent_activities = await activity_collection.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            return {
                "total_analyses": total_analyses,
                "total_matches": total_matches,
                "recent_activities": recent_activities,
                "most_analyzed_tenders": []  # You can implement this later
            }
            
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return {
                "total_analyses": 0,
                "total_matches": 0,
                "recent_activities": 0,
                "most_analyzed_tenders": []
            }

# Global instance
mongodb_service = MongoDBService()