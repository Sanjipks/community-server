from datetime import datetime, timezone
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pathlib import Path
from app.database import get_database
from app.models import BulkDeleteBody
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

# Configure where files live on disk and how they are publicly served
UPLOAD_ROOT = Path(os.getenv("UPLOAD_ROOT", "uploads")).resolve()
BACKEND_URL = os.getenv("BACKEND_URL")  # used to build public URLs

# Make sure folder exists
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


@router.get("/allnews")
async def get_communitynews():
    db = await get_database()
    items = await db["community-news"].find().to_list(length=100)
    for news in items:
        news["id"] = str(news["_id"])
        del news["_id"]
    return items


@router.post("/addnews")
async def add_news(
    title: str = Form(...),
    description: str = Form(...),
    author: str = Form(...),
    image: UploadFile = File(...),
):
    db = await get_database()

    # 1) Create Mongo doc without image first
    news_doc = {
        "title": title,
        "description": description,
        "author": author,
        "image": None,  # set later
        "postedDate": datetime.now(timezone.utc).isoformat(),
    }
    insert_result = await db["community-news"].insert_one(news_doc)
    if not insert_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create news entry")

    news_id = str(insert_result.inserted_id)

    # 2) Prepare per-doc folder + filename
    per_doc_dir = (UPLOAD_ROOT / news_id)
    per_doc_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(image.filename).suffix.lower() or ".jpg"
    # (Optional) whitelist extensions:
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".jpg"

    file_path = per_doc_dir / f"{news_id}{ext}"            # absolute path on disk
    # Build a URL based on how you mounted static files in main.py: app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT))
    rel_path = file_path.relative_to(UPLOAD_ROOT).as_posix()  # e.g. "68fc.../68fc....jpg"
    image_url = f"{BACKEND_URL}/uploads/{rel_path}"

    # 3) Save the file
    try:
        contents = await image.read()  # read once
        with file_path.open("wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        # Roll back the Mongo insert if file write fails
        await db["community-news"].delete_one({"_id": ObjectId(news_id)})
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    # 4) Update Mongo with the public image URL
    await db["community-news"].update_one(
        {"_id": ObjectId(news_id)},
        {"$set": {"image": image_url}},
    )

    return {"message": "News added successfully", "id": news_id, "image": image_url}


@router.delete("/allnews/{id}")
async def delete_news(id: str):
    db = await get_database()
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid news ID format")

    result = await db["community-news"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "News deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="News not found")


@router.post("/allnews/delete-multiple-news")
async def bulk_delete_news(body: BulkDeleteBody):
    db = await get_database()
    object_ids = []
    for _id in body.ids:
        try:
            object_ids.append(ObjectId(_id))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid news ID format: {_id}")

    result = await db["community-news"].delete_many({"_id": {"$in": object_ids}})
    if result.deleted_count > 0:
        return {"message": f"Deleted {result.deleted_count} news items successfully"}
    else:
        raise HTTPException(status_code=404, detail="No news items found to delete")
