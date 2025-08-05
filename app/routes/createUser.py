from fastapi import APIRouter, HTTPException
from app.database import get_database
from datetime import datetime, timedelta, timezone
from app.models import createUser
import uuid
from app.utilityFunctions.sendEmail import send_authcode_via_email

router = APIRouter()


@router.post("/generate-authcode")
async def generate_authcode(user: createUser):
    try:
        db = await get_database()

        existing_user = await db["users"].find_one({"email": user.email})
        if existing_user:
          raise HTTPException(status_code=400, detail="User with this email already exists")   


        authcode = str(uuid.uuid4())
        print(f"Generated authCode: {authcode}")

       
        await db["authCodes"].insert_one({
            "email": user.email,
            "authcode": authcode,
            "createdAt": datetime.utcnow()  # Store the current UTC timestamp
        })

        # Send the authcode to the user (e.g., via email or SMS)
    #    send_authcode_via_email(user.email, authcode)

        return {"message": "Please check your email for the authcode, your authcode will expire in 10 minutes " }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating authcode: {str(e)}")
    

@router.post("/verify-authcode")
async def verify_authcode(user: createUser, email: str, authcode: str):
    try:
        db = await get_database()

        # Check if the authcode matches
        authcode_entry = await db["authCodes"].find_one({"email": email, "authcode": authcode})
        if not authcode_entry:
            raise HTTPException(status_code=400, detail="Invalid authcode")

        # Check if the authcode has expired (10-minute limit)
        created_at = authcode_entry.get("createdAt")
        if not created_at or datetime.now(timezone.utc) > created_at + timedelta(minutes=10):
            raise HTTPException(status_code=400, detail="Authcode has expired")

        # Remove the authcode from the database (optional)
        await db["authCodes"].delete_one({"email": email, "authcode": authcode})

        # Finalize user creation
        user_dict = user.model_dump()
        result = await db["users"].insert_one(user_dict)
        if result.inserted_id:
            return {"message": "User created successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying authcode: {str(e)}")