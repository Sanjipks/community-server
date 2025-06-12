from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_database
from app.models import postCommunityPost, postedCategory, postCategory, deleteCategory, postJoke, user
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

@app.get("/community-posts")
async def get_community_posts():
    posts = await db["communityPost"].find().to_list(length=100)
    for post in posts:
        post["id"] = str(post["_id"])
        del post["_id"]
    return posts

@app.post("/post-community-post")
async def post_community_post(post: postCommunityPost):
    post_dict = post.model_dump()
    result = await db["communityPost"].insert_one(post_dict)
    if result.inserted_id:
        return {"message": "Post Created Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create post")

@app.get("/posted-categories", response_model=list[postedCategory])
async def posted_categories():
    postedCategories = await db["postedCategory"].find().to_list(length=100)
    for category in postedCategories:
        category["id"] = str(category["_id"])
        del category["_id"]
        # Handle timestamp conversion
        if isinstance(category["timestamp"], int):  # If timestamp is an integer
            category["timestamp"] = datetime.fromtimestamp(category["timestamp"] / 1000).isoformat()
        elif isinstance(category["timestamp"], datetime):  # If timestamp is a datetime object
            category["timestamp"] = category["timestamp"].isoformat()
    return postedCategories



@app.post("/add-categoryPost")
async def post_category(category: postCategory):
    category_dict = category.model_dump()
    result = await db["postedCategory"].insert_one(category_dict)
    if result.inserted_id:
        return {"message": "Category Posted Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post category")



@app.delete("/delete-posted-category")
async def delete_posted_category(request: deleteCategory):
    try:
        print('Received ID:', request.id)
        # Convert the string id to ObjectId
        object_id = ObjectId(request.id)
        print('ObjectId:', object_id)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    result = await db["postedCategory"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "Category deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Category not found")
     

@app.post("/add-joke")
async def post_joke(joke: postJoke):
    category_dict = joke.model_dump()
    result = await db["postJoke"].insert_one(category_dict)
    if result.inserted_id:
        return {"message": "joke posted Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post jokes")

@app.get("/posted-jokes")
async def posted_jokes():
    postedJokes = await db["postJoke"].find().to_list(length=100)
    for joke in postedJokes:
        joke["id"] = str(joke["_id"])
        del joke["_id"]
        # Handle timestamp conversion
        if isinstance(joke["timestamp"], int):
            joke["timestamp"] = datetime.fromtimestamp(joke["timestamp"] / 1000).isoformat()
        elif isinstance(joke["timestamp"], datetime):
            joke["timestamp"] = joke["timestamp"].isoformat()
    return postedJokes

@app.delete("/delete-joke")
async def delete_joke(request: postJoke):
    try:
        print('Received ID:', request.id)
        # Convert the string id to ObjectId
        object_id = ObjectId(request.id)
        print('ObjectId:', object_id)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid joke ID format")

    result = await db["postJoke"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "joke deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="joke not found")



@app.get("/users")
async def get_users():
    users = await db["user"].find().to_list(length=100)
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