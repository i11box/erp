from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.sale import Sale, SaleItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.inventory import InventoryMovement
from app.schemas.sale import SaleCreate, SaleUpdate, SaleItemCreate
from app.crud.base import CRUDBase
from datetime import datetime
import uuid


class SaleCRUD(CRUDBase[Sale, SaleCreate, SaleUpdate]):
    def create_sale_with_items(
        self, db: Session, *, sale_in: SaleCreate, user_id: int
    ) -> Sale:
        # Generate sale number
        sale_number = f"SO{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

        # Check inventory availability first
        for item_data in sale_in.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item_data.product_id
            ).first()

            if not inventory or inventory.quantity < item_data.quantity:
                product = db.query(Product).filter(
                    Product.id == item_data.product_id
                ).first()
                product_name = product.name if product else f"商品ID {item_data.product_id}"
                raise ValueError(f"商品 '{product_name}' 库存不足，需要 {item_data.quantity} 件，可用 {inventory.quantity if inventory else 0} 件")

        # Create sale
        db_sale = Sale(
            customer_id=sale_in.customer_id,
            user_id=user_id,
            sale_number=sale_number,
            total_amount=0,  # Will be calculated below
            status="pending"
        )
        db.add(db_sale)
        db.flush()  # Get the ID without committing

        total_amount = 0

        # Create sale items and update inventory
        for item_data in sale_in.items:
            # Calculate total price for this item
            item_total = item_data.quantity * item_data.unit_price
            total_amount += item_total

            # Create sale item
            db_item = SaleItem(
                sale_id=db_sale.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_total
            )
            db.add(db_item)

            # Update inventory (decrease)
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item_data.product_id
            ).first()

            if inventory:
                inventory.quantity -= item_data.quantity
                inventory.last_updated = datetime.now()

            # Record inventory movement
            movement = InventoryMovement(
                product_id=item_data.product_id,
                movement_type="out",
                quantity=-item_data.quantity,  # Negative for outgoing
                reference_type="sale",
                reference_id=db_sale.id,
                reason=f"销售订单 {sale_number}"
            )
            db.add(movement)

        # Update sale total amount
        db_sale.total_amount = total_amount

        db.commit()
        db.refresh(db_sale)
        return db_sale

    def get_with_items(self, db: Session, id: int) -> Optional[Sale]:
        return (
            db.query(self.model)
            .options(joinedload(Sale.items).joinedload(SaleItem.product))
            .filter(Sale.id == id)
            .first()
        )

    def get_with_items_flattened(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取销售订单信息并扁平化客户和商品字段"""
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name,
                "items": []
            }
            
            # 处理订单项
            for item in sale.items:
                item_dict = {
                    "id": item.id,
                    "sale_id": item.sale_id,
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
    ) -> List[Sale]:
        return (
            db.query(self.model)
            .options(joinedload(Sale.items).joinedload(SaleItem.product))
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_with_items_flattened(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ):
        """获取销售订单列表并扁平化客户字段"""
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def update_status(
        self, db: Session, *, db_obj: Sale, status: str
    ) -> Sale:
        db_obj.status = status
        db_obj.updated_at = datetime.now()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_customer(
        self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        return (
            db.query(self.model)
            .filter(Sale.customer_id == customer_id)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_customer_flattened(
        self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100
    ):
        """根据客户获取销售订单列表并扁平化客户字段"""
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(Sale.customer_id == customer_id)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        return (
            db.query(self.model)
            .filter(Sale.status == status)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status_flattened(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ):
        """根据状态获取销售订单列表并扁平化客户字段"""
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(Sale.status == status)
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def search_sales(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        return (
            db.query(self.model)
            .join(Sale.customer)
            .filter(
                or_(
                    Sale.sale_number.contains(query),
                    Customer.name.contains(query)
                )
            )
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_sales_flattened(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ):
        """搜索销售订单并扁平化客户字段"""
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(
                or_(
                    Sale.sale_number.contains(query),
                    Customer.name.contains(query)
                )
            )
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results

    def get_daily_sales(
        self, db: Session, *, date: datetime, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return (
            db.query(self.model)
            .filter(
                and_(
                    Sale.sale_date >= start_date,
                    Sale.sale_date <= end_date
                )
            )
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_daily_sales_flattened(
        self, db: Session, *, date: datetime, skip: int = 0, limit: int = 100
    ):
        """获取指定日期的销售订单并扁平化客户字段"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        results = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(
                and_(
                    Sale.sale_date >= start_date,
                    Sale.sale_date <= end_date
                )
            )
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        flattened_results = []
        for sale, customer in results:
            # 将销售订单和客户信息合并为扁平结构
            flattened_item = {
                "id": sale.id,
                "customer_id": sale.customer_id,
                "user_id": sale.user_id,
                "sale_number": sale.sale_number,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0,
                "status": sale.status,
                "created_at": sale.created_at.isoformat() if sale.created_at else None,
                "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
                "customer_name": customer.name
            }
            flattened_results.append(flattened_item)
        
        return flattened_results


# Create a singleton instance
sale = SaleCRUD(Sale)