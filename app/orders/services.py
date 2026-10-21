from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.customers.models import Customer
from app.customers.repositories import get_by_phone
from app.orders.enum import OrderEvent, OrderStatus
from app.orders.models import Order, OrderHistory, OrderItem
from app.orders.schemas import OrderCreate
from app.products.models import Product
from app.auth.models import User


def _resolve_customer(db: Session, name: str, phone: str) -> Customer:
    """Reuse customer by phone, or create a new one (no commit)."""
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