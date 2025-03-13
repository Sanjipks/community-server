import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "community"

if MONGO_URI is None:
    raise ValueError("MongoDB connection string not found in .env file")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

async def get_database():
    return db