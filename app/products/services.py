from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, status

from app.db.session import get_db
from app.products.models import Product as ProductModel
from app.products.repository import get_by_id, create_product, update_product, get_by_sku, delete_product, get_stock_product
from app.dependencies.auth import get_current_user, RoleChecker
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


def update_product_service(
        db: Session,
        product_id: int,
        data: ProductUpdate
):
        if not data:
                raise HTTPExceptoion(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Data not found"
                )

        product = get_by_id(db, product_id)

        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found"
                )
        
        product.name=data.name,
        product.description=data.description,
        product.price=data.price,
        product.status=data.status

        try:
                updated_product = update_product(db, product)
        except IntegrityError:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Product already exist"
                )

        return {
                "message" : "Product successfully updated",
                "product" : updated_product.name
        }


def delete_product_service(
        db: Session,
        product_id: int
):
        product = get_by_id(db, product_id)

        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found"
                )

        try:
                delete_product(db, product)
        except IntegrityError:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Product can't be deleted"
                )
     
        return {
                "message" : "Product successfully deleted",
                "product" : product.name
        }



def get_product_by_sku(
        db: Session,
        product_sku: str
):
        product = get_by_sku(db, product_sku)

        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found sku" 
                )

        return product

def get_product_by_id(
        db: Session,
        product_id: int
):
        product = get_by_id(db, product_id)

        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product with id {product_id} not found" 
                )

        return product




def get_stock_product_service(
        db: Session,
        product_id: int
):
        product = get_by_id(db, product_id)
        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product with id={product_id} not found"
                                )

        product_stock = get_stock_product(db, product_id)

        if not product_stock:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product data not found"
                )
        return {
                "message": f"{product.name} stock",
                "stock": product.stock
        }


