# create_notes_table.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(_file_)))

from app.database import engine, Base
from app.models.workspace import WorkspaceTenderNote

def create_notes_table():
    try:
        print("🔄 Creating workspace_tender_notes table...")
        WorkspaceTenderNote._table_.create(engine)
        print("✅ Notes table created successfully!")
    except Exception as e:
        print(f"❌ Error creating notes table: {e}")

if _name_ == "_main_":
    create_notes_table()