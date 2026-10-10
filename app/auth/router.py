from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import UserRegister, UserLogin
from app.db.session import get_db
from app.auth.services import register_user, login_user
from app.dependencies.auth import get_current_user, RoleChecker, allow_admin_only, allow_staff_and_admin


auth_router = APIRouter(\
        prefix="/v1/auth",
        tags=["Authentication"]
)


@auth_router.post("/registration")
def user_registration_router(
        data: UserRegister,
        db: Session = Depends(get_db),
        access = Depends(allow_admin_only)
):
        return register_user(db, data)

@auth_router.post("/login")
def user_login_router(
        data : UserLogin,
        db : Session = Depends(get_db)
):
        return login_user(db, data)

@auth_router.post("/token")
def get_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
              
        data = UserLogin(
                email=form_data.username,
                password=form_data.password
        )

        return login_user(db, data)