import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

MONGO_URI = os.getenv("TODO_MONGO_URI")
DATABASE_NAME = "todo"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
