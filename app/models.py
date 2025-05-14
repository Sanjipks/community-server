from pydantic import BaseModel
from typing import Literal, Optional

class user(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    role: Literal["admin", "user", 'guest'] 
    


class postCommunityPost(BaseModel):
    title: str
    content: str
    author: str
    date: str

class communityPosts(postCommunityPost):
    id: int
   

class postCommunityPost(BaseModel):
    title: str
    content: str
    author: str
    date: str



class postCategory(BaseModel):
    title: str
    category: str
    description: str
    author: str
    timestamp: str


class postedCategory(postCategory):
    id: str

class deleteCategory(postCategory):
    id: str
    

class postedJokes(BaseModel):
    id: str
    title: str
    content: str
    author: str
    timestamp: str

class postJoke(BaseModel):  
    title: str
    content: str  
    author: str
    timestamp: str
