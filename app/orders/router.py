from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user 
from app.db.session import get_db
from app.orders import services
from app.orders.schemas import OrderCreate, OrderRead
from app.auth.models import User

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return services.create_order(db, payload, current_user)