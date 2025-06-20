from datetime import datetime
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postCategory, deleteCategory, postedCategory

router = APIRouter()

@router.get("/posted-categories", response_model=list[postedCategory])
async def posted_categories():
    try:
        db = await get_database()
        postedCategories = await db["postedCategory"].find().to_list(length=100)
      
        for category in postedCategories:
            category["id"] = str(category["_id"])
            del category["_id"]
            # Handle timestamp conversion
            if "timestamp" in category:
                if isinstance(category["timestamp"], int):  # If timestamp is an integer
                    category["timestamp"] = datetime.fromtimestamp(category["timestamp"] / 1000).isoformat()
                elif isinstance(category["timestamp"], datetime):  # If timestamp is a datetime object
                    category["timestamp"] = category["timestamp"].isoformat()
        return postedCategories if postedCategories else {"message": "No categories found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.post("/add-categoryPost")
async def post_category(category: postCategory):
    try:
        db = await get_database()
        category_dict = category.model_dump()
        result = await db["postedCategory"].insert_one(category_dict)
        if result.inserted_id:
            return {"message": "Category Posted Successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to post category")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error posting category: {str(e)}")

@router.delete("/delete-posted-category")
async def delete_posted_category(request: deleteCategory):
    try:
        db = await get_database()
        object_id = ObjectId(request.id)  # Convert the string id to ObjectId
        result = await db["postedCategory"].delete_one({"_id": object_id})
        if result.deleted_count == 1:
            return {"message": "Category deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting category: {str(e)}")