from sqlalchemy import String, Integer, ForeignKey, Decimal, Numeric, DateTime, func, Text
from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.orders.enum import OrderStatus
from app.orders.enum import OrderEvent


class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer : Mapped[List["Customer"]] = relationship(back_populates=order, cascade="all, delete-orphan")
    order_item : Mapped[List["OrderItem"]] = relationship(back_populates=order, cascade="all, delete-orphan")
    total_amount : Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    status : Mapped["OrderStatus"] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
                        DateTime(timezone=True), 
                        server_default=func.now()
                    )
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            onupdate=func.now()
    )

    customers = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem",back_populates="orders")
    order_history = relationship("OrderHistory",back_populates="orders")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id : Mapped[int] = mapped_column(ForeignKey('produtcs.id'), nullable=False)
    quantity : Mapped[int] = mapped_column(nullable=False)
    unit_price : Mapped[Decimal] = mapped_column(ForeignKey('products.price'))
    subtotal : Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)

    products = relationship("Product", back_populates="order_items")
    orders = relationship("Order", back_populates="order_items")

    

class OrderHistory(Base):
    __tablename__ = 'order_history'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id : Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    event : Mapped[OrderEvent] = mapped_column(nullable=False)
    user : Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    status_before : Mapped[OrderStatus] = mapped_column(nullable=False)
    status_after : Mapped[OrderStatus] = mapped_column(nullable=False)
    reason : Mapped[str | None] = mapped_column(Text(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
                            DateTime(timezone=True), 
                            server_default=func.now()
                        )

    orders = relationship("Order", back_populates="order_history")
    users = relationship("User", back_populates="order_history")
