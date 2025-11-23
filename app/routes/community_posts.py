from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postCommunityPost

router = APIRouter()

@router.get("/community-posts/start={start}&end={end}")
async def get_community_posts(start: int, end: int):
    print('Fetching community posts from', start, 'to', end)
    # will work for pagination
    try:
        db = await get_database()
        limit = end - start
        print ('limit:', limit)
        total_posts = await db["communityPost"].count_documents({})
        posts = await db["communityPost"].find().skip(start).limit(limit).to_list(length=limit)

        for post in posts:
            post["id"] = str(post["_id"])
            del post["_id"]

        return {"selectedPosts": posts, "totalPosts": total_posts} if posts else {"message": "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

@router.post("/post-community-post")
async def post_community_post(post: postCommunityPost):
    try:
        db = await get_database()
        post_dict = post.model_dump()
        result = await db["communityPost"].insert_one(post_dict)
        if result.inserted_id:
            return {"message": "Post Created Successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create post")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")
    

@router.delete("/delete-community-post")
async def delete_posted_category(request: postCommunityPost):
    try:
        db = await get_database()
        object_id = ObjectId(request.id)  # Convert the string id to ObjectId
        result = await db["communityPost"].delete_one({"_id": object_id})
        if result.deleted_count == 1:
            return {"message": "Category deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting category: {str(e)}")