from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.customers.models import Customer
from app.customers.repositories import get_by_phone
from app.orders.repositories import update_order_status, get_by_id
from app.orders.enum import OrderEvent, OrderStatus
from app.orders.models import Order, OrderHistory, OrderItem
from app.orders.schemas import OrderCreate, UpdateStatusOrder


from app.auth.models import User

from app.inventory.models import StockHistory

from app.products.models import Product
from app.products.repository import lock_products
from app.products.services import check_stock, soft_check
from app.products.enums import Reason




EVENT_MAP = {
    OrderStatus.PENDING: OrderEvent.ORDER_CREATED,
    OrderStatus.CONFIRMED: OrderEvent.ORDER_CONFIRMED,
    OrderStatus.COMPLETED: OrderEvent.ORDER_COMPLETED,
    OrderStatus.CANCELLED: OrderEvent.ORDER_CANCELLED,
}


def _resolve_customer(db: Session, name: str, phone: str) -> Customer:
    customer = get_by_phone(db, phone)
    if customer:
        return customer

    try:
        # Savepoint: if a concurrent request created the same phone,
        # only this block is rolled back, not the whole transaction.
        with db.begin_nested():
            customer = Customer(name=name, phone=phone)
            db.add(customer)
            db.flush()
        return customer
    except IntegrityError:
        customer = get_by_phone(db, phone)
        if customer is None:
            raise
        return customer


def create_order(db: Session, payload: OrderCreate, actor: User) -> Order:
    try:
        customer = _resolve_customer(db, payload.customer_name, payload.customer_phone)

        requested: dict[int, int] = defaultdict(int)
        for item in payload.items:
            requested[item.product_id] += item.quantity

        products = db.scalars(
            select(Product).where(Product.id.in_(requested.keys()))
        ).all()
        product_map = {p.id: p for p in products}

        missing = set(requested) - set(product_map)
        if missing:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Product not found: {sorted(missing)}",
            )

        for product_id, qty in requested.items():
            product = product_map[product_id]
            if not product.status:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product.name}' is inactive",
                )
            if qty > product.stock:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for '{product.name}': "
                        f"requested {qty}, available {product.stock}"
                    ),
                )

        order = Order(
            customer_id=customer.id,
            total_amount=Decimal("0.00"),
            status=OrderStatus.PENDING,
        )
        total = Decimal("0.00")
        for product_id, qty in requested.items():
            product = product_map[product_id]
            subtotal = product.price * qty
            total += subtotal
            order.order_items.append(
                OrderItem(
                    product_id=product_id,
                    quantity=qty,
                    unit_price=product.price,
                    subtotal=subtotal,
                )
            )
        order.total_amount = total

        db.add(order)
        db.flush()  
        db.add(
            OrderHistory(
                order_id=order.id,
                event=OrderEvent.ORDER_CREATED,
                user_id=actor.id,
                status_before=OrderStatus.PENDING,  # non-nullable column; no prior state
                status_after=OrderStatus.PENDING,
                reason="Order created",
            )
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    return db.scalar(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.order_items))
    )


from app.products import services as product_services


def apply_stock_effects(
    db: Session,
    order: Order,
    status_before: OrderStatus,
    status_after: OrderStatus,
    actor: User,
) -> None:
    # PENDING -> CONFIRMED: kurangi stok. CONFIRMED -> CANCELLED: kembalikan.
    if status_before == OrderStatus.PENDING and status_after == OrderStatus.CONFIRMED:
        sign, reason = -1, Reason.BUY
    elif status_before == OrderStatus.CONFIRMED and status_after == OrderStatus.CANCELLED:
        sign, reason = +1, Reason.CANCEL_RESTOCK
    else:
        return

    requested: dict[int, int] = {}
    for item in order.order_items:
        requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

    products = lock_products(db, sorted(requested))

    missing = set(requested) - set(products)
    if missing:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {sorted(missing)}",
        )

    if sign < 0:
        for product_id, qty in requested.items():
            check_stock(products[product_id], qty)

    for product_id in sorted(requested):
        product_services.apply_stock_change(
            db,
            products[product_id],
            sign * requested[product_id],
            reason,
            actor,
            order_id=order.id,
        )

    
def change_order_status(
    db: Session,
    payload: UpdateStatusOrder,
    order_id: int,
    actor: User,
) -> Order:
    try:
        order = get_by_id(db, order_id, for_update=True)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

        status_before = order.status

        if not status_before.can_transition_to(payload.status):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Cannot change status from {status_before.value} to {payload.status.value}",
            )

        # efek stok (BUY / CANCEL_RESTOCK) 
        apply_stock_effects(db, order, status_before, payload.status, actor)

        update_order_status(db, order, payload.status)

        db.add(OrderHistory(
            order_id=order.id,
            event=EVENT_MAP[payload.status],
            user_id=actor.id,
            status_before=status_before,
            status_after=payload.status,
            reason=f"Order status changed to {payload.status.value}",
        ))

        db.commit()         
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order