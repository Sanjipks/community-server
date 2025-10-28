from datetime import datetime
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postCategory, deleteCategory, postedCategory, BulkDeleteBody

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

@router.delete("/delete-posted-category?{id}")
async def delete_posted_category(id: str):
    try:
        db = await get_database()
        object_id = ObjectId(id)  # Convert the string id to ObjectId
        result = await db["postedCategory"].delete_one({"_id": object_id})
        if result.deleted_count == 1:
            return {"message": "Category deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting category: {str(e)}")
    
@router.post("/delete-multiple-categories")
async def bulk_delete_categories(request: BulkDeleteBody):
    ids = request.ids
    db = await get_database()
    object_ids = []
    if not isinstance(ids, list) or not all(isinstance(id, str) for id in ids):
        raise HTTPException(status_code=400, detail="Invalid IDs format. Expected a list of strings.")
    for id in ids:
        try:
            object_id = ObjectId(id)
            object_ids.append(object_id)
        except Exception as e:
            print(f"Error converting ID {id} to ObjectId: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid category ID format: {id}")

    result = await db["postedCategory"].delete_many({"_id": {"$in": object_ids}})
    if result.deleted_count > 0:
        return {"message": f"Deleted {result.deleted_count} categories successfully"}
    else:
        raise HTTPException(status_code=404, detail="No categories found to delete")