from fastapi import Depends, HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from app.database import get_database
from datetime import datetime, timezone
import jwt
from jwt import InvalidTokenError

SECRET = "SECRET"
ALGO = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGO)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db = await get_database()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def require_admin(user = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
