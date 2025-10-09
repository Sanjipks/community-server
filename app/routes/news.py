from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import NewsItem
from bson import ObjectId


router = APIRouter()

@router.get("/news")
async def get_communitynews():
    db = await get_database()
    communitynewses = await db["community-news"].find().to_list(length=100)
    for news in communitynewses:
        news["id"] = str(news["_id"])
        del news["_id"]
   
    return news

@router.post("/addnews")
async def add_news(news: NewsItem):
    db = await get_database()
    news_dict = news.model_dump
    result = await db["community-news"].insert_one(news_dict)
    if result.inserted_id:
        return {"message": "News added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add news") 
    
@router.delete("/delete-news")
async def delete_news(request: NewsItem):
    id = request.id
    db = await get_database()
    try:
        print('Received ID:',id)
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
    