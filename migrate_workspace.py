# migrate_workspace.py
from app.database import engine, SessionLocal
from sqlalchemy import text

def migrate_workspace_tables():
    print("🚀 Running workspace migration...")
    
    db = SessionLocal()
    
    try:
        # Check if workspace_tenders table exists
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='workspace_tenders'
        """))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            print("📋 Workspace tables already exist")
            return
        
        # Create workspace_tenders table
        print("📦 Creating workspace_tenders table...")
        db.execute(text("""
            CREATE TABLE workspace_tenders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                tender_id VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                description TEXT,
                budget VARCHAR,
                province VARCHAR,
                buyer_name VARCHAR,
                deadline VARCHAR,
                ai_summary TEXT,
                match_score FLOAT DEFAULT 0,
                status VARCHAR DEFAULT 'interested',
                last_updated_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (last_updated_by) REFERENCES users (id)
            )
        """))
        
        # Create workspace_notes table
        print("📝 Creating workspace_notes table...")
        db.execute(text("""
            CREATE TABLE workspace_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_tender_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_task INTEGER DEFAULT 0,
                task_assigned_to INTEGER,
                task_due_date DATETIME,
                task_completed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_tender_id) REFERENCES workspace_tenders (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_assigned_to) REFERENCES users (id)
            )
        """))
        
        # Create team_notifications table
        print("🔔 Creating team_notifications table...")
        db.execute(text("""
            CREATE TABLE team_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                workspace_tender_id INTEGER,
                type VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (workspace_tender_id) REFERENCES workspace_tenders (id)
            )
        """))
        
        db.commit()
        print("✅ Workspace tables created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_workspace_tables()