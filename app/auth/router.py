from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import UserRegister, UserLogin
from app.db.session import get_db
from app.auth.services import get_current_user, login_user, register_user, oauth2_scheme


auth_router = APIRouter(
        prefix="/auth",
        tags=["Authentication"]
)


@auth_router.post("/registration")
def user_registration_router(
            data: UserRegister,
            db: Session = Depends(get_db)
):
        return register_user(db, data)
