# app/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/tender_insight")
        self.db_name = os.getenv("MONGODB_DB_NAME", "tender_insight")
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            print(f"🔗 Connecting to MongoDB: {self.mongo_uri}")
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            
            # Test the connection
            await self.db.command('ping')
            print("✅ MongoDB connected successfully!")
            
            # Create indexes for better performance
            await self._create_indexes()
            return self.db
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("💡 Make sure MongoDB is running: mongod")
            print("💡 Or install MongoDB: https://www.mongodb.com/try/download/community")
            return None
    
    async def _create_indexes(self):
        """Create necessary indexes"""
        try:
            # Index for AI analysis results
            await self.db.ai_analysis_results.create_index("tender_id")
            await self.db.ai_analysis_results.create_index("created_at")
            
            # Index for match results
            await self.db.match_results.create_index("tender_id")
            await self.db.match_results.create_index("company_profile_id")
            await self.db.match_results.create_index("created_at")
            
            # Index for user activities
            await self.db.user_activities.create_index("user_id")
            await self.db.user_activities.create_index("created_at")
            await self.db.user_activities.create_index("activity_type")
            
            print("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Could not create indexes: {e}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")
    
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