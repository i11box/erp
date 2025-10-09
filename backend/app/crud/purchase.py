from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.purchase import Purchase, PurchaseItem
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.inventory import InventoryMovement
from app.schemas.purchase import PurchaseCreate, PurchaseUpdate, PurchaseItemCreate
from app.crud.base import CRUDBase
from datetime import datetime
import uuid


class PurchaseCRUD(CRUDBase[Purchase, PurchaseCreate, PurchaseUpdate]):
    def create_purchase_with_items(
        self, db: Session, *, purchase_in: PurchaseCreate, user_id: int
    ) -> Purchase:
        # Generate purchase number
        purchase_number = f"PO{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

        # Create purchase
        db_purchase = Purchase(
            supplier_id=purchase_in.supplier_id,
            user_id=user_id,
            purchase_number=purchase_number,
            total_amount=0,  # Will be calculated below
            status="pending"
        )
        db.add(db_purchase)
        db.flush()  # Get the ID without committing

        total_amount = 0

        # Create purchase items and update inventory
        for item_data in purchase_in.items:
            # Calculate total price for this item
            item_total = item_data.quantity * item_data.unit_price
            total_amount += item_total

            # Create purchase item
            db_item = PurchaseItem(
                purchase_id=db_purchase.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_total
            )
            db.add(db_item)

            # Update inventory
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item_data.product_id
            ).first()

            if inventory:
                # Update existing inventory
                old_quantity = inventory.quantity
                inventory.quantity += item_data.quantity

                # Calculate new average cost
                total_cost = (old_quantity * inventory.avg_cost) + item_total
                inventory.avg_cost = total_cost / inventory.quantity
                inventory.last_updated = datetime.now()
            else:
                # Create new inventory record
                inventory = Inventory(
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    avg_cost=item_data.unit_price,
                    last_updated=datetime.now()
                )
                db.add(inventory)

            # Record inventory movement
            movement = InventoryMovement(
                product_id=item_data.product_id,
                movement_type="in",
                quantity=item_data.quantity,
                reference_type="purchase",
                reference_id=db_purchase.id,
                reason=f"采购订单 {purchase_number}"
            )
            db.add(movement)

        # Update purchase total amount
        db_purchase.total_amount = total_amount

        db.commit()
        db.refresh(db_purchase)
        return db_purchase

    def get_with_items(self, db: Session, id: int) -> Optional[Purchase]:
        return (
            db.query(self.model)
            .options(joinedload(Purchase.items).joinedload(PurchaseItem.product))
            .filter(Purchase.id == id)
            .first()
        )

    def get_with_items_flattened(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取采购订单信息并扁平化供应商和商品字段"""
        results = (
            db.query(Purchase, Supplier)
            .join(Supplier, Purchase.supplier_id == Supplier.id)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for purchase, supplier in results:
            # 将采购订单和供应商信息合并为扁平结构
            flattened_item = {
                "id": purchase.id,
                "supplier_id": purchase.supplier_id,
                "user_id": purchase.user_id,
                "purchase_number": purchase.purchase_number,
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
                "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
                "supplier_name": supplier.name,
                "items": []
            }
            
            # 处理订单项
            for item in purchase.items:
                item_dict = {
                    "id": item.id,
                    "purchase_id": item.purchase_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price else 0,
                    "total_price": float(item.total_price) if item.total_price else 0
                }
                
                # 如果有产品信息，添加产品详情
                if item.product:
                    item_dict.update({
                        "product_name": item.product.name,
                        "product_sku": item.product.sku,
                        "product_description": item.product.description,
                        "unit": item.product.unit
                    })
                
                flattened_item["items"].append(item_dict)
            
            flattened_results.append(flattened_item)
        
        return flattened_results

    def get_multi_with_items(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Purchase]:
        return (
            db.query(self.model)
            .options(joinedload(Purchase.items).joinedload(PurchaseItem.product))
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_with_items_flattened(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ):
        """获取采购订单列表并扁平化供应商字段"""
        results = (
            db.query(Purchase, Supplier)
            .join(Supplier, Purchase.supplier_id == Supplier.id)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for purchase, supplier in results:
            # 将采购订单和供应商信息合并为扁平结构
            flattened_item = {
                "id": purchase.id,
                "supplier_id": purchase.supplier_id,
                "user_id": purchase.user_id,
                "purchase_number": purchase.purchase_number,
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
                "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
                "supplier_name": supplier.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def update_status(
        self, db: Session, *, db_obj: Purchase, status: str
    ) -> Purchase:
        db_obj.status = status
        db_obj.updated_at = datetime.now()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_supplier(
        self, db: Session, *, supplier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Purchase]:
        return (
            db.query(self.model)
            .filter(Purchase.supplier_id == supplier_id)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_supplier_flattened(
        self, db: Session, *, supplier_id: int, skip: int = 0, limit: int = 100
    ):
        """根据供应商获取采购订单列表并扁平化供应商字段"""
        results = (
            db.query(Purchase, Supplier)
            .join(Supplier, Purchase.supplier_id == Supplier.id)
            .filter(Purchase.supplier_id == supplier_id)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for purchase, supplier in results:
            # 将采购订单和供应商信息合并为扁平结构
            flattened_item = {
                "id": purchase.id,
                "supplier_id": purchase.supplier_id,
                "user_id": purchase.user_id,
                "purchase_number": purchase.purchase_number,
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
                "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
                "supplier_name": supplier.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Purchase]:
        return (
            db.query(self.model)
            .filter(Purchase.status == status)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status_flattened(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ):
        """根据状态获取采购订单列表并扁平化供应商字段"""
        results = (
            db.query(Purchase, Supplier)
            .join(Supplier, Purchase.supplier_id == Supplier.id)
            .filter(Purchase.status == status)
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for purchase, supplier in results:
            # 将采购订单和供应商信息合并为扁平结构
            flattened_item = {
                "id": purchase.id,
                "supplier_id": purchase.supplier_id,
                "user_id": purchase.user_id,
                "purchase_number": purchase.purchase_number,
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
                "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
                "supplier_name": supplier.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def search_purchases(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Purchase]:
        return (
            db.query(self.model)
            .join(Purchase.supplier)
            .filter(
                or_(
                    Purchase.purchase_number.contains(query),
                    Supplier.name.contains(query)
                )
            )
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_purchases_flattened(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ):
        """搜索采购订单并扁平化供应商字段"""
        results = (
            db.query(Purchase, Supplier)
            .join(Supplier, Purchase.supplier_id == Supplier.id)
            .filter(
                or_(
                    Purchase.purchase_number.contains(query),
                    Supplier.name.contains(query)
                )
            )
            .order_by(Purchase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for purchase, supplier in results:
            # 将采购订单和供应商信息合并为扁平结构
            flattened_item = {
                "id": purchase.id,
                "supplier_id": purchase.supplier_id,
                "user_id": purchase.user_id,
                "purchase_number": purchase.purchase_number,
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
                "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
                "supplier_name": supplier.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results


# Create a singleton instance
purchase = PurchaseCRUD(Purchase)