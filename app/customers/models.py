from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Customer(Base):
        __tablename__ = 'customers'
        
        id: Mapped[int] = mapped_column(primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
        
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), 
            server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            onupdate=func.now()
        )
        
        orders = relationship("Order",back_populates="customers")