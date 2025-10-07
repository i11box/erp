from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.models.inventory import Inventory, InventoryMovement
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryMovementCreate
from app.crud.base import CRUDBase
from datetime import datetime

class InventoryCRUD(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    def get_by_product(self, db: Session, *, product_id: int) -> Optional[Inventory]:
        return db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def get_with_product(self, db: Session, *, skip: int = 0, limit: int = 100):
        return (
            db.query(self.model)
            .options(joinedload(Inventory.product))
            .order_by(Inventory.last_updated.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_low_stock_items(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取库存不足的商品"""
        return (
            db.query(self.model)
            .options(joinedload(Inventory.product))
            .join(Inventory.product)
            .filter(
                or_(
                    Inventory.quantity <= Product.reorder_level,
                    Inventory.quantity == 0
                )
            )
            .order_by(Inventory.quantity.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_out_of_stock_items(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取缺货商品"""
        return (
            db.query(self.model)
            .options(joinedload(Inventory.product))
            .filter(Inventory.quantity == 0)
            .order_by(Inventory.last_updated.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_or_update(self, db: Session, *, product_id: int, quantity: int, avg_cost: float = 0):
        """创建或更新库存记录"""
        inventory = self.get_by_product(db, product_id=product_id)

        if inventory:
            inventory.quantity = quantity
            if avg_cost > 0:
                inventory.avg_cost = avg_cost
            inventory.last_updated = datetime.now()
            db.commit()
            db.refresh(inventory)
            return inventory
        else:
            inventory = Inventory(
                product_id=product_id,
                quantity=quantity,
                avg_cost=avg_cost,
                last_updated=datetime.now()
            )
            db.add(inventory)
            db.commit()
            db.refresh(inventory)
            return inventory

    def adjust_inventory(
        self,
        db: Session,
        *,
        product_id: int,
        adjustment_quantity: int,
        reason: str,
        user_id: int,
        new_avg_cost: Optional[float] = None
    ) -> Inventory:
        """调整库存数量"""
        inventory = self.get_by_product(db, product_id=product_id)

        if not inventory:
            # Create new inventory record if doesn't exist
            inventory = Inventory(
                product_id=product_id,
                quantity=adjustment_quantity,
                avg_cost=new_avg_cost or 0,
                last_updated=datetime.now()
            )
            db.add(inventory)
            db.flush()
        else:
            # Update existing inventory
            old_quantity = inventory.quantity
            inventory.quantity += adjustment_quantity
            if new_avg_cost and new_avg_cost > 0:
                inventory.avg_cost = new_avg_cost
            inventory.last_updated = datetime.now()

        # Record inventory movement
        movement_type = "in" if adjustment_quantity > 0 else "out" if adjustment_quantity < 0 else "adjustment"
        movement = InventoryMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=adjustment_quantity,
            reference_type="adjustment",
            reason=reason
        )
        db.add(movement)

        db.commit()
        db.refresh(inventory)
        return inventory

    def search_inventory(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inventory]:
        """搜索库存"""
        return (
            db.query(self.model)
            .options(joinedload(Inventory.product))
            .join(Inventory.product)
            .filter(
                or_(
                    Product.name.contains(query),
                    Product.sku.contains(query),
                    Product.description.contains(query)
                )
            )
            .order_by(Inventory.last_updated.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_total_inventory_value(self, db: Session) -> float:
        """获取库存总价值"""
        result = db.query(Inventory).all()
        total_value = sum(item.quantity * float(item.avg_cost) for item in result)
        return total_value

    def get_inventory_summary(self, db: Session) -> dict:
        """获取库存汇总信息"""
        total_items = db.query(Inventory).count()
        low_stock_items = db.query(Inventory).join(Inventory.product).filter(
            Inventory.quantity <= Product.reorder_level
        ).count()
        out_of_stock_items = db.query(Inventory).filter(Inventory.quantity == 0).count()
        total_value = self.get_total_inventory_value(db)

        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_inventory_value": total_value
        }


class InventoryMovementCRUD(CRUDBase[InventoryMovement, InventoryMovementCreate, dict]):
    def get_by_product(
        self,
        db: Session,
        *,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """获取指定商品的库存变动记录"""
        return (
            db.query(self.model)
            .options(joinedload(InventoryMovement.product))
            .filter(InventoryMovement.product_id == product_id)
            .order_by(desc(InventoryMovement.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_movements(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        movement_type: Optional[str] = None
    ) -> List[InventoryMovement]:
        """获取所有库存变动记录"""
        query = (
            db.query(self.model)
            .options(joinedload(InventoryMovement.product))
            .order_by(desc(InventoryMovement.created_at))
        )

        if movement_type:
            query = query.filter(InventoryMovement.movement_type == movement_type)

        return query.offset(skip).limit(limit).all()

    def get_movements_by_date_range(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """获取指定日期范围内的库存变动记录"""
        return (
            db.query(self.model)
            .options(joinedload(InventoryMovement.product))
            .filter(
                and_(
                    InventoryMovement.created_at >= start_date,
                    InventoryMovement.created_at <= end_date
                )
            )
            .order_by(desc(InventoryMovement.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create singleton instances
inventory = InventoryCRUD(Inventory)
inventory_movement = InventoryMovementCRUD(InventoryMovement)