from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.products.services import create_product_service
from app.products.schemas import ProductCreate
from app.products.models import Product
from app.db.session import get_db
from app.dependencies.auth import get_current_user, RoleChecker, allow_admin_only, allow_staff_and_admin





product_router = APIRouter(
        prefix="/v1/product",
        tags=["Products"]
)


@product_router.post("/products")
def create_product(
        data: ProductCreate,
        db: Session = Depends(get_db),
        access = Depends(allow_admin_only)

):
        return create_product_service(db, data)