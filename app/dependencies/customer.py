from sqlalchemy.orm import Session
from fastapi import Depends

from app.customers.repositories import get_by_phone
from app.customers.enum import ExistStatus
from app.db.session import get_db
from app.customers.schemas import CustomerCreate, CustomerCheckResult


def check_customer_status(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerCheckResult:
    customer = get_by_phone(db, payload.phone)
    
    if customer:
        return CustomerCheckResult(
            status=ExistStatus.EXIST,
            customer_data=customer
        )
    else:
        return CustomerCheckResult(
            status=ExistStatus.NOT_EXIST,
            customer_data=payload
        )