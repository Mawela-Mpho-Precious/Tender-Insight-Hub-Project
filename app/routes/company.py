from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_models import CompanyProfile, Team
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/company", tags=["company"])

# Pydantic models for request/response
class CompanyProfileCreate(BaseModel):
    company_name: str
    industry_sector: str
    services_provided: str
    certifications: str
    geographic_coverage: str
    years_of_experience: int
    contact_email: str
    contact_phone: str

class CompanyProfileResponse(CompanyProfileCreate):
    id: int
    team_id: int

    class Config:
        from_attributes = True

@router.post("/profile", response_model=CompanyProfileResponse)
async def create_company_profile(
    profile: CompanyProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a company profile for the current team
    """
    # In a real app, you'd get team_id from authenticated user
    # For now, we'll use a hardcoded team ID for testing
    team_id = 1
    
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if profile already exists
    existing_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == team_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Company profile already exists for this team")
    
    # Create new profile
    db_profile = CompanyProfile(**profile.dict(), team_id=team_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/profile", response_model=CompanyProfileResponse)
async def get_company_profile(db: Session = Depends(get_db)):
    """
    Get company profile for the current team
    """
    team_id = 1  # Hardcoded for now
    
    profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == team_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    
    return profile

@router.put("/profile", response_model=CompanyProfileResponse)
async def update_company_profile(
    profile: CompanyProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Update company profile for the current team
    """
    team_id = 1  # Hardcoded for now
    
    db_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == team_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    
    # Update fields
    for field, value in profile.dict().items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile