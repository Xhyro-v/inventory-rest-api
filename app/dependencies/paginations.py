from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.paginations.repositories import ProductRepository
from app.paginations.services import ProductService
from app.db.session import get_db


# --- Pagination query parameters (dipakai SEMUA endpoint list) ---
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Total data"),
    ) -> None:
        self.page = page
        self.limit = limit


# --- Injeksi per resource ---
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


# def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
#     return CustomerService(CustomerRepository(db))