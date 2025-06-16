from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models import postCategory, deleteCategory

router = APIRouter()

@router.get("/posted-categories")
async def posted_categories():
    db = await get_database()
    postedCategories = await db["postedCategory"].find().to_list(length=100)
    for category in postedCategories:
        category["id"] = str(category["_id"])
        del category["_id"]
    return postedCategories

@router.post("/add-categoryPost")
async def post_category(category: postCategory):
    db = await get_database()
    category_dict = category.model_dump()
    result = await db["postedCategory"].insert_one(category_dict)
    if result.inserted_id:
        return {"message": "Category Posted Successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to post category")

@router.delete("/delete-posted-category")
async def delete_posted_category(request: deleteCategory):
    db = await get_database()
    try:
        object_id = ObjectId(request.id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    result = await db["postedCategory"].delete_one({"_id": object_id})
    if result.deleted_count == 1:
        return {"message": "Category deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Category not found")