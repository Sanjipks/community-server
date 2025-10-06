from app.database import get_database
from fastapi import APIRouter


router = APIRouter()

@router.get("/news")
async def get_communitynews():
    db = await get_database()
    communitynewses = await db["community-news"].find().to_list(length=100)
    for news in communitynewses:
        news["id"] = str(news["_id"])
        del news["_id"]
   
    return news