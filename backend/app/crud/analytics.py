from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, extract, cast, String
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.supplier import Supplier


class AnalyticsCRUD:
    def get_dashboard_data(self, db: Session) -> Dict[str, Any]:
        """获取仪表板数据"""
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        # 今日销售统计
        today_sales = (
            db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(func.date(Sale.created_at) == today)
            .scalar()
        )

        # 本月销售统计
        month_sales = (
            db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(
                and_(
                    func.date(Sale.created_at) >= start_of_month,
                    func.date(Sale.created_at) <= today
                )
            )
            .scalar()
        )

        # 本年销售统计
        year_sales = (
            db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(
                and_(
                    func.date(Sale.created_at) >= start_of_year,
                    func.date(Sale.created_at) <= today
                )
            )
            .scalar()
        )

        # 今日采购统计
        today_purchases = (
            db.query(func.coalesce(func.sum(Purchase.total_amount), 0))
            .filter(func.date(Purchase.created_at) == today)
            .scalar()
        )

        # 本月采购统计
        month_purchases = (
            db.query(func.coalesce(func.sum(Purchase.total_amount), 0))
            .filter(
                and_(
                    func.date(Purchase.created_at) >= start_of_month,
                    func.date(Purchase.created_at) <= today
                )
            )
            .scalar()
        )

        # 总商品数
        total_products = db.query(Product).count()

        # 低库存商品数
        low_stock_products = (
            db.query(Inventory)
            .join(Inventory.product)
            .filter(Inventory.quantity <= Product.reorder_level)
            .count()
        )

        # 缺货商品数
        out_of_stock_products = (
            db.query(Inventory)
            .filter(Inventory.quantity == 0)
            .count()
        )

        # 总客户数
        total_customers = db.query(Customer).count()

        # 总供应商数
        total_suppliers = db.query(Supplier).count()

        # 库存总价值
        inventory_value = (
            db.query(func.coalesce(func.sum(Inventory.quantity * Inventory.avg_cost), 0))
            .scalar()
        )

        return {
            "sales": {
                "today": float(today_sales),
                "month": float(month_sales),
                "year": float(year_sales)
            },
            "purchases": {
                "today": float(today_purchases),
                "month": float(month_purchases)
            },
            "inventory": {
                "total_products": total_products,
                "low_stock_products": low_stock_products,
                "out_of_stock_products": out_of_stock_products,
                "total_value": float(inventory_value)
            },
            "counts": {
                "customers": total_customers,
                "suppliers": total_suppliers
            }
        }

    def get_sales_report(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """获取销售报表"""
        if group_by == "day":
            date_col = cast(func.date(Sale.sale_date), String)
        elif group_by == "week":
            date_col = cast(func.date_trunc('week', Sale.sale_date), String)
        elif group_by == "month":
            date_col = cast(func.date_trunc('month', Sale.sale_date), String)
        else:
            date_col = cast(func.date(Sale.sale_date), String)

        sales_data = (
            db.query(
                date_col.label('period'),
                func.count(Sale.id).label('order_count'),
                func.sum(Sale.total_amount).label('total_amount'),
                func.avg(Sale.total_amount).label('avg_amount')
            )
            .filter(
                and_(
                    Sale.sale_date >= start_date,
                    Sale.sale_date <= end_date,
                    Sale.status == "completed"
                )
            )
            .group_by(date_col)
            .order_by(date_col)
            .all()
        )

        return [
            {
                "period": item.period,
                "order_count": item.order_count,
                "total_amount": float(item.total_amount or 0),
                "avg_amount": float(item.avg_amount or 0)
            }
            for item in sales_data
        ]

    def get_purchase_report(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """获取采购报表"""
        if group_by == "day":
            date_format = func.date(Purchase.purchase_date)
        elif group_by == "week":
            date_format = func.date_trunc('week', Purchase.purchase_date)
        elif group_by == "month":
            date_format = func.date_trunc('month', Purchase.purchase_date)
        else:
            date_format = func.date(Purchase.purchase_date)

        purchase_data = (
            db.query(
                date_format.label('period'),
                func.count(Purchase.id).label('order_count'),
                func.sum(Purchase.total_amount).label('total_amount'),
                func.avg(Purchase.total_amount).label('avg_amount')
            )
            .filter(
                and_(
                    Purchase.purchase_date >= start_date,
                    Purchase.purchase_date <= end_date,
                    Purchase.status == "completed"
                )
            )
            .group_by(date_format)
            .order_by(date_format)
            .all()
        )

        return [
            {
                "period": str(item.period),
                "order_count": item.order_count,
                "total_amount": float(item.total_amount or 0),
                "avg_amount": float(item.avg_amount or 0)
            }
            for item in purchase_data
        ]

    def get_top_selling_products(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取热销商品排行"""
        top_products = (
            db.query(
                Product.id,
                Product.name,
                Product.sku,
                func.sum(SaleItem.quantity).label('total_quantity'),
                func.sum(SaleItem.total_price).label('total_revenue')
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at <= end_date,
                    Sale.status == "completed"
                )
            )
            .group_by(Product.id, Product.name, Product.sku)
            .order_by(desc(func.sum(SaleItem.quantity)))
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": item.id,
                "product_name": item.name,
                "product_sku": item.sku,
                "total_quantity": item.total_quantity,
                "total_revenue": float(item.total_revenue or 0)
            }
            for item in top_products
        ]

    def get_top_customers(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取重要客户排行"""
        top_customers = (
            db.query(
                Customer.id,
                Customer.name,
                Customer.contact_person,
                func.sum(Sale.total_amount).label('total_spent'),
                func.count(Sale.id).label('order_count')
            )
            .join(Sale, Customer.id == Sale.customer_id)
            .filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at <= end_date,
                    Sale.status == "completed"
                )
            )
            .group_by(Customer.id, Customer.name, Customer.contact_person)
            .order_by(desc(func.sum(Sale.total_amount)))
            .limit(limit)
            .all()
        )

        return [
            {
                "customer_id": item.id,
                "customer_name": item.name,
                "contact_person": item.contact_person,
                "total_spent": float(item.total_spent or 0),
                "order_count": item.order_count
            }
            for item in top_customers
        ]

    def get_profit_analysis(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """获取利润分析"""
        # 销售收入
        sales_revenue = (
            db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at <= end_date,
                    Sale.status == "completed"
                )
            )
            .scalar()
        )

        # 销售成本 (根据商品的成本价计算)
        sales_cost = (
            db.query(
                func.coalesce(
                    func.sum(SaleItem.quantity * Product.cost_price), 0
                )
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Product, SaleItem.product_id == Product.id)
            .filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at <= end_date,
                    Sale.status == "completed"
                )
            )
            .scalar()
        )

        # 采购成本
        purchase_cost = (
            db.query(func.coalesce(func.sum(Purchase.total_amount), 0))
            .filter(
                and_(
                    Purchase.created_at >= start_date,
                    Purchase.created_at <= end_date,
                    Purchase.status == "completed"
                )
            )
            .scalar()
        )

        # 计算利润
        gross_profit = float(sales_revenue or 0) - float(sales_cost or 0)
        net_profit = gross_profit - float(purchase_cost or 0)

        return {
            "sales_revenue": float(sales_revenue or 0),
            "sales_cost": float(sales_cost or 0),
            "purchase_cost": float(purchase_cost or 0),
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "gross_margin": (gross_profit / float(sales_revenue or 1)) * 100 if sales_revenue else 0
        }

    def get_inventory_turnover(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """获取库存周转率分析"""
        # 计算销售数量
        sales_by_product = (
            db.query(
                Product.id,
                Product.name,
                func.sum(SaleItem.quantity).label('total_sold')
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at <= end_date,
                    Sale.status == "completed"
                )
            )
            .group_by(Product.id, Product.name)
            .subquery()
        )

        # 获取库存信息
        inventory_turnover = (
            db.query(
                Product.id,
                Product.name,
                Inventory.quantity.label('current_stock'),
                sales_by_product.c.total_sold.label('total_sold')
            )
            .join(Inventory, Product.id == Inventory.product_id)
            .outerjoin(sales_by_product, Product.id == sales_by_product.c.id)
            .filter(Inventory.quantity > 0)
            .all()
        )

        result = []
        for item in inventory_turnover:
            total_sold = item.total_sold or 0
            current_stock = item.quantity or 1
            avg_stock = (current_stock + (current_stock + total_sold)) / 2
            turnover_rate = total_sold / avg_stock if avg_stock > 0 else 0

            result.append({
                "product_id": item.id,
                "product_name": item.name,
                "current_stock": current_stock,
                "total_sold": total_sold,
                "turnover_rate": round(turnover_rate, 2)
            })

        return sorted(result, key=lambda x: x["turnover_rate"], reverse=True)


# Create a singleton instance
analytics = AnalyticsCRUD()