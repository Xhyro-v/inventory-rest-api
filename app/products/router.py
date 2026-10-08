from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.products.services import create_product_service, update_product_service, get_product_by_sku, get_product_by_id
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.products.models import Product
from app.db.session import get_db
from app.dependencies.auth import get_current_user, RoleChecker, allow_admin_only, allow_staff_and_admin

from app.dependencies.paginations import (
    PaginationParams,
    get_product_service,
)
from app.paginations.schemas import PaginatedResponse
from app.products.schemas import ProductResponse
from app.paginations.services import ProductService


products_router = APIRouter(
        prefix="/v1/products",
        tags=["Products"]
)


@products_router.post("")
def create_product(
        data: ProductCreate,
        db: Session = Depends(get_db),
        access = Depends(allow_admin_only)

):
        return create_product_service(db, data)


@products_router.patch("")
def update_product(
        data: ProductUpdate,
        product_id: int,
        db: Session = Depends(get_db),

):
        return update_product_service(db, product_id, data)


@products_router.get("", response_model=PaginatedResponse[ProductResponse])
def get_list_products(
        params: PaginationParams = Depends(),
        service: ProductService = Depends(get_product_service),
        access = Depends(allow_admin_only)
):
        """
        - **page** (int, default: `1`): Page number.
        - **limit** (int, default: `10`): Total data.
        """
        return service.paginate(params.page, params.limit)


@products_router.get("/{product_id}")
def get_product_by_id_r(
        product_id: int,
        db: Session = Depends(get_db),
):
        return get_product_by_id(db, product_id)



@products_router.get("/SKU/{product_sku}")
def get_product_by_sku_r(
        product_sku: str,
        db: Session = Depends(get_db),
):
        return get_product_by_sku(db, product_sku)



