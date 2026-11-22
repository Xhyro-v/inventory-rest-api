from enum import Enum

class OrderStatus(str, Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        COMPLETED = "completed"

        def can_transition_to(self, new: "OrderStatus") -> bool:
                return new in ALLOWED_TRANSITIONS[self]

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING:   {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED:   {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),   # final
    OrderStatus.CANCELLED: set(),   # final
}

class OrderEvent(str, Enum):
        ORDER_CREATED = "order_created"
        ORDER_CONFIRMED = "order_confirmed"
        ORDER_CANCELLED = "order_cancelled"
        ORDER_COMPLETED = "order_completed"