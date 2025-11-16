from fastapi import Depends, HTTPException
from app.utilityFunctions.security import get_current_user

async def require_admin(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admins only")
    return user
