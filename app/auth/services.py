from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException, status

from app.auth.models import User as UserModel
from app.auth.schemas import UserRegister, UserLogin
from app.auth.repositories import get_by_email
from app.dependencies.auth import pwd_context
from app.core.security import create_access_token

############################################################################################################


def register_user(db: Session, data: UserRegister) -> dict:
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirm password do not match.",
        )

    password_hash = pwd_context.hash(data.password)

    new_user = UserModel(
        email=data.email,
        role=data.role,
        password_hash=password_hash, 
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    return {
        "message": "Successfully registered",
        "email": new_user.email,
    }

def authenticate_user(db: Session, email: str, password: str) -> UserModel | None:
    user = get_by_email(db, email)
    if not user:
        return None
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user


def login_user(db: Session, data: UserLogin) -> dict:
    user = authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}