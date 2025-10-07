from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.crud.base import CRUDBase
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Product]:
        return db.query(Product).filter(Product.name == name).first()

    def search(
        self,
        db: Session,
        *,
        keyword: str = "",
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        query = db.query(Product)
        if keyword:
            query = query.filter(
                or_(
                    Product.name.contains(keyword),
                    Product.sku.contains(keyword),
                    Product.description.contains(keyword)
                )
            )
        return query.offset(skip).limit(limit).all()

    def get_with_inventory(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        include_out_of_stock: bool = True
    ) -> List[Product]:
        """获取包含库存信息的商品列表"""
        query = db.query(Product).options(joinedload(Product.inventory))

        if not include_out_of_stock:
            query = query.join(Inventory).filter(Inventory.quantity > 0)

        return query.offset(skip).limit(limit).all()

    def get_multi_with_inventory(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """获取包含库存信息的商品列表"""
        return db.query(Product).options(joinedload(Product.inventory)).offset(skip).limit(limit).all()

    def get_low_stock_products(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """获取库存不足的商品"""
        return (
            db.query(Product)
            .join(Inventory)
            .options(joinedload(Product.inventory))
            .filter(and_(
                Inventory.quantity <= Product.reorder_level,
                Product.reorder_level > 0
            ))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def has_inventory(self, db: Session, *, product_id: int) -> bool:
        """检查商品是否有库存记录"""
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        return inventory is not None

    def has_transactions(self, db: Session, *, product_id: int) -> bool:
        """检查商品是否有关联的交易记录"""
        from app.models.purchase import PurchaseItem
        from app.models.sale import SaleItem

        purchase_item = db.query(PurchaseItem).filter(PurchaseItem.product_id == product_id).first()
        sale_item = db.query(SaleItem).filter(SaleItem.product_id == product_id).first()

        return purchase_item is not None or sale_item is not None


product = CRUDProduct(Product)