# app/services/document_integration.py
from app.services.document_processor import document_processor
from app.services.tender_doc_services import summarize_text, highlight_key_points
from typing import Dict, List, Optional

class DocumentIntegrationService:
    """Service to integrate document processing with your existing system"""
    
    async def process_tender_documents(self, tender_id: str, documents: List[Dict]) -> Dict:
        """
        Process documents for a tender and return AI-ready text
        """
        try:
            # Process documents using the document processor
            result = await document_processor.process_tender_documents(tender_id, documents)
            
            return {
                "success": result["success"],
                "extracted_text": result["extracted_text"],
                "documents_processed": result["documents_processed"],
                "message": result["message"],
                "errors": result.get("errors", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "extracted_text": "",
                "documents_processed": 0,
                "message": f"Document processing failed: {str(e)}",
                "errors": [str(e)]
            }
    
    async def auto_summarize_tender(self, tender_id: str, db_session):
        """
        Complete pipeline: Download documents → Extract text → Generate summary
        """
        try:
            # 1. Get tender data from your SQL database
            from app.models.tender_models import Tender
            tender = db_session.query(Tender).filter(Tender.ocds_id == tender_id).first()
            
            if not tender:
                return {"success": False, "message": "Tender not found"}
            
            # 2. Check if tender has documents
            documents = tender.documents or []
            if not documents:
                return {
                    "success": False, 
                    "message": "No documents available for this tender",
                    "documents_processed": 0
                }
            
            print(f"📄 Found {len(documents)} documents for tender {tender_id}")
            
            # 3. Process documents
            doc_result = await self.process_tender_documents(tender_id, documents)
            
            if not doc_result["success"]:
                return {
                    "success": False,
                    "message": doc_result["message"],
                    "errors": doc_result["errors"]
                }
            
            # 4. Generate AI summary from extracted text
            extracted_text = doc_result["extracted_text"]
            
            print(f"🤖 Generating AI summary from {len(extracted_text)} characters of text")
            
            summary = summarize_text(extracted_text)
            highlights = highlight_key_points(extracted_text)
            
            return {
                "success": True,
                "tender_id": tender_id,
                "tender_title": tender.title,
                "overall_summary": summary,
                "overall_highlights": highlights,
                "documents_processed": doc_result["documents_processed"],
                "extracted_text_length": len(extracted_text)
            }
            
        except Exception as e:
            print(f"❌ Auto-summarization error: {e}")
            return {
                "success": False,
                "message": f"Auto-summarization failed: {str(e)}"
            }

# Global instance
document_integration = DocumentIntegrationService()