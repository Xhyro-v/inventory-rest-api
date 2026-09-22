from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import String, DateTime, Integer, Text, Numeric, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
        __tablename__ = 'products'

        id: Mapped[int] = mapped_column(primary_key=True, index=True)
        sku: Mapped[str] = mapped_column(String(12), index=True, unique=True, nullable=False)
        name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
        description: Mapped[str | None] = mapped_column(Text, nullable=True)
        price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
        stock: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
        status: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)
        created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now()
        )

        order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
        stock_histories: Mapped[List["StockHistory"]] = relationship("StockHistory", back_populates="product")