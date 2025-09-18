# from fastapi import APIRouter, HTTPException
# from app.database import get_database
# from datetime import datetime, timedelta, timezone
# from app.models import createUser, VerifyAuthBody
# import uuid
# from app.utilityFunctions.sendEmail import send_authcode_via_email

# router = APIRouter()

# @router.post("/generate-authcode")
# async def generate_authcode(user: createUser):
#     try:
#         db = await get_database()

#         existing_user = await db["users"].find_one({"email": user.email})
#         if existing_user:
#             raise HTTPException(status_code=400, detail="User with this email already exists")   

#         authcode = str(uuid.uuid4().hex[:8])
#         print(f"Generated authCode: {authcode}")
       
#         await db["authCodesForRegistration"].insert_one({
#             "email": user.email,
#             "authcode": authcode,
#             "createdAt": datetime.now(timezone.utc)
#         })

        
#         try:
#             send_authcode_via_email(user.email, authcode)
#             return {
#                 "status": "success",
#                 "message": "Please check your email for the authcode, your authcode will expire in 10 minutes",
#             }
#         except Exception as email_error:
#             print(f"Warning: Failed to send email: {str(email_error)}")
#             # Return authcode in response since email failed
#             return {
#                 "status": "warning",
#                 "message": "Auth code generated but email delivery failed. Please use the code from the response.",
                
#             }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating authcode: {str(e)}")
    

# @router.post("/verify-authcode")
# async def verify_authcode(payload: VerifyAuthBody):
#     code = payload.authCodeRegister
#     user = payload.newUser
#     print(f"Verifying authcode for user: {user.email} with code: {code}")
    
#     try:
#         db = await get_database()
#         # Check if the authcode matches
#         authcode_entry = await db["authCodesForRegistration"].find_one({"email": user.email, "authcode": code})
#         if not authcode_entry:
#             raise HTTPException(status_code=400, detail="Invalid authcode")

#         # Check if the authcode has expired (10-minute limit)
#         created_at = authcode_entry.get("createdAt")
#         if not created_at or datetime.now(timezone.utc) > created_at + timedelta(minutes=10):
#             raise HTTPException(status_code=400, detail="Authcode has expired")

#         # Remove the authcode from the database (optional)
#         await db["authCodesForRegistration"].delete_one({"email": user.email, "authcode": code})

#         # Finalize user creation
#         user_dict = user.model_dump()
       
#         result = await db["users"].insert_one(user_dict)
#         if result.inserted_id:
#             return {"message": "User created successfully", "id": str(result.inserted_id)}
#         else:
#             raise HTTPException(status_code=500, detail="Failed to create user")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error verifying authcode: {str(e)}")

from fastapi import APIRouter, HTTPException
from app.database import get_database
from datetime import datetime, timedelta, timezone
from app.models import createUser, VerifyAuthBody
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
            "message": "Please check your email for the auth code. It expires in 10 minutes.",
        }
    except Exception as email_error:
        # Email failed; still return success with guidance (avoid leaking the code unless you intend to)
        # If you DO want to return the code on failure, uncomment the next line
        # "authcode": authcode,
        return {
            "status": "warning",
            "message": "Auth code generated but email delivery failed. Please request a new code or contact support.",
        }

@router.post("/verify-authcode")
async def verify_authcode(payload: VerifyAuthBody):
    db = await get_database()

    code = payload.authCodeRegister
    user = payload.newUser

    # Cutoff time handled IN Mongo (no Python-side naive/aware comparison)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)

    # Atomically verify AND consume the code (race-safe)
    entry = await db["authCodesForRegistration"].find_one_and_delete({
        "email": user.email,
        "authcode": code,
        "createdAt": {"$gt": cutoff},
    })

    if not entry:
        # Distinguish between "expired" and "invalid"
        exists = await db["authCodesForRegistration"].find_one({
            "email": user.email,
            "authcode": code
        })
        if exists:
            # Optionally delete expired code to keep the collection clean
            await db["authCodesForRegistration"].delete_one({"_id": exists["_id"]})
            raise HTTPException(status_code=400, detail="Auth code has expired")
        raise HTTPException(status_code=400, detail="Invalid auth code")

    # Create the user (you may also want a unique index on users.email)
    result = await db["users"].insert_one(user.model_dump())
    if not result.inserted_id:
        # Extremely rare; re-throw as server error
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User created successfully", "id": str(result.inserted_id)}
