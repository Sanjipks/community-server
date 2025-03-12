from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class communityPost(BaseModel):
    id: int
    title: str
    content: str
    author: str
    date: str


class postedCategory(BaseModel):
    id: int
    title: str
    category: str
    content: str
    descritpion: str
    author: str
    timestamp: str

class postedJokes(BaseModel):
    id: int
    joke: str
    author: str
    timestamp: str


