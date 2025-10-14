# app/services/document_processor.py
import httpx
import logging
from typing import Optional, Dict, List
from io import BytesIO
import PyPDF2
from datetime import datetime
import asyncio
import re
import os

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for downloading and processing tender documents"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.timeout = 120.0
    
    async def download_document(self, url: str) -> Optional[bytes]:
        """Download document from URL"""
        try:
            print(f"📥 Downloading document from: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Check file size
                content_length = int(response.headers.get('content-length', 0))
                if content_length > self.max_file_size:
                    logger.warning(f"Document too large: {content_length} bytes")
                    return None
                
                print(f"✅ Downloaded {len(response.content)} bytes")
                return response.content
                
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> Dict:
        """Extract text from PDF bytes"""
        result = {
            "text": "",
            "page_count": 0,
            "method": "pypdf2",
            "success": False,
            "error": None
        }
        
        try:
            # Check if it's actually a PDF
            if not pdf_bytes.startswith(b'%PDF'):
                result["error"] = "File is not a PDF document"
                return result
            
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            result["page_count"] = len(pdf_reader.pages)
            
            # Extract text from all pages (prioritize early pages where eligibility is usually stated)
            text_parts = []
            for i, page in enumerate(pdf_reader.pages[:15]):  # First 15 pages
                page_text = page.extract_text()
                if page_text.strip():
                    # Clean up common PDF extraction artifacts
                    page_text = re.sub(r'\s+', ' ', page_text)  # Normalize whitespace
                    page_text = re.sub(r'(\w)-\s+(\w)', r'\1\2', page_text)  # Fix hyphenation
                    text_parts.append(page_text)
            
            result["text"] = "\n\n".join(text_parts)
            result["success"] = True if result["text"].strip() else False
            
            # If no text extracted, it might be scanned PDF
            if not result["text"].strip():
                result["error"] = "No text found - document may be scanned/image-based"
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PDF extraction failed: {e}")
        
        return result
    
    async def process_tender_documents(self, tender_id: str, documents: List[Dict]) -> Dict:
        """Process all documents for a tender and return combined text"""
        if not documents:
            return {
                "success": False,
                "message": "No documents found",
                "extracted_text": "",
                "documents_processed": 0
            }
        
        extracted_texts = []
        processed_count = 0
        errors = []
        
        # Prioritize documents likely to contain requirements
        priority_keywords = ["specification", "requirement", "eligibility", "scope", "terms", "tender", "bid"]
        sorted_docs = sorted(
            documents,
            key=lambda d: any(kw in d.get("title", "").lower() for kw in priority_keywords),
            reverse=True
        )

        # Process up to 3 documents
        for doc in sorted_docs[:3]:
            url = doc.get("url")
            if not url:
                continue
            
            try:
                # Download document
                pdf_bytes = await self.download_document(url)
                if not pdf_bytes:
                    errors.append(f"Failed to download: {doc.get('title', 'Unknown')}")
                    continue
                
                # Extract text
                extraction = self.extract_text_from_pdf(pdf_bytes)
                
                if extraction["success"] and extraction["text"].strip():
                    extracted_texts.append(extraction["text"])
                    processed_count += 1
                    
                    print(f"✅ Processed document: {doc.get('title', 'Unknown')} - {len(extraction['text'])} characters")
                else:
                    errors.append(f"No text extracted from: {doc.get('title', 'Unknown')} - {extraction.get('error', 'Unknown error')}")
            
            except Exception as e:
                logger.error(f"Error processing document {doc.get('title', 'Unknown')}: {e}")
                errors.append(f"Error processing: {doc.get('title', 'Unknown')}")
        
        # Combine all extracted text
        combined_text = "\n\n--- DOCUMENT BREAK ---\n\n".join(extracted_texts)
        
        return {
            "success": processed_count > 0,
            "message": f"Processed {processed_count}/{len(documents)} documents",
            "extracted_text": combined_text,
            "documents_processed": processed_count,
            "errors": errors
        }

# Global instance
document_processor = DocumentProcessor()