from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class TenderMatchScore(Base):
    __tablename__ = "tender_match_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)  # Add when user auth is ready
    suitability_score = Column(Integer, nullable=False)  # 0-100
    recommendation = Column(String(255), nullable=False)
    checklist = Column(Text, nullable=True)  # Store checklist as JSON string
    matched_criteria_count = Column(Integer, default=0)
    total_criteria_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TenderMatchScore tender_id={self.tender_id} score={self.suitability_score}>"