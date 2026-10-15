# Router Test for Customer Checker

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.customers.schemas import CustomerCreate, CustomerCheckResult
from app.dependencies.customer import check_customer_status
from app.customers.services import CustomerService

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/process")
def process_customer_endpoint(
    check_result: CustomerCheckResult = Depends(check_customer_status),
    db: Session = Depends(get_db)
):
    final_customer= CustomerService.process_customer(check_result, db)
    
    post_result = CustomerService.trigger_endpoint(final_customer)
    
    return {
        "status_check": check_result.status,
        "Customer": {
            "id": final_customer.customer_data.id,
            "name": final_customer.customer_data.name,
            "phone": final_customer.customer_data.phone
        },
        "post_response": post_result
    }