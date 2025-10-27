from datetime import datetime
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postJoke

router = APIRouter()


    
@router.post("/add-joke")
async def post_joke(joke: postJoke):
    db = await get_database()
    category_dict = joke.model_dump()
    result = await db["postJoke"].insert_one(category_dict)
    if result.inserted_id:
        return {"message": "joke posted Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post jokes")

@router.get("/posted-jokes")
async def posted_jokes():
    db = await get_database()
    postedJokes = await db["postJoke"].find().to_list(length=100)
    for joke in postedJokes:
        joke["id"] = str(joke["_id"])
        del joke["_id"]
        # Handle timestamp conversion
        if isinstance(joke["timestamp"], int):
            joke["timestamp"] = datetime.fromtimestamp(joke["timestamp"] / 1000).isoformat()
        elif isinstance(joke["timestamp"], datetime):
            joke["timestamp"] = joke["timestamp"].isoformat()
    return postedJokes

@router.delete("/posted-jokes/{id}")
async def delete_joke(id:str):
    jokeId = id
    db = await get_database()
    print('ObjectId:', jokeId)
    try:
        object_id = ObjectId(jokeId)
        print('ObjectId:', jokeId)
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=400, detail="Invalid joke ID format")

    result = await db["postJoke"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "joke deleted successfully", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="joke not found")
