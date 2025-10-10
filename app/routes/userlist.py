from app.database import get_database
from fastapi import APIRouter


router = APIRouter()

@router.get("/list")
async def get_users():
    db = await get_database()
    users = await db["users"].find().to_list(length=100)
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
   
    return users

@router.delete("/delete-user")
async def delete_user(useremail: str):
    db = await get_database()
    result = await db["users"].delete_one({"email": useremail})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}     