import jwt
from typing import Optional
from pwdlib import PasswordHash
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.auth.enum import UserRole
from app.auth.models import User as UserModel
from app.core.config import ALGORITHM, ACCESS_TOKEN, SECRET_KEY
from app.auth.schemas import UserRegister, UserLogin
from app.auth.repositories import get_by_email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Inisialisasi PasswordHash diubah menjadi dengan Argon2
pwd_context = PasswordHash((Argon2Hasher(),))

############################################################################################################
def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
                to_encode,
                SECRET_KEY,
                algorithm=ALGORITHM
            )


def verify_access_token(token : str):
        try:
            payload = jwt.decode(
                 token,
                 SECRET_KEY,
                 algorithms=ALGORITHM
            )
            return payload
        
        except InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
             

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)
    if not payload:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if not email:
        raise credentials_exception

    user = get_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserModel = Depends(get_current_user)) -> UserModel:
        user_role = getattr(user, "role", None)
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access rejected: Insufficient permissions",
            )
        return user

# Shortcut for router to get easier to call
allow_admin_only = RoleChecker([UserRole.ADMIN])
allow_staff_and_admin = RoleChecker([UserRole.ADMIN, UserRole.STAFF])


############################################################################################################


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