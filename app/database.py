from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite Database for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./tender_hub.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB - we'll handle the connection gracefully
try:
    mongodb_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    mongodb = mongodb_client[os.getenv("MONGODB_DB_NAME", "tender_hub")]
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}. Using in-memory storage for development.")
    mongodb = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()