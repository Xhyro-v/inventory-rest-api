from enum import Enum

class OrderStatus(str, Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        COMPLETED = "completed"

class OrderEvent(str, Enum):
        ORDER_CREATED = "order_created"
        ORDER_CONFIRMED = "order_confirmed"
        ORDER_CANCELLED = "order_cancelled"
        ORDER_COMPLETED = "order_completed"