from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "testdb"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB"}

@app.get("/users")
async def get_users():
    users = await db["users"].find().to_list(length=100)
    return users


