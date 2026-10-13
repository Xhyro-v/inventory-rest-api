from app.products.models import Product

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update

def get_by_id(db: Session, product_id: int) -> Product | None :
        return db.get(Product, product_id)

def get_by_sku(db: Session, product_sku: str) -> Product | None :
        return db.scalar(select(Product).where(Product.sku == product_sku))

def update_stock_product(
    db: Session, product_id: int, new_stock: int
) -> Optional[Product]:
        stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(stock=new_stock)
        .returning(Product)
        )
        updated_product = db.scalar(stmt)
        db.commit()

        return updated_product


def get_stock_product(db: Session, product_id: int):
        return db.scalar(select(Product.stock).where(Product.id == product_id))

def create_product(db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)

        return product 

def update_product(db: Session, product: Product) -> Product:
        db.commit()
        db.refresh(product)

        return product

def delete_product(db: Session, product: Product) -> Product:
        db.delete(product)
        db.commit()

        return product
