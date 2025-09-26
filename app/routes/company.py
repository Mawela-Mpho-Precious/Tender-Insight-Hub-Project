# routes/company.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_models import CompanyProfile, Team, User, INDUSTRY_SECTORS, PROVINCES, CERTIFICATION_OPTIONS
from app.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/company", tags=["company"])

class CompanyProfileCreate(BaseModel):
    company_name: str
    registration_number: str = None
    vat_number: str = None
    industry_sector: str
    services_provided: str
    years_of_experience: int = 0
    cidb_grading: str = None
    bbbee_level: str = None
    operating_provinces: str = None
    contact_email: str = None
    contact_phone: str = None
    physical_address: str = None
    number_of_employees: int = 0
    annual_turnover: str = None

@router.get("/options/industries")
async def get_industry_options():
    """Get available industry sectors"""
    return {"industries": INDUSTRY_SECTORS}

@router.get("/options/provinces")
async def get_province_options():
    """Get available provinces"""
    return {"provinces": PROVINCES}

@router.get("/options/certifications")
async def get_certification_options():
    """Get available certification options"""
    return {"certifications": CERTIFICATION_OPTIONS}

@router.post("/profiles")
async def create_company_profile(
    profile_data: CompanyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update company profile"""
    try:
        # Check if profile already exists
        existing_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == current_user.team_id).first()
        
        if existing_profile:
            # Update existing profile
            for field, value in profile_data.dict().items():
                if value is not None:
                    setattr(existing_profile, field, value)
        else:
            # Create new profile
            new_profile = CompanyProfile(
                **profile_data.dict(),
                team_id=current_user.team_id
            )
            db.add(new_profile)
        
        db.commit()
        return {"message": "Company profile saved successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

@router.get("/profiles")
async def get_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company profile for current user's team"""
    profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == current_user.team_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    
    return {
        "company_name": profile.company_name,
        "registration_number": profile.registration_number,
        "vat_number": profile.vat_number,
        "industry_sector": profile.industry_sector,
        "services_provided": profile.services_provided,
        "years_of_experience": profile.years_of_experience,
        "cidb_grading": profile.cidb_grading,
        "bbbee_level": profile.bbbee_level,
        "operating_provinces": profile.operating_provinces,
        "contact_email": profile.contact_email,
        "contact_phone": profile.contact_phone,
        "physical_address": profile.physical_address,
        "number_of_employees": profile.number_of_employees,
        "annual_turnover": profile.annual_turnover
    }
# In your company.py routes, add proper response models
