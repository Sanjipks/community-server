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
    
@router.get('/messages')
async def get_messages():
    db = await get_database()
    messages = await db["messages"].find().to_list(length=100)
    for msg in messages:
        msg["id"] = str(msg["_id"])
        del msg["_id"]
    return messages 