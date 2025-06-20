from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_database
from app.models import postCommunityPost, postJoke, user
from app.routes.community_posts import router as community_posts_router
from app.routes.categories import router as categories_router
from app.routes.fun import router as fun_router

from dotenv import load_dotenv
from bson import ObjectId
load_dotenv()
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    db = await get_database()
    yield
   

app = FastAPI(lifespan=lifespan)

ORIGINS = os.getenv("ORIGINS")

# Configure CORS
origins = [
   ORIGINS   
]

print("Routers linked successfully!")
app.include_router(community_posts_router, prefix="/community", tags=["Community Posts"])
app.include_router(categories_router, prefix="/categories", tags=["Categories"])
app.include_router(fun_router, prefix="/fun", tags=["fun"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB"}



@app.get("/users")
async def get_users():
    users = await db["user"].find().to_list(length=100)
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
   
    return users

@app.post("/chatlist/adduser") 
async def add_user(user: postCommunityPost):
    user_dict = user.model_dump()
    result = await db["user"].insert_one(user_dict)
    if result.inserted_id:
        return {"message": "User added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add user")
    
@app.get("/chatlist/getusers")
async def get_users_list():
    users = await db["user"].find().to_list(length=100)
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users

@app.delete("/chatlist/removeuser") 
async def remove_user(request: user):
    try:
        print('Received ID:', request.id)
        # Convert the string id to ObjectId
        object_id = ObjectId(request.id)
        print('ObjectId:', object_id)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await db["user"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")