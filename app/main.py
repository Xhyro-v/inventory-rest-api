from fastapi import FastAPI

from app.auth.router import auth_router
from app.products.router import product_router
import app.db.base_all_model

app = FastAPI(
    title="API"
)

app.include_router(auth_router)
app.include_router(product_router)