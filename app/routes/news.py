from datetime import datetime, timezone
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pathlib import Path
from app.database import get_database
from app.models import BulkDeleteBody
from bson import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()

IMAGE_UPLOADPATH = os.getenv("COMMUNITY_UPLOADPATH")


router = APIRouter()

@router.get("/allnews")
async def get_communitynews():
    db = await get_database()
    communitynewses = await db["community-news"].find().to_list(length=100)
    for news in communitynewses:
        news["id"] = str(news["_id"])
        del news["_id"]
   
    return communitynewses


@router.post("/addnews")
async def add_news(
    title: str = Form(...),
    description: str = Form(...),
    author: str = Form(...),
    image: UploadFile = File(...)
):
    db = await get_database()

    #create a placeholder document in MongoDB (no image yet)
    news_dict = {
        "title": title,
        "description": description,
        "author": author,
        "image": None,  # temporarily empty
        "postedDate": datetime.now(timezone.utc).isoformat()
    }

    insert_result = await db["community-news"].insert_one(news_dict)

    if not insert_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create news entry")

    news_id = str(insert_result.inserted_id)

    # build a unique image path tied to this ID
    upload_dir = Path(IMAGE_UPLOADPATH) / news_id  # optional per-document folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # You can just use the original extension, but rename to the id
    ext = Path(image.filename).suffix or ".jpg"
    file_path = upload_dir / f"{news_id}{ext}"

    # save image to that path
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
    except Exception as e:
        # rollback: delete the Mongo entry if image write fails
        await db["community-news"].delete_one({"_id": ObjectId(news_id)})
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    #update the document with the final image path
    await db["community-news"].update_one(
        {"_id": ObjectId(news_id)},
        {"$set": {"image": str(file_path)}}
    )

    return {
        "message": "News added successfully",
        "id": news_id,
        "image": str(file_path)
    }

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