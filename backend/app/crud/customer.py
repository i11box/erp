from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy import or_


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.name == name).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.email == email).first()

    def search(
        self,
        db: Session,
        *,
        keyword: str = "",
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        query = db.query(Customer)
        if keyword:
            query = query.filter(
                or_(
                    Customer.name.contains(keyword),
                    Customer.contact_person.contains(keyword),
                    Customer.email.contains(keyword),
                    Customer.phone.contains(keyword)
                )
            )
        return query.offset(skip).limit(limit).all()

    def has_sales(self, db: Session, *, customer_id: int) -> bool:
        """检查客户是否有关联的销售记录"""
        from app.models.sale import Sale
        sale = db.query(Sale).filter(Sale.customer_id == customer_id).first()
        return sale is not None


customer = CRUDCustomer(Customer)