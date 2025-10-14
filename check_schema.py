# Create a temporary script to check your current schema
# check_schema.py
from app.database import engine, Base
from app.models.workspace import WorkspaceTender

# This will show the current table structure
print("Current table columns:")
inspector = inspect(engine)
columns = inspector.get_columns('workspace_tenders')
for column in columns:
    print(f"  - {column['name']}: {column['type']}")