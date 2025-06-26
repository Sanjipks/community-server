from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class user(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    role: Literal["admin", "user", 'guest'] 

class createUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    
class addUser(user):
    password: str
    confirm_password: str

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

class CommunityNews(BaseModel):
    id: str
    title: str
    descreption: str
    image: str
    link: str

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

class chatMessages(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: str



