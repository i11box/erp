from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from sqlalchemy import or_


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Supplier]:
        return db.query(Supplier).filter(Supplier.name == name).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Supplier]:
        return db.query(Supplier).filter(Supplier.email == email).first()

    def search(
        self,
        db: Session,
        *,
        keyword: str = "",
        skip: int = 0,
        limit: int = 100
    ) -> List[Supplier]:
        query = db.query(Supplier)
        if keyword:
            query = query.filter(
                or_(
                    Supplier.name.contains(keyword),
                    Supplier.contact_person.contains(keyword),
                    Supplier.email.contains(keyword),
                    Supplier.phone.contains(keyword)
                )
            )
        return query.offset(skip).limit(limit).all()

    def has_purchases(self, db: Session, *, supplier_id: int) -> bool:
        """检查供应商是否有关联的采购记录"""
        from app.models.purchase import Purchase
        purchase = db.query(Purchase).filter(Purchase.supplier_id == supplier_id).first()
        return purchase is not None


supplier = CRUDSupplier(Supplier)