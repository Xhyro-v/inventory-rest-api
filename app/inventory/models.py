from sqlalchemy import String, Integer, Text, func, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from app.db.base import Base

class StockHistory(Base):

        __tablename__ = 'stock_history'
    
        id : Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
        product_id : Mapped[int] = mapped_column(ForeignKey('products.id'),nullable=False)
        quantity_change: Mapped[int] = mapped_column(nullable=False)
        stock_before : Mapped[int] = mapped_column(nullable=False)
        stock_after : Mapped[int] = mapped_column(nullable=False)
        reason : Mapped[str | None] = mapped_column(Text, nullable=True)
        order_id : Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=True)
        user_id : Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

        created_at: Mapped[datetime] = mapped_column(
                                    DateTime(timezone=True), 
                                    server_default=func.now()
                                )


        products = relationship("Product", back_populates="stock_history")  
        users = relationship("User", back_populates="stock_history")  
        orders = relationship("Order", back_populates="stock_history")  
