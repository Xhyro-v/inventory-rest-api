from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import UserRegister, UserLogin
from app.db.session import get_db
from app.auth.services import get_current_user, login_user, register_user, allow_admin_only, allow_staff_and_admin


auth_router = APIRouter(\
        prefix="/v1/auth",
        tags=["Authentication"]
)


@auth_router.post("/registration")
def user_registration_router(
        allow_admin_only,
        data: UserRegister,
        db: Session = Depends(get_db)
):
        return register_user(db, data)

@auth_router.post("/login")
def user_login_router(
        data : UserLogin,
        db : Session = Depends(get_db)
):
        return login_user(db, data)