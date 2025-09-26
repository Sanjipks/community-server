from fastapi import APIRouter, HTTPException
from app.database import get_database
from datetime import datetime, timedelta, timezone
from app.utilityFunctions.sendEmail import send_authcode_via_email 
from app.models import ResetPasswordBody
import uuid     
router = APIRouter()



@router.post("/generate-password-reset-code")
async def generate_password_reset_code(useremail: str):
    db = await get_database()
    user = await db["users"].find_one({"email": useremail})
    
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    
    reset_code = str(uuid.uuid4())

    print(f"Generated password reset code: {reset_code}")

    await db["passwordResetCodes"].insert_one({
        "email": useremail,
        "resetCode": reset_code,
        "createdAt": datetime.now(timezone.utc)
    })
    try:
            send_authcode_via_email(useremail, reset_code)
            return {
                "status": "success",
                "message": "Please check your email for the password reset code, your code will expire in 10 minutes",
                "reset_code": reset_code 
            }
    except Exception as email_error:
            print(f"Warning: Failed to send email: {str(email_error)}")
            # Return reset code in response since email failed
            return {
                "status": "warning",
                "message": "Password reset code generated but email delivery failed. Please use the code from the response.",
                "reset_code": reset_code
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating password reset code: {str(e)}")
    

@router.post("/reset-password-with-code")
async def reset_password_with_code(payload: ResetPasswordBody):
    db = await get_database()

    # DB-side time check (avoids naive/aware datetime issues)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)

    # 1) Verify + consume the reset code atomically
    entry = await db["passwordResetCodes"].find_one_and_delete({
        "email": payload.useremail,
        "resetCode": payload.resetCode,
        "createdAt": {"$gt": cutoff},
    })
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset code")

    # 2) Update the user's password (already hashed by your validator)
    result = await db["users"].update_one(
        {"email": payload.useremail},
        {"$set": {"password": payload.password, "passwordUpdatedAt": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Password reset successful"}