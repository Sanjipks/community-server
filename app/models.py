from pydantic import BaseModel, EmailStr, validator
from typing import Literal, Optional
from bcrypt import hashpw, gensalt

class user(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    role: Literal["admin", "user", 'guest'] 

class createUser(BaseModel):  
    email: EmailStr
    password: str
    confirmPassword: str
    date_created: str

    @validator("password", pre=True)
    def hash_password(cls, password: str, values):
        # Ensure passwords match before hashing
        confirm_password = values.get("confirmPassword")
        if confirm_password and password != confirm_password:
            raise ValueError("Passwords do not match")
        # Hash the password using bcrypt
        hashed_password = hashpw(password.encode("utf-8"), gensalt())
        return hashed_password.decode("utf-8")
    
    class Config:
        # Exclude confirmPassword from being serialized (e.g., in responses)
        fields = {"confirmPassword": {"exclude": True}}
    
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



