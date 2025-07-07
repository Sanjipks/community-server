from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import createUser
from bson import ObjectId
import uuid
from app.utilityFunctions.sendEmail import send_authcode_via_email

router = APIRouter()

  # For generating unique authcodes

@router.post("/generate-authcode")
async def generate_authcode(email: str):
    try:
        db = await get_database()

        # Check if the user already exists
        existing_user = await db["users"].find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Generate a unique authcode
        authcode = str(uuid.uuid4())

        # Save the authcode and email in the database
        await db["authcodes"].insert_one({"email": email, "authcode": authcode})

        # Send the authcode to the user (e.g., via email or SMS)
        send_authcode_via_email(email, authcode)


        return {"message": "Authcode generated and sent to user"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating authcode: {str(e)}")
    

@router.post("/verify-authcode")
async def verify_authcode(email: str, authcode: str, user: createUser):
    try:
        db = await get_database()

        # Check if the authcode matches
        authcode_entry = await db["authcodes"].find_one({"email": email, "authcode": authcode})
        if not authcode_entry:
            raise HTTPException(status_code=400, detail="Invalid authcode")

        # Remove the authcode from the database (optional)
        await db["authcodes"].delete_one({"email": email, "authcode": authcode})

        # Finalize user creation
        user_dict = user.model_dump()
        result = await db["users"].insert_one(user_dict)
        if result.inserted_id:
            return {"message": "User created successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying authcode: {str(e)}")