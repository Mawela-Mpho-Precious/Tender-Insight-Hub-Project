import requests
import PyPDF2
import io
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.timeout = 30
    
    async def download_and_extract_text(self, document_url: str) -> Optional[str]:
        """
        Download document and extract text content
        """
        try:
            print(f"📥 Downloading document from: {document_url}")
            
            response = requests.get(document_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Check if it's a PDF
            if document_url.lower().endswith('.pdf') or 'application/pdf' in response.headers.get('content-type', ''):
                return await self._extract_pdf_text(response.content)
            else:
                print(f"⚠️ Unsupported document format: {document_url}")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading document: {e}")
            return None
    
    async def _extract_pdf_text(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from PDF content
        """
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            print(f"✅ Extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return None

# Global instance
document_service = DocumentService()