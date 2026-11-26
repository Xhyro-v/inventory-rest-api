from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user 
from app.db.session import get_db
from app.orders import services
from app.orders.schemas import OrderCreate, OrderRead, UpdateStatusOrder
from app.auth.models import User

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.create_order(db, payload, current_user)

@order_router.patch("/{order_id}/status", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def update_order_status(
    payload: UpdateStatusOrder,
    order_id: int,
    actor: Session = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.change_order_status(db, payload, order_id, actor)

@order_router.patch("/{order_id}/status/cancell", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def cancell_order_status(
    order_id: int,
    actor: Session = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.cancell_order(db, order_id, actor)
