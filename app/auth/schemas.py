from pydantic import BaseModel, EmailStr, Field, model_validator
from app.auth.enum import UserRole

class UserLogin(BaseModel):
        email : EmailStr
        password : str

class UserRegister(BaseModel):
    email: EmailStr
    role : UserRole
    password: str = Field(..., min_length=8, max_length=20)
    confirm_password: str

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match")
        return self

class Token(BaseModel):
        acces_token : str
        token_type : str
