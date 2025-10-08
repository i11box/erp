#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, Supplier, Customer, Product, Inventory, Purchase, Sale
from app.core.auth import get_password_hash

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(User).first():
            print("数据库已有数据，跳过初始化")
            return

        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)

        # 创建普通用户
        user = User(
            username="user",
            email="user@example.com",
            password_hash=get_password_hash("user123"),
            role="user",
            is_active=True
        )
        db.add(user)

        # 创建示例供应商
        suppliers = [
            Supplier(
                name="科技有限公司",
                contact_person="张经理",
                phone="13800138001",
                email="zhang@tech.com",
                address="北京市朝阳区科技园"
            ),
            Supplier(
                name="电子产品批发商",
                contact_person="李总",
                phone="13800138002",
                email="li@electronics.com",
                address="上海市浦东新区商务区"
            )
        ]

        for supplier in suppliers:
            db.add(supplier)

        # 创建示例客户
        customers = [
            Customer(
                name="ABC贸易公司",
                contact_person="王经理",
                phone="13800138003",
                email="wang@abc.com",
                address="深圳市南山区创业园"
            ),
            Customer(
                name="XYZ零售店",
                contact_person="赵老板",
                phone="13800138004",
                email="zhao@xyz.com",
                address="广州市天河区商业街"
            )
        ]

        for customer in customers:
            db.add(customer)

        # 创建示例商品
        products = [
            Product(
                name="笔记本电脑",
                sku="LAPTOP-001",
                description="高性能商务笔记本",
                unit="台",
                cost_price=3000.00,
                selling_price=4500.00,
                reorder_level=10
            ),
            Product(
                name="无线鼠标",
                sku="MOUSE-001",
                description="无线蓝牙鼠标",
                unit="个",
                cost_price=50.00,
                selling_price=80.00,
                reorder_level=50
            ),
            Product(
                name="机械键盘",
                sku="KEYBOARD-001",
                description="机械轴键盘",
                unit="个",
                cost_price=200.00,
                selling_price=350.00,
                reorder_level=20
            ),
            Product(
                name="显示器",
                sku="MONITOR-001",
                description="27寸4K显示器",
                unit="台",
                cost_price=1500.00,
                selling_price=2200.00,
                reorder_level=15
            )
        ]

        for product in products:
            db.add(product)

        # 提交商品数据以便获取ID
        db.commit()

        # 为每个商品创建库存记录
        for product in products:
            inventory = Inventory(
                product_id=product.id,
                quantity=100,  # 初始库存
                avg_cost=product.cost_price
            )
            db.add(inventory)

        # 提交所有更改
        db.commit()
        print("示例数据初始化完成")

    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()