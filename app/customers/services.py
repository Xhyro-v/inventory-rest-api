from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, status

from app.dependencies.customer import check_customer_status
from app.customers.enum import ExistStatus
from app.customers.schemas import CustomerResponse, CustomerCreate
from app.customers.repositories import create_customer
from app.customers.models import Customer as CustomerModel



class CustomerService:

        @staticmethod
        def process_customer(
                result: check_customer_status,
                db: Session
        ) -> CustomerModel:
                if result.status == ExistStatus.NOT_EXIST:
                        payload: CustomerCreate = result.customer_data
                        print(f"Customer with phone {payload.phone} not found. Make a new one... ")

                        new_customer = CustomerModel(
                              name=payload.name,
                              phone=payload.phone
                        )

                        try:
                            create_customer(db, new_customer)
                        except IntegrityError:
                              db.rollbackack()
                              raise HTTPException(
                                   status_code=status.HTTP_409_CONFLICT,
                                   detail="Customer already registered."
                              )
                        return {
                               "message": "Customer just added",
                               "status": "Not Exist -> Exist"
                        }
        
                else:
                     existing_customer: CustomerModel = result
                     return existing_customer

        @staticmethod
        def trigger_endpoint(customer: CustomerModel):
                return {"action": "success", "processed_name": customer.customer_data.name}
