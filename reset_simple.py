# reset_simple.py
from app.database import SessionLocal
from sqlalchemy import text

def reset_simple():
    print("🔄 Resetting workspace table...")
    
    db = SessionLocal()
    
    try:
        # Drop and recreate the table
        db.execute(text("DROP TABLE IF EXISTS workspace_tenders"))
        db.commit()
        
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.commit()
        print("✅ Workspace table reset successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_simple()