#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Supplier, Customer, Product, Inventory, Purchase, Sale

def test_data_integrity():
    """测试数据完整性"""
    db = SessionLocal()

    try:
        print("=== 数据完整性测试 ===")

        # 测试用户数据
        user_count = db.query(User).count()
        print(f"用户数量: {user_count}")
        if user_count == 0:
            print("❌ 错误: 没有用户数据")
        else:
            print("✅ 用户数据正常")

        # 测试供应商数据
        supplier_count = db.query(Supplier).count()
        print(f"供应商数量: {supplier_count}")
        if supplier_count == 0:
            print("❌ 错误: 没有供应商数据")
        else:
            print("✅ 供应商数据正常")

        # 测试客户数据
        customer_count = db.query(Customer).count()
        print(f"客户数量: {customer_count}")
        if customer_count == 0:
            print("❌ 错误: 没有客户数据")
        else:
            print("✅ 客户数据正常")

        # 测试商品数据
        product_count = db.query(Product).count()
        print(f"商品数量: {product_count}")
        if product_count == 0:
            print("❌ 错误: 没有商品数据")
        else:
            print("✅ 商品数据正常")

        # 测试库存数据
        inventory_count = db.query(Inventory).count()
        print(f"库存记录数量: {inventory_count}")
        if inventory_count == 0:
            print("❌ 错误: 没有库存数据")
        else:
            print("✅ 库存数据正常")

        # 测试采购订单数据
        purchase_count = db.query(Purchase).count()
        print(f"采购订单数量: {purchase_count}")
        if purchase_count == 0:
            print("⚠️  警告: 没有采购订单数据")
        else:
            print("✅ 采购订单数据正常")

        # 测试销售订单数据
        sale_count = db.query(Sale).count()
        print(f"销售订单数量: {sale_count}")
        if sale_count == 0:
            print("⚠️  警告: 没有销售订单数据")
        else:
            print("✅ 销售订单数据正常")

        # 显示具体数据样本
        print("\n=== 数据样本 ===")

        # 显示用户样本
        users = db.query(User).limit(3).all()
        for user in users:
            print(f"用户: {user.username} ({user.role})")

        # 显示商品样本
        products = db.query(Product).limit(5).all()
        for product in products:
            inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
            stock = inventory.quantity if inventory else 0
            print(f"商品: {product.name} - 库存: {stock} {product.unit}")

        print("\n=== 测试完成 ===")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_data_integrity()