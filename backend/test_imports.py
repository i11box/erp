#!/usr/bin/env python3

"""测试所有模块是否可以正确导入"""

def test_imports():
    """测试所有关键模块的导入"""
    try:
        # 测试核心模块
        print("Testing core modules...")
        from app.core import security
        from app.config import settings
        from app.database import SessionLocal
        print("✅ Core modules imported successfully")

        # 测试数据模型
        print("Testing models...")
        from app.models.user import User
        from app.models.supplier import Supplier
        from app.models.customer import Customer
        from app.models.product import Product
        from app.models.inventory import Inventory
        from app.models.purchase import Purchase
        from app.models.sale import Sale
        print("✅ Models imported successfully")

        # 测试CRUD模块
        print("Testing CRUD modules...")
        from app.crud import user
        from app.crud import supplier
        from app.crud import customer
        from app.crud import product
        from app.crud import purchase
        from app.crud import sale
        from app.crud import inventory
        from app.crud import analytics
        print("✅ CRUD modules imported successfully")

        # 测试API模块
        print("Testing API modules...")
        from app.api import deps
        from app.api import auth
        from app.api import suppliers
        from app.api import customers
        from app.api import products
        from app.api import purchases
        from app.api import sales
        from app.api import inventory
        from app.api import analytics
        print("✅ API modules imported successfully")

        # 测试schemas
        print("Testing schemas...")
        from app.schemas import user
        from app.schemas import supplier
        from app.schemas import customer
        from app.schemas import product
        from app.schemas import purchase
        from app.schemas import sale
        from app.schemas import inventory
        print("✅ Schemas imported successfully")

        print("\n🎉 All modules imported successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)