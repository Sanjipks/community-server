
from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import NewsItem


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