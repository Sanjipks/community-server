from pydantic import BaseModel
from typing import Literal, Optional

class user(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    role: Literal["admin", "user", 'guest'] 
    


class communityPost(BaseModel):
    id: int
    title: str
    content: str
    author: str
    date: str


class postedCategory(BaseModel):
    id: str
    title: str
    category: str
    description: str
    author: str
    timestamp: str


class postCategory(BaseModel):
    title: str
    category: str
    description: str
    author: str
    timestamp: str

class postedJokes(BaseModel):
    id: int
    joke: str
    author: str
    timestamp: str


