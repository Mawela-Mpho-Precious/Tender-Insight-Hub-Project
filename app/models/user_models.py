from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    plan_tier = Column(String, default="free")  # free, basic, pro
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="team")
    company_profile = relationship("CompanyProfile", back_populates="team", uselist=False, cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="users")

class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    registration_number = Column(String)  # CIPC registration number
    vat_number = Column(String)
    
    # Industry information
    industry_sector = Column(String, nullable=False)
    services_provided = Column(Text)  # Comma-separated services
    years_of_experience = Column(Integer, default=0)
    
    # Certifications (stored as JSON for flexibility)
    certifications = Column(JSON, default=dict)
    bbbee_level = Column(String)  # BBBEE level: 1, 2, 3, etc.
    cidb_grading = Column(String)  # CIDB grading
    
    # Geographic coverage
    geographic_coverage = Column(JSON, default=dict)
    operating_provinces = Column(Text)  # Comma-separated provinces
    
    # Contact information
    contact_email = Column(String)
    contact_phone = Column(String)
    physical_address = Column(Text)
    website = Column(String)
    
    # Additional details
    number_of_employees = Column(Integer, default=0)
    annual_turnover = Column(String)  # Could be a range like "1M-5M"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    team = relationship("Team", back_populates="company_profile")

# Certification options (can be used for dropdowns)
CERTIFICATION_OPTIONS = {
    "cidb": ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8", "Grade 9"],
    "bbbee": ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8"],
    "other": ["ISO 9001", "ISO 14001", "OHSAS 18001", "SANS 10400", "NHBRC", "CSD Registered"]
}

INDUSTRY_SECTORS = [
    "Construction & Engineering",
    "IT & Technology Services",
    "Security Services",
    "Cleaning & Maintenance",
    "Transport & Logistics",
    "Education & Training",
    "Healthcare Services",
    "Manufacturing",
    "Agriculture",
    "Mining",
    "Tourism & Hospitality",
    "Financial Services",
    "Consulting",
    "Other"
]

PROVINCES = [
    "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal",
    "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"
]