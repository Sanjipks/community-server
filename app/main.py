from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_database
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

@app.get("/posted-categories")
async def get_users():
    users = await db["postedCategory"].find().to_list(length=100)
    return users
