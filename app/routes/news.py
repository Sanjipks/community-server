from datetime import datetime
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pathlib import Path
from app.database import get_database
from app.models import BulkDeleteBody
from bson import ObjectId


router = APIRouter()

@router.get("/allnews")
async def get_communitynews():
    db = await get_database()
    communitynewses = await db["community-news"].find().to_list(length=100)
    for news in communitynewses:
        news["id"] = str(news["_id"])
        del news["_id"]
   
    return news

@router.post("/addnews")
async def add_news(
    title: str = Form(...),
    description: str = Form(...),
    author: str = Form(...),
    image: UploadFile = File(...)
):
    db = await get_database()

    # Save the uploaded file to a local folder
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / image.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    # Prepare data for MongoDB
    news_dict = {
        "title": title,
        "description": description,
        "author": author,
        "image": str(file_path),
        "postedDate": datetime.now().isoformat()   
    }

    result = await db["community-news"].insert_one(news_dict)

    if result.inserted_id:
        return {"message": "News added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add news")
    
@router.delete("/allnews/{id}")
async def delete_news(id: str):
    db = await get_database()
    try:
        print('Received ID:', id)
        object_id = ObjectId(id)
        print('ObjectId:', object_id)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid news ID format")

    result = await db["community-news"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "News deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="News not found")
    
#to delete multiple news items by their IDs
@router.post("/allnews/delete-multiple-news")
async def bulk_delete_news(body: BulkDeleteBody):
    ids = body.ids
    db = await get_database()
    object_ids = []
    for id in ids:
        try:
            object_id = ObjectId(id)
            object_ids.append(object_id)
        except Exception as e:
            print(f"Error converting ID {id} to ObjectId: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid news ID format: {id}")

    result = await db["community-news"].delete_many({"_id": {"$in": object_ids}})
    if result.deleted_count > 0:
        return {"message": f"Deleted {result.deleted_count} news items successfully"}
    else:
        raise HTTPException(status_code=404, detail="No news items found to delete")