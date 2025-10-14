from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Form,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil, os, json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_models import CompanyProfile, User
from app.auth import get_current_user , get_current_user_optional
from typing import Optional
from app.services.mongodb_service import mongodb_service

from app.services.tender_doc_services import (
    extract_text_from_pdf,
    extract_text_from_zip,
    summarize_text,
    highlight_key_points,
    readiness_scoring,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for match scores (replace with database later)
match_scores_storage = {}

@router.post("/api/tenders/summarize")
async def summarize_tender(
    file: UploadFile = File(None),
    tender_data: str = Form(None)
):
    """
    Summarize tender from either file upload or JSON data
    """
    try:
        print(f"🔍 DEBUG: Received request - file: {file}, tender_data: {tender_data}")
        
        text = ""
        tender_id = "file_upload"
        
        # Handle file upload
        if file and file.filename:
            print(f"🔍 DEBUG: Processing file upload - {file.filename}")
            # ... your existing file processing code ...
        
        # Handle JSON data from form
        elif tender_data:
            print(f"🔍 DEBUG: Processing tender_data - {tender_data}")
            try:
                data = json.loads(tender_data)
                tender_id = data.get('tender_id', 'unknown')
                text = f"""
                TENDER: {data.get('title', '')}
                DESCRIPTION: {data.get('description', '')}
                ADDITIONAL INFO: {data.get('text_content', '')}
                """
                print(f"🔍 DEBUG: Parsed JSON - Tender ID: {tender_id}")
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: JSON decode error - {e}")
                return {"error": "Invalid JSON data"}
        else:
            print("❌ DEBUG: Neither file nor tender_data provided")
            return {"error": "Either file or tender data must be provided"}

        if not text.strip():
            return {"error": "No text content to summarize"}

        # Generate summary
        summary = summarize_text(text)
        highlights = highlight_key_points(text)

        print(f"✅ DEBUG: Summary generated successfully for tender {tender_id}")

        # STORE IN MONGODB
        summary_data = {
            "summary": summary,
            "highlights": highlights,
            "tender_id": tender_id,
            "documents_processed": 1 if file else 0
        }
        
        # Store in MongoDB
        await mongodb_service.store_ai_analysis(tender_id, summary_data)
        
        # Log user activity
        user_id = "anonymous"  # Replace with actual user ID when auth is available
        await mongodb_service.log_user_activity(user_id, "summarize", {
            "tender_id": tender_id,
            "file_uploaded": bool(file),
            "summary_length": len(summary)
        })

        return {
            "success": True,
            "summary": summary,
            "highlights": highlights,
            "tender_id": tender_id
        }

    except Exception as e:
        print(f"❌ DEBUG: Summarization error - {e}")
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@router.post("/api/tenders/{tender_id}/match")
async def match_tender(
    tender_id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)  
):
    """
    Compare summarized tender with REAL company profile from database
    """
    try:
        data = await request.json()
        summary = data.get('summary', '')
        
        print(f"🔍 Matching tender {tender_id} with company profile...")
        
        if not summary:
            return {"error": "No summary provided for matching"}

        if current_user: 
            company_profile = db.query(CompanyProfile).filter(
            CompanyProfile.team_id == current_user.team_id
        ).first()
        else:
            company_profile = db.query(CompanyProfile).first()
        
        if not company_profile:
            company_profile = CompanyProfile(
                company_name="Demo Construction Company",
                industry_sector="Construction",
                services_provided="Building Construction, Civil Engineering, Road Works",
                years_of_experience=8,
                cidb_grading="7CE",
                bbbee_level="2",
                operating_provinces="Gauteng, Western Cape, KwaZulu-Natal",
                number_of_employees=45,
                annual_turnover="R 50,000,000",
                team_id=1  # Default team ID
            )
            db.add(company_profile)
            db.commit()
            db.refresh(company_profile)
            print("🏢 Created default company profile for testing")
            

        # Convert company profile to the format expected by readiness_scoring
        company_data = {
            "name": company_profile.company_name,
            "industry": company_profile.industry_sector,
            "services": company_profile.services_provided.split(',') if company_profile.services_provided else [],
            "certifications": _extract_certifications(company_profile),
            "geographic_coverage": company_profile.operating_provinces.split(',') if company_profile.operating_provinces else [],
            "years_of_experience": company_profile.years_of_experience,
            "annual_turnover": _parse_turnover(company_profile.annual_turnover),
            "employee_count": company_profile.number_of_employees,
            "black_owned": _is_black_owned(company_profile.bbbee_level),
            "sme": company_profile.number_of_employees < 50  # SME definition
        }
        
        print(f"🏢 Using company: {company_data['name']}")
        if current_user:
            print(f"👤 Authenticated user: {current_user.email}")
        else:
            print("👤 Using demo mode (no authentication)")
            
        
        # Calculate readiness score
        match_result = readiness_scoring(summary, company_data)
        
        company_profile_id = str(company_profile.id) if hasattr(company_profile, 'id') else "default"
        await mongodb_service.store_match_result(tender_id, company_profile_id, match_result)

        
        

        # Store the match result
        match_scores_storage[tender_id] = {
            **match_result,
            "tender_id": tender_id,
            "timestamp": datetime.now().isoformat(),
            "company_used": company_data['name'],
            "authenticated": current_user is not None
        }

        user_id = str(current_user.id) if current_user else "anonymous"
        await mongodb_service.log_user_activity(user_id, "match_tender", {
            "tender_id": tender_id,
            "suitability_score": match_result["suitability_score"],
            "matched_criteria": match_result["matched_criteria"]
        })

        
        print(f"✅ Match completed - Score: {match_result['suitability_score']}%")

        return {
            "success": True,
            "tender_id": tender_id,
            **match_result,
            "authenticated": current_user is not None,
            "stored_in_mongodb": True
        }
        
    except Exception as e:
        print(f"❌ Matching error: {e}")
        return {
            "success": False,
            "detail": f"Matching error: {str(e)}"
        }

def _extract_certifications(company_profile):
    """Extract certifications from company profile"""
    certifications = []
    if company_profile.cidb_grading:
        certifications.append(f"CIDB {company_profile.cidb_grading}")
    if company_profile.bbbee_level:
        certifications.append(f"BBBEE {company_profile.bbbee_level}")
    return certifications

def _parse_turnover(turnover_str):
    """Parse turnover string to numeric value"""
    if not turnover_str:
        return 0
    try:
        # Handle formats like "R 5,000,000" or "5 million"
        turnover_str = turnover_str.upper().replace('R', '').replace(' ', '').replace(',', '')
        if 'MILLION' in turnover_str:
            return int(float(turnover_str.replace('MILLION', '')) * 1000000)
        return int(turnover_str)
    except:
        return 0

def _is_black_owned(bbbee_level):
    """Determine if company is black-owned based on BBBEE level"""
    if not bbbee_level:
        return False
    # Assume levels 1-3 indicate significant black ownership
    return any(level in str(bbbee_level) for level in ['1', '2', '3'])

@router.get("/api/tenders/{tender_id}/match-score")
async def get_tender_match_score(tender_id: str):
    """
    Get stored match score for a tender
    """
    try:
        if tender_id in match_scores_storage:
            return {
                "success": True,
                "tender_id": tender_id,
                **match_scores_storage[tender_id]
            }
        else:
            return {
                "success": True,
                "tender_id": tender_id,
                "suitability_score": None,
                "message": "No match score calculated yet"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match score: {str(e)}")

@router.get("/api/company/match-history")
async def get_company_match_history():
    """
    Get all tender match scores for the company
    """
    try:
        results = []
        for tender_id, score_data in match_scores_storage.items():
            results.append({
                "tender_id": tender_id,
                "suitability_score": score_data["suitability_score"],
                "recommendation": score_data["recommendation"],
                "matched_criteria": score_data.get("matched_criteria", 0),
                "total_criteria": score_data.get("total_criteria", 0),
                "last_updated": score_data.get("timestamp", "Unknown")
            })
        
        return {
            "success": True,
            "total_matches": len(results),
            "average_score": sum(r["suitability_score"] for r in results) / len(results) if results else 0,
            "matches": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match history: {str(e)}")

# Serve the HTML form
@router.get("/summarize", response_class=HTMLResponse)
async def show_summarize_form(request: Request):
    return templates.TemplateResponse("partials/summarize.html", {"request": request})

# Test endpoint
@router.get("/api/tenders/test-summarize")
async def test_summarize():
    """
    Test endpoint to verify summarization service works
    """
    try:
        test_text = """
        This is a test tender document for construction services. 
        The project involves building a new community center in Gauteng province. 
        Budget: R5 million. Deadline: 30 days from publication. 
        Required: CIDB grading 6CE, 5+ years experience, BBBEE level 2.
        """
        
        summary = summarize_text(test_text)
        highlights = highlight_key_points(test_text)
        
        return {
            "success": True,
            "summary": summary,
            "highlights": highlights,
            "message": "Summarization service is working correctly"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/tenders/summarize-from-data")
async def summarize_tender_from_data(tender_data: dict):
    """
    Summarize tender from provided data (not file upload)
    """
    try:
        # Extract text from the tender data
        text = f"""
        Tender Title: {tender_data.get('title', '')}
        Description: {tender_data.get('description', '')}
        Buyer: {tender_data.get('buyer', {}).get('name', '')}
        Province: {tender_data.get('province', '')}
        Budget: {tender_data.get('value', {}).get('amount', '')}
        """
        
        # Generate summary
        summary = summarize_text(text)
        highlights = highlight_key_points(text)

        return {
            "success": True,
            "summary": summary,
            "highlights": highlights,
            "tender_id": tender_data.get('tender_id')
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/tenders/{tender_id}/summarize")
async def summarize_specific_tender(tender_id: str):
    """
    Summarize a specific tender by ID
    """
    try:
        # Mock summary for testing
        mock_summary = f"AI-generated summary for tender {tender_id}. This would contain key requirements, deadlines, and important specifications extracted from the tender documents."
        
        mock_highlights = [
            "Key requirement: 5+ years experience in similar projects",
            "Deadline: 30 days from publication",
            "Budget range: R1-5 million",
            "Required certifications: CIDB grading 5CE or higher",
            "Location: Primarily Gauteng province"
        ]
        
        return {
            "success": True,
            "summary": mock_summary,
            "highlights": mock_highlights,
            "tender_id": tender_id
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Temporary workspace endpoints (move to separate file later)


@router.get("/api/tenders/{tender_id}/documents-info")
async def get_tender_documents_info(tender_id: str, db: Session = Depends(get_db)):
    """
    Get document information and test if documents can be processed
    """
    try:
        tender = db.query(Tender).filter(Tender.ocds_id == tender_id).first()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        
        documents = tender.documents or []
        
        # Test if documents have valid URLs
        document_test = []
        for doc in documents:
            has_url = bool(doc.get('url'))
            document_test.append({
                "title": doc.get('title', 'Unknown'),
                "has_url": has_url,
                "url": doc.get('url'),
                "can_download": has_url and doc.get('url', '').startswith('http')
            })
        
        return {
            "success": True,
            "tender_id": tender_id,
            "total_documents": len(documents),
            "documents": document_test,
            "has_downloadable_docs": any(doc["can_download"] for doc in document_test)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document info: {str(e)}")    
@router.get("/api/analytics/summary-stats")
async def get_summary_stats(db: Session = Depends(get_db)):
    """Get analytics data from MongoDB"""
    try:
        from app.services.mongodb_service import mongodb_service
        
        # This would aggregate data from MongoDB
        # For now, return basic stats
        return {
            "success": True,
            "analytics": {
                "total_analyses": 0,  # Would count from MongoDB
                "average_processing_time": 0,
                "most_analyzed_tenders": []
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@router.get("/api/company/{company_id}/match-history")
async def get_company_match_history(company_id: str):
    """Get match history for a company from MongoDB"""
    try:
        from app.services.mongodb_service import mongodb_service
        
        history = await mongodb_service.get_company_match_history(company_id)
        
        return {
            "success": True,
            "company_id": company_id,
            "match_history": history,
            "total_matches": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting match history: {str(e)}")
    
@router.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics data from MongoDB"""
    try:
        analytics = await mongodb_service.get_analytics_summary()
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Analytics error: {str(e)}"
        }
@router.get("/api/debug/mongodb-test")
async def test_mongodb():
    """Test MongoDB connection and basic operations"""
    try:
        # Test connection
        db = await get_mongo_db()
        if not db:
            return {"success": False, "error": "MongoDB not connected"}
        
        # Test insert
        test_doc = {
            "test": "MongoDB connection test",
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
        collection = mongodb.get_collection("connection_test")
        result = await collection.insert_one(test_doc)
        
        # Test read
        found_doc = await collection.find_one({"_id": result.inserted_id})
        
        return {
            "success": True,
            "message": "MongoDB is working!",
            "inserted_id": str(result.inserted_id),
            "test_document": str(found_doc)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"MongoDB test failed: {str(e)}"
        }
