from fastapi import FastAPI

from app.auth.router import auth_router
from app.products.router import products_router
from app.customers.router import router as customer_router_test
import app.db.base_all_model

app = FastAPI(
    title="API"
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(customer_router_test)