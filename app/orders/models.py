from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Integer, ForeignKey, Numeric, DateTime, Enum, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.orders.enum import OrderStatus, OrderEvent


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    order_histories: Mapped[List["OrderHistory"]] = relationship("OrderHistory", back_populates="order")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    stock_histories: Mapped[List["StockHistory"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)  # <-- FIX: kolom ini yang hilang
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")


class OrderHistory(Base):
    __tablename__ = 'order_history'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    event: Mapped[OrderEvent] = mapped_column(Enum(OrderEvent), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    status_before: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False)
    status_after: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    order: Mapped["Order"] = relationship("Order", back_populates="order_histories")
    user: Mapped["User"] = relationship("User", back_populates="order_histories")