from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.workspace import WorkspaceTender, WorkspaceTenderNote

class NoteCreate(BaseModel):
    content: str
    is_task: bool = False
    task_assigned_to: Optional[int] = None
    task_due_date: Optional[datetime] = None

class NoteUpdate(BaseModel):
    content: Optional[str] = None
    task_completed: Optional[bool] = None


router = APIRouter()

@router.post("/tenders")
async def save_tender_to_workspace(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Save a tender to workspace
    """
    try:
        data = await request.json()
        
        print(f"💾 Saving tender to workspace: {data.get('tender_id')}")
        
        # Check if tender already exists in workspace
        existing = db.query(WorkspaceTender).filter(
            WorkspaceTender.tender_id == data['tender_id']
        ).first()
        
        if existing:
            return {
                "success": False,
                "detail": "Tender already in workspace"
            }
        
        # Parse deadline if provided
        deadline = None
        if data.get('deadline'):
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except:
                pass
        
        # Create new workspace entry
        workspace_tender = WorkspaceTender(
            tender_id=data['tender_id'],
            user_id=1,
            company_id=1,
            title=data.get('title', 'No Title'),
            description=data.get('description', ''),
            deadline=deadline,
            budget=data.get('budget'),
            province=data.get('province'),
            buyer_name=data.get('buyer_name'),
            ai_summary=data.get('ai_summary', ''),
            match_score=data.get('match_score'),
            match_recommendation=data.get('match_recommendation', 'Saved from search'),
            status="pending"  # Now using string
        )
        
        db.add(workspace_tender)
        db.commit()
        db.refresh(workspace_tender)
        
        return {
            "success": True,
            "message": "Tender saved to workspace",
            "workspace_tender_id": workspace_tender.id
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving tender: {e}")
        return {
            "success": False,
            "detail": f"Error saving tender: {str(e)}"
        }

@router.get("/tenders")
async def get_workspace_tenders(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all tenders in workspace, optionally filtered by status
    """
    try:
        query = db.query(WorkspaceTender)
        
        if status:
            query = query.filter(WorkspaceTender.status == status)
        
        # Sort by match score (highest first), then by deadline (soonest first)
        workspace_tenders = query.order_by(
            WorkspaceTender.match_score.desc().nullslast(),
            WorkspaceTender.deadline.asc().nullslast()
        ).all()
        
        return {
            "success": True,
            "tenders": [
                {
                    "id": wt.id,
                    "tender_id": wt.tender_id,
                    "title": wt.title,
                    "deadline": wt.deadline.isoformat() if wt.deadline else None,
                    "budget": wt.budget,
                    "province": wt.province,
                    "buyer_name": wt.buyer_name,
                    "ai_summary": wt.ai_summary,
                    "match_score": wt.match_score,
                    "match_recommendation": wt.match_recommendation,
                    "status": wt.status,
                    "created_at": wt.created_at.isoformat() if wt.created_at else None
                }
                for wt in workspace_tenders
            ],
            "total_count": len(workspace_tenders)
        }
        
    except Exception as e:
        print(f"❌ Error fetching workspace tenders: {e}")
        return {
            "success": False,
            "detail": f"Error fetching workspace tenders: {str(e)}"
        }

@router.put("/tenders/{workspace_tender_id}/status")
async def update_tender_status(
    workspace_tender_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update tender status in workspace
    """
    try:
        data = await request.json()
        new_status = data['status']
        
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            return {
                "success": False,
                "detail": "Workspace tender not found"
            }
        
        # Update status
        workspace_tender.status = new_status
        db.commit()
        
        return {
            "success": True,
            "message": f"Status updated to {new_status}",
            "status": new_status
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating status: {e}")
        return {
            "success": False,
            "detail": f"Error updating status: {str(e)}"
        }

@router.delete("/tenders/{workspace_tender_id}")
async def remove_tender_from_workspace(
    workspace_tender_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove tender from workspace
    """
    try:
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            return {
                "success": False,
                "detail": "Workspace tender not found"
            }
        
        db.delete(workspace_tender)
        db.commit()
        
        return {
            "success": True,
            "message": "Tender removed from workspace"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing tender: {e}")
        return {
            "success": False,
            "detail": f"Error removing tender: {str(e)}"
        }
class NoteCreate(BaseModel):
    content: str
    is_task: bool = False
    task_assigned_to: Optional[int] = None
    task_due_date: Optional[datetime] = None

class NoteUpdate(BaseModel):
    content: Optional[str] = None
    task_completed: Optional[bool] = None
   
@router.get("/tenders/{workspace_tender_id}/notes")
async def get_tender_notes(
    workspace_tender_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all notes for a workspace tender
    """
    try:
        # For now, return empty array since we don't have notes model yet
        # You'll need to create a WorkspaceTenderNotes model
        return {
            "success": True,
            "notes": []  # Return empty array for now
        }
        
    except Exception as e:
        print(f"❌ Error fetching notes: {e}")
        return {
            "success": False,
            "detail": f"Error fetching notes: {str(e)}"
        }

@router.post("/tenders/{workspace_tender_id}/notes")
async def add_tender_note(
    workspace_tender_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Add a note to a workspace tender
    """
    try:
        # Check if workspace tender exists
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            return {
                "success": False,
                "detail": "Workspace tender not found"
            }
        
        # TODO: Create a WorkspaceTenderNotes model and save the note
        # For now, return success but don't actually save
        print(f"📝 Would save note for tender {workspace_tender_id}: {note_data.content}")
        
        return {
            "success": True,
            "message": "Note added successfully",
            "note": {
                "id": 1,  # Temporary
                "content": note_data.content,
                "is_task": note_data.is_task,
                "task_assigned_to": note_data.task_assigned_to,
                "task_due_date": note_data.task_due_date,
                "task_completed": False,
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ Error adding note: {e}")
        return {
            "success": False,
            "detail": f"Error adding note: {str(e)}"
        }
@router.get("/test")
async def test_workspace():
    return {"message": "Workspace routes are working!"}


@router.get("/tenders/debug")
async def debug_workspace_tenders(db: Session = Depends(get_db)):
    """
    Debug endpoint to see all workspace tenders
    """
    try:
        tenders = db.query(WorkspaceTender).all()
        
        return {
            "success": True,
            "tenders": [
                {
                    "id": wt.id,
                    "tender_id": wt.tender_id,
                    "title": wt.title,
                    "status": wt.status
                }
                for wt in tenders
            ],
            "total": len(tenders)
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Error: {str(e)}"
        }
@router.put("/tenders/{workspace_tender_id}/status")
async def update_tender_status(
    workspace_tender_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update tender status in workspace
    """
    try:
        data = await request.json()
        new_status = data.get('status')
        
        if not new_status:
            return {
                "success": False,
                "detail": "Status is required"
            }
        
        print(f"🔄 Updating status for workspace tender {workspace_tender_id} to {new_status}")
        
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            # Debug: show what tenders exist
            all_tenders = db.query(WorkspaceTender).all()
            tender_ids = [t.id for t in all_tenders]
            print(f"🔍 Tender {workspace_tender_id} not found. Available tenders: {tender_ids}")
            
            return {
                "success": False,
                "detail": f"Workspace tender not found. Available IDs: {tender_ids}",
                "available_ids": tender_ids
            }
        
        # Update status
        workspace_tender.status = new_status
        db.commit()
        
        print(f"✅ Successfully updated tender {workspace_tender_id} to {new_status}")
        
        return {
            "success": True,
            "message": f"Status updated to {new_status}",
            "status": new_status
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating status: {e}")
        return {
            "success": False,
            "detail": f"Error updating status: {str(e)}"
        }

@router.get("/tenders/{workspace_tender_id}/notes")
async def get_tender_notes(
    workspace_tender_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all notes for a workspace tender
    """
    try:
        # Check if workspace tender exists
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            return {
                "success": False,
                "detail": "Workspace tender not found"
            }
        
        # Get all notes for this tender
        notes = db.query(WorkspaceTenderNote).filter(
            WorkspaceTenderNote.workspace_tender_id == workspace_tender_id
        ).order_by(WorkspaceTenderNote.created_at.desc()).all()
        
        return {
            "success": True,
            "notes": [
                {
                    "id": note.id,
                    "content": note.content,
                    "is_task": note.is_task,
                    "task_assigned_to": note.task_assigned_to,
                    "task_due_date": note.task_due_date.isoformat() if note.task_due_date else None,
                    "task_completed": note.task_completed,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                    "updated_at": note.updated_at.isoformat() if note.updated_at else None
                }
                for note in notes
            ]
        }
        
    except Exception as e:
        print(f"❌ Error fetching notes: {e}")
        return {
            "success": False,
            "detail": f"Error fetching notes: {str(e)}"
        }

@router.post("/tenders/{workspace_tender_id}/notes")
async def add_tender_note(
    workspace_tender_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Add a note to a workspace tender
    """
    try:
        # Check if workspace tender exists
        workspace_tender = db.query(WorkspaceTender).filter(
            WorkspaceTender.id == workspace_tender_id
        ).first()
        
        if not workspace_tender:
            return {
                "success": False,
                "detail": "Workspace tender not found"
            }
        
        # Create the note
        note = WorkspaceTenderNote(
            workspace_tender_id=workspace_tender_id,
            content=note_data.content,
            is_task=note_data.is_task,
            task_assigned_to=note_data.task_assigned_to,
            task_due_date=note_data.task_due_date
        )
        
        db.add(note)
        db.commit()
        db.refresh(note)
        
        return {
            "success": True,
            "message": "Note added successfully",
            "note": {
                "id": note.id,
                "content": note.content,
                "is_task": note.is_task,
                "task_assigned_to": note.task_assigned_to,
                "task_due_date": note.task_due_date.isoformat() if note.task_due_date else None,
                "task_completed": note.task_completed,
                "created_at": note.created_at.isoformat() if note.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding note: {e}")
        return {
            "success": False,
            "detail": f"Error adding note: {str(e)}"
        }

@router.put("/tenders/{workspace_tender_id}/notes/{note_id}")
async def update_tender_note(
    workspace_tender_id: int,
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a note (mark task complete, edit content, etc.)
    """
    try:
        # Check if note exists and belongs to this tender
        note = db.query(WorkspaceTenderNote).filter(
            WorkspaceTenderNote.id == note_id,
            WorkspaceTenderNote.workspace_tender_id == workspace_tender_id
        ).first()
        
        if not note:
            return {
                "success": False,
                "detail": "Note not found"
            }
        
        # Update fields if provided
        if note_data.content is not None:
            note.content = note_data.content
            
        if note_data.task_completed is not None:
            note.task_completed = note_data.task_completed
        
        db.commit()
        db.refresh(note)
        
        return {
            "success": True,
            "message": "Note updated successfully",
            "note": {
                "id": note.id,
                "content": note.content,
                "is_task": note.is_task,
                "task_assigned_to": note.task_assigned_to,
                "task_due_date": note.task_due_date.isoformat() if note.task_due_date else None,
                "task_completed": note.task_completed,
                "updated_at": note.updated_at.isoformat() if note.updated_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating note: {e}")
        return {
            "success": False,
            "detail": f"Error updating note: {str(e)}"
        }

@router.delete("/tenders/{workspace_tender_id}/notes/{note_id}")
async def delete_tender_note(
    workspace_tender_id: int,
    note_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a note from a workspace tender
    """
    try:
        # Check if note exists and belongs to this tender
        note = db.query(WorkspaceTenderNote).filter(
            WorkspaceTenderNote.id == note_id,
            WorkspaceTenderNote.workspace_tender_id == workspace_tender_id
        ).first()
        
        if not note:
            return {
                "success": False,
                "detail": "Note not found"
            }
        
        db.delete(note)
        db.commit()
        
        return {
            "success": True,
            "message": "Note deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting note: {e}")
        return {
            "success": False,
            "detail": f"Error deleting note: {str(e)}"
        }


