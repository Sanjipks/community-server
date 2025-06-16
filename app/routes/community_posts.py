from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postCommunityPost

router = APIRouter()

@router.get("/community-posts")
async def get_community_posts():
    db = await get_database()
    posts = await db["communityPost"].find().to_list(length=100)
    for post in posts:
        post["id"] = str(post["_id"])
        del post["_id"]
    return posts

@router.post("/post-community-post")
async def post_community_post(post: postCommunityPost):
    db = await get_database()
    post_dict = post.model_dump()
    result = await db["communityPost"].insert_one(post_dict)
    if result.inserted_id:
        return {"message": "Post Created Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create post")