from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import LoginUser, VerifyAuthCodeBody
from app.utilityFunctions.sendEmail import send_authcode_via_email
from app.utilityFunctions.security import create_access_token
import uuid

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
            "used": False,
        }

        inserted = await db["authCodesForLogin"].insert_one(record)
        if not inserted.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to store auth code")

        try:
            send_authcode_via_email(body.useremail, authcode)
            return {
                "status": "success",
                "message": "Please check your email for the auth code. It expires in 10 minutes.",
            }
        except Exception as email_error:
            print(f"Warning: Failed to send email: {email_error}")
            return {
                "status": "warning",
                "message": "Auth code generated but email delivery failed. Use the code shown here; it expires in 10 minutes.",
                "authcode": authcode,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth code: {e}")

@router.post("/verify-authcode")
async def verify_authcode(body: VerifyAuthCodeBody):
    try:
        db = await get_database()

        # match the same field names you used in insert
        authcode_entry = await db["authCodesForLogin"].find_one({
            "email": body.useremail,
            "authCode": body.authcode,
            "used": False,
        })

        if not authcode_entry:
            raise HTTPException(status_code=400, detail="Invalid auth code")

        # check expiration (use expiresAt if present)
        expires_at = authcode_entry.get("expiresAt")
        if not expires_at or datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="Auth code has expired")

        # mark authcode as used (so it can't be reused)
        await db["authCodesForLogin"].update_one(
            {"_id": authcode_entry["_id"]},
            {"$set": {"used": True, "usedAt": datetime.now(timezone.utc)}},
        )

        # load user
        user = await db["users"].find_one({"email": body.useremail})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # create JWT token for this user
        access_token = create_access_token(
            data={"sub": str(user["_id"])},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "message": "User logged in successfully",
            "access_token": access_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying auth code: {str(e)}")