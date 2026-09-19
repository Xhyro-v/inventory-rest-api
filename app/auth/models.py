from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.db.base import Base
from app.auth.enum import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    order_histories: Mapped[List["OrderHistory"]] = relationship("OrderHistory", back_populates="user")
    stock_histories: Mapped[List["StockHistory"]] = relationship("StockHistory", back_populates="user")