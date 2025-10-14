# quick_fix.py
from app.database import SessionLocal
from sqlalchemy import text

def quick_fix():
    print("🔧 Quick fix: Creating workspace tables...")
    
    db = SessionLocal()
    
    try:
        # Drop tables if they exist (be careful with this in production)
        db.execute(text("DROP TABLE IF EXISTS team_notifications"))
        db.execute(text("DROP TABLE IF EXISTS workspace_notes")) 
        db.execute(text("DROP TABLE IF EXISTS workspace_tenders"))
        db.commit()
        
        # Create tables in correct order
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
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    quick_fix()