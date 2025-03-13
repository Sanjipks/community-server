from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_database
from app.models import postedCategory
from dotenv import load_dotenv
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
    return users

# @app.get("/posted-categories")
# async def posted_categories():
#     postedCategories = await db["postedCategory"].find().to_list(length=100)
#     return postedCategories

@app.get("/posted-categories")
async def posted_categories():
    postedCategories = await db["postedCategory"].find().to_list(length=100)
    for category in postedCategories:
        category["id"] = str(category["_id"])
        del category["_id"]
    return postedCategories


@app.post("/posted-categories")
async def post_category(category: postedCategory):
    category_dict = category.model_dump()
    result = await db["postedCategory"].insert_one(category_dict)
    if result.inserted_id:
        return {"message": "Category Posted Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post category")