# reset_workspace.py
# reset_workspace.py
from app.database import engine, Base
from app.models.workspace import WorkspaceTender, WorkspaceNote, TeamNotification
from app.models.user_models import Team, User, CompanyProfile
from app.models.tender_models import Tender

def reset_workspace_tables():
    print("🔧 Resetting workspace tables...")
    
    try:
        # Drop tables in correct order to handle foreign key constraints
        print("🗑️ Dropping tables...")
        
        # First drop tables that have foreign keys to other tables we're dropping
        Base.metadata.drop_all(bind=engine, tables=[
            TeamNotification.__table__,
            WorkspaceNote.__table__,
            WorkspaceTender.__table__,
        ])
        
        print("✅ Tables dropped successfully")
        
        # Recreate tables in correct order
        print("🔄 Recreating tables...")
        Base.metadata.create_all(bind=engine, tables=[
            WorkspaceTender.__table__,
            WorkspaceNote.__table__,
            TeamNotification.__table__,
        ])
        
        print("✅ Workspace tables recreated successfully!")
        
    except Exception as e:
        print(f"❌ Error resetting workspace tables: {e}")
        raise

if __name__ == "__main__":
    reset_workspace_tables()