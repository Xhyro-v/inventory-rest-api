from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.auth.enum import UserRole

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email : Mapped[str] = mapped_column(unique=True, nullable=False) 
    role: Mapped[UserRole] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    order_history = relationship("OrderHistory", back_populates="users")