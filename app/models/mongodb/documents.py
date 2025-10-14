# app/models/mongodb/documents.py
from datetime import datetime
from typing import Optional, Dict, Any

class TenderDocument:
    """Model for storing tender documents in MongoDB"""
    
    @staticmethod
    def create_document(tender_id: str, document_data: dict) -> dict:
        """Create a tender document entry"""
        return {
            "tender_id": tender_id,  # Reference to OCDS tender ID
            "document_url": document_data.get("url", ""),
            "document_title": document_data.get("title", ""),
            "document_format": document_data.get("format", "PDF"),
            "file_size": document_data.get("size", 0),
            "content_type": "application/pdf",
            
            # Binary storage (for small docs)
            "file_data": None,  # Store actual bytes if needed
            
            # Extracted text
            "extracted_text": None,
            "extraction_status": "pending",  # pending, success, failed
            "extraction_date": None,
            "extraction_method": None,  # pypdf2, pdfplumber, ocr
            
            # Processing metadata
            "text_length": 0,
            "page_count": 0,
            "language": "en",
            
            # Timestamps
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # Error tracking
            "errors": []
        }
    
    @staticmethod
    def get_collection_name():
        return "tender_documents"