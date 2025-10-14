from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict
from datetime import datetime

class CertificationBase(BaseModel):
    type: str
    level: Optional[str] = None
    number: Optional[str] = None
    expiry_date: Optional[str] = None

class CompanyProfileBase(BaseModel):
    company_name: str
    registration_number: Optional[str] = None
    vat_number: Optional[str] = None
    industry_sector: str
    services_provided: str
    years_of_experience: int = 0
    
    # Certifications
    certifications: Optional[Dict] = {}
    bbbee_level: Optional[str] = None
    cidb_grading: Optional[str] = None
    
    # Geographic coverage
    geographic_coverage: Optional[Dict] = {}
    operating_provinces: Optional[str] = None
    
    # Contact information
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    physical_address: Optional[str] = None
    website: Optional[str] = None
    
    # Additional details
    number_of_employees: int = 0
    annual_turnover: Optional[str] = None

class CompanyProfileCreate(CompanyProfileBase):
    team_id: int

class CompanyProfileUpdate(CompanyProfileBase):
    pass

class CompanyProfileResponse(CompanyProfileBase):
    id: int
    team_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CompanyProfileWithTeam(CompanyProfileResponse):
    team_name: str