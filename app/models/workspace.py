from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean  # ADD Boolean here
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # ADD this import
from app.database import Base


class WorkspaceTender(Base):
    _tablename_ = "workspace_tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    company_id = Column(Integer, nullable=False)
    
    # Tender details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    budget = Column(String(100))
    province = Column(String(100))
    buyer_name = Column(String(255))
    
    # AI and matching data
    ai_summary = Column(Text)
    match_score = Column(Integer)
    match_recommendation = Column(String(255))
    
    # Status tracking - use String instead of Enum
    status = Column(String(50), default="pending")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkspaceTenderNote(Base):
    _tablename_ = "workspace_tender_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_tender_id = Column(Integer, ForeignKey('workspace_tenders.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_task = Column(Boolean, default=False)
    task_assigned_to = Column(Integer, nullable=True)  # User ID
    task_due_date = Column(DateTime, nullable=True)
    task_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    workspace_tender = relationship("WorkspaceTender", backref="notes")


