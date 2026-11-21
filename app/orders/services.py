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
        # 1-5. Customer resolution
        customer = _resolve_customer(db, payload.customer_name, payload.customer_phone)

        # Merge duplicate product_id lines so stock is validated against the total
        requested: dict[int, int] = defaultdict(int)
        for item in payload.items:
            requested[item.product_id] += item.quantity

        # Take product info (price, stock, status). Soft check: no lock, no reservation.
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

        # Validate active status and early stock check
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

        # Create order header (PENDING) + items. Stock is NOT deducted here.
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
        db.flush()  # get order.id

        # Record OrderHistory (ORDER_CREATED)
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


    
def change_order_status(
    db: Session, 
    payload: UpdateStatusOrder,
    order_id: int, 
    actor: User
) -> Order:
    try:
        # 1. Fetch & lock order
        order = get_by_id(db, order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

        # 2. Prevent duplicate/redundant status changes
        if order.status == payload.status:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Order status is already {order.status.value}",
            )

        status_before = order.status

        # 3. Deduct stock ONLY when transitioning from PENDING -> CONFIRMED
        if status_before == OrderStatus.PENDING and payload.status == OrderStatus.CONFIRMED:
            requested: dict[int, int] = {}
            for item in order.order_items:
                requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

            products = lock_products(db, requested.keys())

            missing = set(requested) - set(products)
            if missing:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail=f"Product not found: {sorted(missing)}",
                )

            # Check stock availability
            for product_id, qty in requested.items():
                check_stock(products[product_id], qty)

            # Deduct stock and log StockHistory
            for product_id in sorted(requested):
                qty = requested[product_id]
                product = products[product_id]

                stock_before = product.stock
                product.stock = stock_before - qty

                db.add(
                    StockHistory(
                        product_id=product_id,
                        order_id=order.id,
                        user_id=actor.id,
                        quantity_change=-qty,
                        stock_before=stock_before,
                        stock_after=product.stock,
                        reason=Reason.BUY,
                    )
                )

        # 4. Map event dynamically based on payload status
        event_map = {
            OrderStatus.CONFIRMED: getattr(OrderEvent, "ORDER_CONFIRMED", "ORDER_CONFIRMED"),
            OrderStatus.CANCELLED: getattr(OrderEvent, "ORDER_CANCELLED", "ORDER_CANCELLED"),
        }
        event = event_map.get(payload.status, OrderEvent.ORDER_CONFIRMED)

        # 5. Apply new status and log OrderHistory
        order.status = payload.status
        db.add(
            OrderHistory(
                order_id=order.id,
                event=event,
                user_id=actor.id,
                status_before=status_before,
                status_after=payload.status,
                reason=f"Order status changed to {payload.status.value}",
            )
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order