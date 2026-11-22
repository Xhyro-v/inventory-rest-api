from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, status
from typing import Dict

from app.db.session import get_db
from app.products.models import Product as ProductModel
from app.products.repository import (
                                        get_by_id,
                                        create_product,
                                        update_product,
                                        update_stock_product,
                                        get_by_sku,
                                        delete_product,
                                        get_stock_product
                                        )
from app.dependencies.auth import get_current_user, RoleChecker
from app.products.schemas import ProductCreate, ProductUpdate, ProductStockAdjust
from app.products.enums import Reason
from app.inventory.models import StockHistory


from app.auth.models import User


INCREASE_ONLY = {Reason.RESTOCK, Reason.CANCEL_RESTOCK}
DECREASE_ONLY = {Reason.LOST, Reason.DAMAGED, Reason.BUY}



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
                raise HTTPException(
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


def adjust_stock_product(
        db: Session,
        product_id: int,
        payload: ProductStockAdjust
):
        product = get_by_id(db, product_id, for_update=True)

        if not product:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found"
                )
        
        if payload.quantity_change == 0:
                raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="Quantity change cannot be zero",
                )

        if payload.reason == Reason.RESTOCK and payload.quantity_change < 0:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Restock reason cannot have a negative quantity (to be add)"
                )

        if payload.reason == Reason.LOST in Reason.DAMAGED and payload.quantity_change > 0:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="{payload.reason} reason cannot have a positive quantity (to be reduce)"
                        )

        product_stock_before = product.stock

        # Take from payload
        product_stock_after = product_stock_before + payload.quantity_change

        if product_stock_after < 0 :
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient stock for this adjustment"
                )
        
        try:
                updated_stock_product = update_stock_product(db, product_id, product_stock_after)

                if updated_stock_product is None:
                        raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="Something wrong"
                        )
                return {
                        "message": "Product stokc successfully adjusted",
                        "product": product_id
                }

        except Exception:
                db.rollback()
                raise HTTPException(
                        status_code=500,
                        detail="Failed to update product stock",
                )


def check_stock(product: ProductModel, qty: int) -> None:
    """Validate product is active and has enough stock. Raises HTTP 400/409-style errors."""
    if not product.status:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{product.name}' is inactive",
        )
    if qty > product.stock:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=(
                f"Insufficient stock for '{product.name}': "
                f"requested {qty}, available {product.stock}"
            ),
        )


def soft_check(products: Dict[int, ProductModel], requested: Dict[int, int]) -> None:
    """Informational check at order creation. No lock, no reservation."""
    for product_id, qty in requested.items():
        check_stock(products[product_id], qty)


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



def apply_stock_change(
    db: Session,
    product: ProductModel,
    quantity_change: int,
    reason: Reason,
    actor: User,
    order_id: int | None = None,
) -> StockHistory:
    if quantity_change == 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Quantity change cannot be zero")

    if reason in INCREASE_ONLY and quantity_change < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail=f"{reason.value} requires a positive quantity")

    if reason in DECREASE_ONLY and quantity_change > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail=f"{reason.value} requires a negative quantity")

    stock_before = product.stock
    stock_after = stock_before + quantity_change

    if stock_after < 0:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            detail=f"Insufficient stock for product {product.id}")

    product.stock = stock_after
    history = StockHistory(
        product_id=product.id,
        order_id=order_id,
        user_id=actor.id,
        quantity_change=quantity_change,
        stock_before=stock_before,
        stock_after=stock_after,
        reason=reason,
    )
    db.add(history)
    return history   # tidak commit