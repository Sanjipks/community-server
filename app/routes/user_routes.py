# from app.database import get_database
# from fastapi import APIRouter


# router = APIRouter()

# router.post("/loginUser")
# async def find_user(useremail, userpassword):
#     db = await get_database()
#     user = await db["users"].find_one({"email": useremail, "password": userpassword})
    
#     if user:
#         user["id"] = str(user["_id"])
#         del user["_id"]
#         return {"message": "User logged in successfully", "user": user}
#     else:
#         return {"message": "Invalid email or password"}

