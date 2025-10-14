# update_database.py
from app.database import engine, Base
from app.models.tender_models import Tender
from sqlalchemy import text

def update_database():
    try:
        # Method 1: Using SQLAlchemy to add the column
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                PRAGMA table_info(tenders)
            """))
            columns = [row[1] for row in result]
            
            if 'documents' not in columns:
                # Add the documents column
                connection.execute(text("""
                    ALTER TABLE tenders ADD COLUMN documents JSON
                """))
                connection.commit()
                print("✅ Successfully added 'documents' column to tenders table")
            else:
                print("✅ 'documents' column already exists")
                
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    update_database()