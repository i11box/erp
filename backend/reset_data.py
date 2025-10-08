#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, Supplier, Customer, Product, Inventory, Purchase, Sale, PurchaseItem, SaleItem

def reset_all_data():
    """删除所有数据并重新创建"""
    print("开始重置数据...")

    db = SessionLocal()
    try:
        # 按依赖关系删除数据
        print("删除订单项...")
        db.query(PurchaseItem).delete()
        db.query(SaleItem).delete()

        print("删除订单...")
        db.query(Purchase).delete()
        db.query(Sale).delete()

        print("删除库存...")
        db.query(Inventory).delete()

        print("删除商品...")
        db.query(Product).delete()

        print("删除客户...")
        db.query(Customer).delete()

        print("删除供应商...")
        db.query(Supplier).delete()

        print("删除用户...")
        db.query(User).delete()

        db.commit()
        print("所有数据已删除")

        # 重新创建表（确保结构正确）
        print("重新创建表结构...")
        Base.metadata.create_all(bind=engine)

        print("数据库重置完成！")

    except Exception as e:
        print(f"重置失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_all_data()