from pydantic import BaseModel, EmailStr, model_validator
from typing import Literal, Optional, List
from bcrypt import hashpw, gensalt

from app.utilityFunctions.passwordRules import check_password

class user(BaseModel):
    firstName: str
    lastName: str
    email: str
    image: Optional[str] = None
    age: Optional[int] = None
    role: Literal["admin", "user", 'guest'] 

class createUser(BaseModel):  
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    confirmPassword: Optional[str] = None
    date_created: str

    @model_validator(mode="before")
    def validate_passwords(cls, values):
        password = values.get("password")
        confirm_password = values.get("confirmPassword")

        print("Validating passwords...")
        print(f"Password: {password}, Confirm Password: {confirm_password}, firstName: {values.get('firstName')}")
        # Ensure both password and confirmPassword are provided
        if not password or not confirm_password:
            raise ValueError("Both password and confirmPassword are required")
        
        check_password(password)

        # Ensure passwords match
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        

        # Hash the password using bcrypt
        hashed_password = hashpw(password.encode("utf-8"), gensalt())
        values["password"] = hashed_password.decode("utf-8")

        # Remove confirmPassword from the values (optional)
        values.pop("confirmPassword", None)

        return values


    class Config:
        # Exclude confirmPassword from being serialized (e.g., in responses)
        fields = {"confirmPassword": {"exclude": True}}

class VerifyAuthBody(BaseModel):
    authCodeRegister: str
    newUser: createUser  

#user login model
class LoginUser(BaseModel):
    useremail: EmailStr
    userpassword: str

class VerifyAuthCodeBody(BaseModel):
    useremail: str
    authcode: str

class ResetPasswordBody(BaseModel):
    useremail: EmailStr
    resetCode: str
    password: str
    confirmPassword: str
     
    def validate_passwords(cls, values):
        password = values.get("password")
        confirm_password = values.get("confirmPassword")

        print("Validating passwords...")
        print(f"Password: {password}, Confirm Password: {confirm_password}, firstName: {values.get('firstName')}")
        # Ensure both password and confirmPassword are provided
        if not password or not confirm_password:
            raise ValueError("Both password and confirmPassword are required")
        
        check_password(password)

        # Ensure passwords match
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        

        # Hash the password using bcrypt
        hashed_password = hashpw(password.encode("utf-8"), gensalt())
        values["password"] = hashed_password.decode("utf-8")

        # Remove confirmPassword from the values (optional)
        values.pop("confirmPassword", None)

        return values

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

#can be used for bulk delete witj ids in the body
class BulkDeleteBody(BaseModel):
    ids: List[str]

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

class chatlist(BaseModel):
    userId: str
    username: str
    userEmail: str
    profilePicture: str
    # lastMessage: Optional[str] = None
    # lastMessageTime: Optional[str] = None

class chatMessages(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: str


class VerifyAuthCodeRequest(BaseModel):
    useremail: EmailStr
    authcode: str

class  NewsItem (BaseModel): 
  id: int
  title: str
  description: str
  image: str
  author: str
  postedDate: str
  link: str

class postMessage(BaseModel):
    senderName: str
    senderEmail: str
    message: str

class ContactUSMessageBody(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    userId: Optional[str] = None