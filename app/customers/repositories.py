from sqlalchemy.orm import Session
from app.customers.models import Customer


def get_by_phone(db: Session, phone: str) -> Customer | None:
        return db.query(Customer).filter(Customer.phone == phone).first()

def create_customer(db: Session, customer: Customer) -> Customer:
        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

