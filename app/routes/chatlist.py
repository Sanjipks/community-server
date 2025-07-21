from bson import ObjectId
from app.database import get_database
from fastapi import APIRouter, HTTPException

from app.models import postCommunityPost, user


router = APIRouter()

@router.post("/adduser") 
async def add_user(user: postCommunityPost):
    db = await get_database()
    user_dict = user.model_dump()
    result = await db["user"].insert_one(user_dict)
    if result.inserted_id:
        return {"message": "User added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add user")

    
@router.get("/users")
async def get_users_list():
    db = await get_database()
    users = await db["chatlist"].find().to_list(length=100)
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users



@router.delete("/removeuser") 
async def remove_user(request: user):
    db = await get_database()
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