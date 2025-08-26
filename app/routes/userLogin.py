from app.database import get_database
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
from app.utilityFunctions.sendEmail import send_authcode_via_email
from app.models import userSignIn, user   
import uuid

router = APIRouter()
@router.get("/login")
async def login_user(useremail: str, userpassword: str):
    db = await get_database()
    user = await db["users"].find_one({"email": useremail, "password": userpassword})
    
    if user:
        authcode = str(uuid.uuid4())
        print(f"Generated authCode: {authcode}")

        await db["authCodes"].insert_one({
            "email": user.email,
            "authcode": authcode,
            "createdAt": datetime.now(timezone.utc)
        })
    try:
            send_authcode_via_email(user.email, authcode)
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