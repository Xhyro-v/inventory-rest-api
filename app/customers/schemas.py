from pydantic import BaseModel
from typing import Optional, Any
from app.customers.enum import ExistStatus

class CustomerCreate(BaseModel):
    name: str
    phone: str


class CustomerResponse(BaseModel):
    id: Optional[int] = None
    name: str
    phone: str

    class Config:
        from_attributes = True

class CustomerCheckResult(BaseModel):
    status: ExistStatus
    customer_data: Any