from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import createUser
from bson import ObjectId

router = APIRouter()

@router.post("/create-user")
async def create_user(user: createUser):
    print("Received user data:", user)
    try:
       
        # if user.password != user.confirmPassword:
        #     raise HTTPException(status_code=400, detail="Passwords do not match")
        
        db = await get_database()
        user_dict = user.model_dump()
        

        existing_user = await db["users"].find_one({"email": user_dict["email"]})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
     
        result = await db["users"].insert_one(user_dict)
        if result.inserted_id:
            return {"message": "User created successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")