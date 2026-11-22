from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Optional

from app.orders.enum import OrderEvent, OrderStatus
from app.orders.models import OrderItem, Order



def get_by_id(db: Session, order_id: int, for_update: bool = False) -> Order | None:
    stmt = select(Order).where(Order.id == order_id)
    if for_update:
        stmt = stmt.with_for_update()
    return db.scalar(stmt)


def create_order_item(db: Session, order_item: OrderItem) -> OrderItem:
        db.add(order_item)
        db.commit()
        db.refresh(order_item)

        return order_item


def update_order_status(db: Session, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        db.flush()          # kirim ke DB tapi belum commit
        return order



