from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.orm import Session
from pwdlib import PasswordHash


from app.db.session import get_db
from app.core.security import verify_access_token, create_access_token
from app.auth.repositories import get_by_email
from app.auth.models import User as UserModel
from app.auth.enum import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

#Inisialisasi PasswordHash diubah menjadi dengan Argon2
pwd_context = PasswordHash((Argon2Hasher(),))


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




