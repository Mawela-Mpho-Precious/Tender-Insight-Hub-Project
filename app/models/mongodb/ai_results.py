# app/models/mongodb/ai_results.py
from datetime import datetime
from typing import Dict, List, Any, Optional

class AIAnalysisResult:
    """Model for storing AI analysis results in MongoDB"""
    
    @staticmethod
    def create_analysis(tender_id: str, summary_data: Dict, match_data: Dict = None) -> Dict:
        """Create an AI analysis result entry"""
        return {
            "tender_id": tender_id,
            "analysis_type": "document_summary",
            
            # AI Summary Data
            "summary": {
                "overall_summary": summary_data.get("overall_summary", ""),
                "highlights": summary_data.get("overall_highlights", {}),
                "documents_processed": summary_data.get("documents_processed", 0),
                "extracted_text_length": summary_data.get("extracted_text_length", 0),
                "summary_length": len(summary_data.get("overall_summary", "")),
            },
            
            # Match Results (if available)
            "match_analysis": match_data or {},
            
            # Processing Metadata
            "processing_time_ms": 0,
            "ai_model_used": "facebook/bart-large-cnn",
            "extraction_method": "pypdf2",
            
            # Timestamps
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # Status
            "status": "completed",  # pending, processing, completed, failed
            "errors": []
        }
    
    @staticmethod
    def get_collection_name():
        return "ai_analysis_results"