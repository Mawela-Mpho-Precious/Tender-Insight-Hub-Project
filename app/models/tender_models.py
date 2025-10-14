from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import JSON

class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    ocds_id = Column(String, unique=True, index=True)  # ID from OCDS API
    title = Column(String)
    description = Column(Text)  # Changed from String to Text for longer descriptions
    publishing_office = Column(String)
    province = Column(String)
    budget_range = Column(String)
    submission_deadline = Column(String)  # Changed from DateTime to String for flexibility
    estimated_value = Column(Float)
    buyer_name = Column(String)
    buyer_id = Column(String)
    documents = Column(JSON)
    
    # We'll store the raw OCDS data in MongoDB
