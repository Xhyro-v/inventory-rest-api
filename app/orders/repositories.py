from sqlalchemy.orm import Session
from app.orders.enum import OrderEvent, OrderStatus
from app.orders.models import OrderItem 




def create_order_item(db: Session, order_item: OrderItem) -> OrderItem:
        db.add(order_item)
        db.commit()
        db.refresh(order_item)

        return order_item


