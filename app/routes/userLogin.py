from app.database import get_database
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
from app.utilityFunctions.sendEmail import send_authcode_via_email 
from app.models import LoginUser
import uuid



router = APIRouter()

@router.post("/generate-authcode")
async def generate_authcode(body: LoginUser):
    try:
        db = await get_database()

        user = await db["users"].find_one({
            "email": body.useremail,
            "password": body.userpassword
        })
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # create auth code (valid for 10 minutes)
        authcode = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        record = {
            "email": body.useremail,
            "authCode": authcode,
            "createdAt": now,
            "expiresAt": now + timedelta(minutes=10),
            "used": False
        }

        inserted = await db["authCodesForLogin"].insert_one(record)
        if not inserted.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to store auth code")

        # try sending email, but still return a usable code if email fails
        try:
            send_authcode_via_email(body.useremail, authcode)  # assume sync; if async, await it
            return {
                "status": "success",
                "message": "Please check your email for the auth code. It expires in 10 minutes.",
            }
        except Exception as email_error:
            # log and still return the code so user can proceed
            # some codeswill be removed after successful login implementation
            print(f"Warning: Failed to send email: {email_error}")
            return {
                "status": "warning",
                "message": "Auth code generated but email delivery failed. Use the code shown here; it expires in 10 minutes.",
                "authcode": authcode
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth code: {e}")

    

@router.post("/verify-authcode")
async def verify_authcode(useremail: str, authcode: str):
    try:
        db = await get_database()

        # Check if the authcode matches
        authcode_entry = await db["authCodesForLogin"].find_one({"user": useremail, "authcode": authcode})
        if not authcode_entry:
            raise HTTPException(status_code=400, detail="Invalid authcode")

        # Check if the authcode has expired (10-minute limit)
        created_at = authcode_entry.get("createdAt")
        if not created_at or datetime.now(timezone.utc) > created_at + timedelta(minutes=10):
            raise HTTPException(status_code=400, detail="Authcode has expired")

        # Remove the authcode from the database (optional)
        await db["authCodesForLogin"].delete_one({"user": useremail, "authcode": authcode})

        # Finalize user login
     
        if authcode_entry:
            return {"message": "User logged in successfully", }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying authcode: {str(e)}")