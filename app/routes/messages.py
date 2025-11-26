from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import postMessage

router = APIRouter()

@router.post('/message')
async def post_message(message: postMessage):
    db = await get_database()
    message_dict = {"content": "Hello, World!"}
    result = await db["messages"].insert_one(message_dict)
    if result.inserted_id: 
        return {"message": "Message posted Successfully", "status": "success", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to post message")