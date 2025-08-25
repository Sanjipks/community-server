from app.database import get_database
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.models import userSignIn, user   


router = APIRouter()
@router.get("/login")
async def login_user(useremail: str, userpassword: str):
    db = await get_database()
    user = await db["users"].find_one({"email": useremail, "password": userpassword})
    
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        return {"message": "User logged in successfully", "user": user}
    else:
        return {"message": "Invalid email or password"}
   