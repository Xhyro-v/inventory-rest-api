from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, status





from app.db.session import get_db
from app.products.models import Product as ProductModel
from app.products.repository import get_by_id, create_product
from app.auth.services import get_current_user, RoleChecker
from app.products.schemas import ProductCreate, ProductUpdate, ProductStockUpdate




def create_product_service(
        db: Session,
        data : ProductCreate
) -> ProductModel:
        if data is None:
                return HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Data not found"
                )

        new_product = ProductModel(
                sku=data.sku,
                name=data.name,
                description=data.description,
                price=data.price,
                stock=data.stock,
                status=data.status
        )

        
        try:
                create_product(db, new_product)
        except IntegrityError:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Product already exist"
                )

        return {
                "message" : "Product successfully created",
                "product" : new_product.name
        }