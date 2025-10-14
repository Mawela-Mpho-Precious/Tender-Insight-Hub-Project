# reset_workspace_table.py
from app.database import engine, Base, SessionLocal
from app.models.workspace import WorkspaceTender

# Drop the table
WorkspaceTender.__table__.drop(engine)

# Recreate the table with correct schema
Base.metadata.create_all(bind=engine)

print("✅ Workspace table recreated with correct schema")