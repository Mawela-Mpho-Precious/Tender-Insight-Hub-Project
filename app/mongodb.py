# app/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv


load_dotenv()

class MongoDB:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "tender_insight")
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test the connection
            await self.db.command('ping')
            print("✅ Connected to MongoDB successfully")
            return self.db
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return None
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection"""
        if self.db is None:
            raise Exception("MongoDB not connected. Call connect() first.")
        return self.db[collection_name]

# Global MongoDB instance
mongodb = MongoDB()

# FastAPI dependency
async def get_mongo_db():
    """Dependency to get MongoDB database instance"""
    if mongodb.db is None:
        await mongodb.connect()
    return mongodb.db