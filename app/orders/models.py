from sqlalchemy import String, Integer, ForeignKey, Decimal, Numeric, DateTime, func
from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.orders.enum import OrderStatus


class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True)

    customer: Mapped["Customer"] = relationship(back_populates="orders")

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", 
        cascade="all, delete-orphan" #IDK how this is work
    )
    status : Mapped[OrderStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), 
                server_default=func.now()
            )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    product_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()