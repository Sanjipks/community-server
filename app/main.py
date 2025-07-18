from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_database
from app.routes.community_posts import router as community_posts_router
from app.routes.categories import router as categories_router
from app.routes.fun import router as fun_router
from app.routes.createUser import router as createUser_router
from app.routes.userlist import router as userlist_router
from app.routes.chatlist import router as chatlist_router
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

print("Routers linked successfully!")

app.include_router(community_posts_router, prefix="/community", tags=["Community Posts"])
app.include_router(categories_router, prefix="/categories", tags=["Categories"])
app.include_router(fun_router, prefix="/fun", tags=["fun"])
app.include_router(createUser_router, prefix="/create-user", tags=["Create User"])
app.include_router(userlist_router, prefix="/users", tags=["Userlist"])
app.include_router(chatlist_router, prefix="/chatlist", tags=["Chatlist"])

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






