from fastapi import FastAPI, APIRouter

from app.auth.router import auth_router
import app.db.base_all_model

app = FastAPI(
    title="API"
)

auth_router = APIRouter(
        prefix="/v1/auth",
        tags=["Authentication"]
)


app.include_router(auth_router)