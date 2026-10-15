from pydantic import BaseModel, Field, ConfigDict
from typing import List

from app.orders.enum import OrderStatus, OrderEvent

class ORMSchema(BaseModel):
        model_config = ConfigDict(from_attributes=True)



class OrderItemCreate(BaseModel):
        product_id: int
        quantity: int

class OrderItemResponse(ORMSchema):
        id: int
        order_id: int
        product_id: int
        quantity: int
        unit_price: int
        subtotal: int


class OrderCreate(BaseModel):
        customer_id: int
        order_items: List[OrderItemCreate]
        
