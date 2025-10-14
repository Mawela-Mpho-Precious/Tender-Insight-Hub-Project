# simple_setup.py
from app.database import SessionLocal
from sqlalchemy import text

def setup_simple_workspace():
    print("🚀 Setting up simple workspace tables...")
    
    db = SessionLocal()
    
    try:
        # Create simple workspace_tenders table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS workspace_tenders (
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.commit()
        print("✅ Simple workspace table created!")
        
        # Check if we have any data
        result = db.execute(text("SELECT COUNT(*) FROM workspace_tenders"))
        count = result.scalar()
        print(f"📊 Current tenders in workspace: {count}")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_simple_workspace()