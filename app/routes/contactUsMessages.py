from fastapi import APIRouter, HTTPException
from app.database import get_database
from datetime import datetime, timezone
from app.models import postMessage
from bson import ObjectId

router = APIRouter()

@router.post('/send-message')
async def post_message(message: postMessage):
    db = await get_database()
    now = datetime.now(timezone.utc)
    message_dict = {
        'sender': message.senderName,
        'senderEmail': message.senderEmail,
        'message': message.message,
        'createdAt': now
    }
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

@router.delete('/messages/{id}')
async def delete_message(id: str):
    db = await get_database()  
    try:
        object_id = ObjectId(id)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid message ID format")

    result = await db["messages"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "Message deleted successfully", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Message not found")