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
