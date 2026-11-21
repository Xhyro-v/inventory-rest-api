from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Optional

from app.orders.enum import OrderEvent, OrderStatus
from app.orders.models import OrderItem, Order



def get_by_id(
        db: Session,
        order_id: int
):
        return db.get(Order, order_id)
        


def create_order_item(db: Session, order_item: OrderItem) -> OrderItem:
        db.add(order_item)
        db.commit()
        db.refresh(order_item)

        return order_item


def update_order_status(
    db: Session, 
    order_id: int, 
    new_order_status: OrderStatus
):
    stmt = select(Order).where(Order.id == order_id)
    order = db.scalar(stmt)
    
    if order:
        order.status = new_order_status
        db.commit()
        db.refresh(order)
        
    return order





