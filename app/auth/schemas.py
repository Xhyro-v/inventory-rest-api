from pydantic import BaseModel, EmailStr, Field, model_validator
from app.auth.enum import UserRole

class UserLogin(BaseModel):
        email : EmailStr
        password : str

class UserRegister(BaseModel):
        email: EmailStr
        role : UserRole
        password: str 
        confirm_password: str

class Token(BaseModel):
        acces_token : str
        token_type : str
