# reset_db.py
from app.database import Base, engine
from app import models  # make sure this imports all your model files

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database reset complete! Schema now matches your models.")
