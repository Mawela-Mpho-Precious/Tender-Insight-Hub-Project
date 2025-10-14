from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tender_models import Tender
from app.services.ocds_service import ocds_service

router = APIRouter(prefix="/api/tenders", tags=["tenders"])


@router.get("/search")
async def search_tenders(
    keywords: str = Query(..., description="Keywords to search for (required)"),
    province: Optional[str] = Query(None),
    buyer: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search tenders with keywords and optional filters using OCDS eTenders API.
    Returns only real data from the API or empty results.
    """
    try:
        if not keywords.strip():
            raise HTTPException(status_code=400, detail="Keywords parameter is required")

        print(f"Searching for: '{keywords}', province: {province}, buyer: {buyer}")

        # Prepare filters
        filters = {}
        if province:
            filters["province"] = province
        if buyer:
            filters["buyer"] = buyer

        # Get results from real OCDS API (returns empty list if API fails)
        tenders = ocds_service.search_tenders(keywords, filters)

        processed_tenders = []

        # Process tender information from OCDS format
        for tender_data in tenders:
            try:
                # Extract data from OCDS format
                ocid = tender_data.get("ocid", "")
                tender_info = tender_data.get("tender", {})

                # Get title
                title = (
                    tender_data.get("title")
                    or tender_info.get("title")
                    or f"Tender {ocid}"
                    or "No Title"
                )

                # Get description
                description = (
                    tender_info.get("description")
                    or tender_data.get("description")
                    or ""
                )

                # Get procuring entity (buyer)
                procuring_entity = tender_info.get("procuringEntity", {})
                buyer_name = (
                    procuring_entity.get("name", "")
                    if isinstance(procuring_entity, dict) else ""
                )
                buyer_id = (
                    procuring_entity.get("id", "")
                    if isinstance(procuring_entity, dict) else ""
                )

                # Get value
                value_info = tender_info.get("value", {})
                amount = (
                    value_info.get("amount", 0)
                    if isinstance(value_info, dict) else 0
                )

                # Get tender period
                tender_period = tender_info.get("tenderPeriod", {})
                end_date = (
                    tender_period.get("endDate", "")
                    if isinstance(tender_period, dict) else ""
                )

                # Get location
                location = ""
                if "address" in tender_info:
                    location = tender_info.get("address", {}).get("region", "")
                elif "items" in tender_info and tender_info["items"]:
                    location = tender_info["items"][0].get("address", {}).get("region", "")
               
                documents = tender_info.get('documents', [])
                if documents:
                    print(f"📄 Found {len(documents)} documents for tender {ocid}")
                     
                    if documents:
                        print(f"📄 Sample document: {documents[0].get('title', 'No title')} - {documents[0].get('url', 'No URL')}")


                # Build processed tender
                processed_tender = {
                    "id": ocid or tender_data.get("id", ""),
                    "title": title,
                    "description": description,
                    "publisher": tender_data.get("publisher", {}),
                    "value": {"amount": amount, "currency": "ZAR"},
                    "tender": {
                        "tenderPeriod": {
                            "endDate": end_date,
                            "startDate": (
                                tender_period.get("startDate", "")
                                if isinstance(tender_period, dict) else ""
                            )
                        },
                        "procuringEntity": procuring_entity,
                    },
                    "buyer": {"name": buyer_name, "id": buyer_id},
                    "province": location,
                    "documents": documents,
                    "raw_data": tender_data,

                }
                processed_tenders.append(processed_tender)

                # Store in database (if new)
                if ocid and not db.query(Tender).filter(Tender.ocds_id == ocid).first():
                    tender = Tender(
                        ocds_id=ocid,
                        title=title[:200],
                        description=description[:500],
                        publishing_office=buyer_name[:100],
                        province=location[:100],
                        budget_range=str(amount),
                        submission_deadline=end_date,
                        estimated_value=amount,
                        buyer_name=buyer_name[:200],
                        buyer_id=buyer_id[:100],
                        documents=documents
                    )
                    db.add(tender)

            except Exception as e:
                print(f"Error processing tender data: {e}")
                continue

        db.commit()

        return {
            "count": len(processed_tenders),
            "results": processed_tenders,
            "search_term": keywords,
            "source": "OCDS eTenders API",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error searching tenders: {str(e)}")
        return {
            "count": 0,
            "results": [],
            "search_term": keywords,
            "source": "OCDS eTenders API (Error)",
            "error": "Failed to fetch tenders from API",
        }
    
@router.get("/api/debug/raw-tenders")
async def get_raw_tenders(keywords: str = ""):
    """Get raw tender data for debugging"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")
        
        params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "pageSize": 10,  # Small sample
            "page": 1,
        }
        
        response = requests.get(
            "https://ocds-api.etenders.gov.za/api/OCDSReleases",
            params=params,
            timeout=25
        )
        
        response.raise_for_status()
        data = response.json()
        releases = data.get('releases', [])
        
        # Return raw data for inspection
        sample_tenders = []
        for i, release in enumerate(releases[:5]):  # First 5 tenders
            tender = release.get('tender', {})
            sample_tenders.append({
                'index': i,
                'id': release.get('id', 'No ID'),
                'title': tender.get('title', 'No Title'),
                'description': tender.get('description', 'No Description')[:200] + '...' if tender.get('description') else 'No Description',
                'buyer': tender.get('procuringEntity', {}).get('name', 'Unknown'),
                'value': tender.get('value', {}),
                'contains_construction': 'construction' in tender.get('title', '').lower() or 'construction' in tender.get('description', '').lower()
            })
        
        return {
            "success": True,
            "total_tenders": len(releases),
            "search_keywords": keywords,
            "sample_tenders": sample_tenders,
            "params_used": params
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
@router.get("/debug/tender-structure")
async def debug_tender_structure():
    """Debug endpoint to see the actual structure of OCDS responses"""
    try:
        # Get a small sample of tenders
        tenders = ocds_service.search_tenders("construction", {})
        
        if not tenders:
            return {"error": "No tenders found to analyze"}
        
        # Analyze the first tender's structure
        sample_tender = tenders[0]
        
        # Look for documents in common locations
        document_locations = {
            'root_documents': sample_tender.get('documents', 'NOT_FOUND'),
            'tender_documents': sample_tender.get('tender', {}).get('documents', 'NOT_FOUND'),
            'releases_documents': sample_tender.get('releases', [{}])[0].get('documents', 'NOT_FOUND') if sample_tender.get('releases') else 'NO_RELEASES',
        }
        
        # Also check for any URL-like fields that might be documents
        def find_potential_document_urls(obj, path="", max_depth=3):
            if max_depth == 0:
                return []
            
            urls = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and ('http' in value.lower() and ('pdf' in value.lower() or 'doc' in value.lower())):
                        urls.append({current_path: value})
                    elif isinstance(value, (dict, list)):
                        urls.extend(find_potential_document_urls(value, current_path, max_depth-1))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    urls.extend(find_potential_document_urls(item, f"{path}[{i}]", max_depth-1))
            return urls
        
        potential_urls = find_potential_document_urls(sample_tender)
        
        # Get important keys for overview
        important_keys = list(sample_tender.keys())
        
        return {
            "message": "Debug analysis of OCDS structure",
            "total_tenders_found": len(tenders),
            "sample_tender_keys": important_keys,
            "document_locations": document_locations,
            "potential_document_urls": potential_urls[:10],  # Limit to first 10
            "has_tender_key": 'tender' in sample_tender,
            "tender_keys": list(sample_tender.get('tender', {}).keys()) if sample_tender.get('tender') else 'NO_TENDER_KEY'
        }
        
    except Exception as e:
        return {"error": str(e)}
@router.post("/api/tenders/{tender_id}/auto-summarize")
async def auto_summarize_tender_documents(
    tender_id: str,
    db: Session = Depends(get_db)
):
    """
    Automatically download, process, and summarize documents for a tender
    """
    try:
        # Get tender from database
        tender = db.query(Tender).filter(Tender.ocds_id == tender_id).first()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        
        # Check if tender has documents
        documents = tender.documents or []
        if not documents:
            return {
                "success": False,
                "message": "No documents found for this tender",
                "tender_id": tender_id
            }
        
        print(f"📄 Found {len(documents)} documents for tender {tender_id}")
        
        # Process all documents
        from app.services.document_service import document_service
        processing_result = await document_service.process_tender_documents(documents)
        
        # Store the results (you might want to create a new table for this)
        # For now, we'll return them directly
        
        return {
            "success": True,
            "tender_id": tender_id,
            "tender_title": tender.title,
            "total_documents": len(documents),
            "processed_documents": processing_result["total_documents_processed"],
            "overall_summary": processing_result["overall_summary"],
            "overall_highlights": processing_result["overall_highlights"],
            "document_summaries": processing_result["document_summaries"]
        }
        
    except Exception as e:
        print(f"❌ Auto-summarization error: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-summarization failed: {str(e)}")

@router.get("/api/tenders/{tender_id}/documents")
async def get_tender_documents(tender_id: str, db: Session = Depends(get_db)):
    """
    Get document information for a tender
    """
    try:
        tender = db.query(Tender).filter(Tender.ocds_id == tender_id).first()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        
        return {
            "success": True,
            "tender_id": tender_id,
            "tender_title": tender.title,
            "documents": tender.documents or [],
            "total_documents": len(tender.documents) if tender.documents else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")