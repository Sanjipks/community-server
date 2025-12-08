from fastapi import APIRouter, HTTPException
from app.database import get_database
from datetime import datetime, timedelta, timezone
from app.models import createUser, VerifyAuthBody
from app.utilityFunctions.sendEmail import send_authcode_via_email
import secrets, string  # more appropriate than uuid for short auth codes


router = APIRouter()

# Helper to generate an 8-char, high-entropy code (A-Z, 0-9)
def gen_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

@router.post("/generate-authcode")
async def generate_authcode(user: createUser):
    db = await get_database()

    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    authcode = gen_code(8)  # e.g., 8-char code like "7X2K9PQA"
    now = datetime.now(timezone.utc)
    print('Generated authcode:', authcode)


    await db["authCodesForRegistration"].insert_one({
        "email": user.email,
        "authcode": authcode,
        "createdAt": now
    })

    try:
        send_authcode_via_email(user.email, authcode)
        return {
            "status": "success",
            "message": "Please check your email for the auth code. It expires in 10 minutes.",
        }
    except Exception as email_error:
        # Email failed; still return success with guidance
        return {
            "status": "warning",
            "message": "Auth code generated but email delivery failed. Please request a new code or contact support.",
            'error': email_error
        
        }
    
@router.post("/resend-authcode")
async def resend_authcode(user: createUser):       
    db = await get_database()

    authcode = gen_code(8)  # e.g., 8-char code like "7X2K9PQA"
    now = datetime.now(timezone.utc)

    await db["authCodesForRegistration"].insert_one({
        "email": user.email,
        "authcode": authcode,
        "createdAt": now
    })

    try:
        from app.utilityFunctions.sendEmail import send_authcode_via_email
        send_authcode_via_email(user.email, authcode)
        return {
            "status": "success",
            "message": "A new auth code has been sent to your email. It expires in 10 minutes.",
        }
    except Exception as email_error:
        # Email failed; still return success with guidance
        return {
            "status": "warning",
            "message": "Auth code generated but email delivery failed. Please request a new code or contact support.",
            "error": email_error
            
        }

@router.post("/verify-authcode")
async def verify_authcode(payload: VerifyAuthBody):
    db = await get_database()

    code = payload.authCodeRegister
    user = payload.newUser

    # cutoff time handled IN Mongo (no Python-side naive/aware comparison)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)

    # Atomically verify AND consume the code (race-safe)
    entry = await db["authCodesForRegistration"].find_one_and_delete({
        "email": user.email,
        "authcode": code,
        "createdAt": {"$gt": cutoff},
    })

    if not entry:
        # distinguish between "expired" and "invalid"
        exists = await db["authCodesForRegistration"].find_one({
            "email": user.email,
            "authcode": code
        })
        if exists:
            # optionally delete expired code to keep the collection clean
            await db["authCodesForRegistration"].delete_one({"_id": exists["_id"]})
            raise HTTPException(status_code=400, detail="Auth code has expired")
        raise HTTPException(status_code=400, detail="Invalid auth code")

    # create the user (you may also want a unique index on users.email)
    result = await db["users"].insert_one(user.model_dump())
    if not result.inserted_id:
        # extremely rare; re-throw as server error
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User created successfully", "id": str(result.inserted_id), "status": "success"}
