from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from app.database import get_database

router = APIRouter()

class ContactMessageBody(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    userId: str | None = None  

@router.post("/contact-us-message")
async def create_contact_message(contactMessage: ContactMessageBody):
    db = await get_database()
    now = datetime.now(timezone.utc)

    doc = {
        "name": contactMessage.name,
        "email": contactMessage.email,
        "subject": contactMessage.subject,
        "message": contactMessage.message,
        "userId": contactMessage.userId,
        "status": "new",
        "createdAt": now,
        "updatedAt": now,
        "assignedTo": None,
    }

    result = await db["contactMessages"].insert_one(doc)
    
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create news entry")
    del doc["_id"]
    return {"message": "Message sent successfully"}

@router.get("/contact-us-messages")
async def get_contact_messages():   
    db = await get_database()
    messages = await db["contactMessages"].find().to_list(length=100)
    for msg in messages:
        msg["id"] = str(msg["_id"])
        del msg["_id"]
        if isinstance(msg["createdAt"], datetime):
            msg["createdAt"] = msg["createdAt"].isoformat()
        if isinstance(msg["updatedAt"], datetime):
            msg["updatedAt"] = msg["updatedAt"].isoformat()
    return messages
