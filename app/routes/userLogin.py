from app.database import get_database
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
from app.utilityFunctions.sendEmail import send_authcode_via_email
from app.models import userSignIn, user   
import uuid

router = APIRouter()
@router.get("/generate-authcode")
async def login_user(useremail: str, userpassword: str):
    db = await get_database()
    user = await db["users"].find_one({"email": useremail, "password": userpassword})
    
    if user:
        authcode = str(uuid.uuid4())
        print(f"Generated authCode: {authcode}")

        await db["authCodes"].insert_one({
            "email": useremail,
            "authcode": authcode,
            "createdAt": datetime.now(timezone.utc)
        })
    try:
            send_authcode_via_email(useremail, authcode)
            return {
                "status": "success",
                "message": "Please check your email for the authcode, your authcode will expire in 10 minutes",
                "authcode": authcode 
            }
    except Exception as email_error:
            print(f"Warning: Failed to send email: {str(email_error)}")
            # Return authcode in response since email failed
            return {
                "status": "warning",
                "message": "Auth code generated but email delivery failed. Please use the code from the response.",
                "authcode": authcode
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating authcode: {str(e)}")
    

@router.post("/verify-authcode")
async def verify_authcode(useremail: str, authcode: str):
    try:
        db = await get_database()

        # Check if the authcode matches
        authcode_entry = await db["authCodes"].find_one({"user": useremail, "authcode": authcode})
        if not authcode_entry:
            raise HTTPException(status_code=400, detail="Invalid authcode")

        # Check if the authcode has expired (10-minute limit)
        created_at = authcode_entry.get("createdAt")
        if not created_at or datetime.now(timezone.utc) > created_at + timedelta(minutes=10):
            raise HTTPException(status_code=400, detail="Authcode has expired")

        # Remove the authcode from the database (optional)
        await db["authCodes"].delete_one({"user": useremail, "authcode": authcode})

        # Finalize user login
     
        if authcode_entry:
            return {"message": "User logged in successfully", }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying authcode: {str(e)}")