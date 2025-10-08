#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import engine, SessionLocal, Base
from app.models import User, Supplier, Customer, Product, Inventory, Purchase, Sale, PurchaseItem, SaleItem
from app.core.auth import get_password_hash

def create_test_data():
    """创建大量测试数据"""
    print("脚本开始执行...")

    # 确保所有表都已创建
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    # 创建数据库会话
    print("正在创建数据库会话...")
    db = SessionLocal()
    print("数据库会话创建成功")

    try:
        print("开始创建测试数据...")

        # 直接删除所有现有数据
        print("删除所有现有数据...")
        db.query(PurchaseItem).delete()
        db.query(SaleItem).delete()
        db.query(Purchase).delete()
        db.query(Sale).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Customer).delete()
        db.query(Supplier).delete()
        db.query(User).delete()
        db.commit()
        print("所有数据已清空")
        
        # 创建更多用户
        users = [
            User(
                username="manager1",
                email="manager1@example.com",
                password_hash=get_password_hash("manager123"),
                role="manager",
                is_active=True
            ),
            User(
                username="sales1",
                email="sales1@example.com",
                password_hash=get_password_hash("sales123"),
                role="sales",
                is_active=True
            ),
            User(
                username="purchase1",
                email="purchase1@example.com",
                password_hash=get_password_hash("purchase123"),
                role="purchase",
                is_active=True
            )
        ]

        for user in users:
            db.add(user)

        # 创建更多供应商
        suppliers_data = [
            ("华为技术有限公司", "陈经理", "13900001001", "chen@huawei.com", "深圳市龙岗区华为基地"),
            ("小米科技有限责任公司", "刘总", "13900001002", "liu@xiaomi.com", "北京市海淀区小米科技园"),
            ("联想集团有限公司", "张经理", "13900001003", "zhang@lenovo.com", "北京市海淀区上地信息产业基地"),
            ("戴尔（中国）有限公司", "王总", "13900001004", "wang@dell.com", "厦门市思明区软件园二期"),
            ("惠普（中国）有限公司", "李经理", "13900001005", "li@hp.com", "北京市朝阳区惠普大厦"),
            ("苹果电脑贸易（上海）有限公司", "赵总", "13900001006", "zhao@apple.com", "上海市浦东新区苹果零售店"),
            ("华硕电脑股份有限公司", "周经理", "13900001007", "zhou@asus.com", "上海市闵行区华硕大厦"),
            ("宏碁股份有限公司", "吴总", "13900001008", "wu@acer.com", "上海市浦东新区宏碁大厦"),
            ("神舟电脑股份有限公司", "郑经理", "13900001009", "zheng@hasee.com", "深圳市南山区神舟大厦"),
            ("清华同方股份有限公司", "冯总", "13900001010", "feng@thtf.com", "北京市海淀区清华同方科技广场")
        ]

        for name, contact, phone, email, address in suppliers_data:
            supplier = Supplier(
                name=name,
                contact_person=contact,
                phone=phone,
                email=email,
                address=address
            )
            db.add(supplier)

        # 创建更多客户
        customers_data = [
            ("阿里巴巴集团控股有限公司", "马经理", "13800002001", "ma@alibaba.com", "杭州市余杭区文一西路969号"),
            ("腾讯计算机系统有限公司", "张总", "13800002002", "zhang@tencent.com", "深圳市南山区科技中一路腾讯大厦"),
            ("百度在线网络技术有限公司", "李经理", "13800002003", "li@baidu.com", "北京市海淀区上地十街10号"),
            ("京东集团股份有限公司", "刘总", "13800002004", "liu@jd.com", "北京市亦庄经济技术开发区科创十一街18号"),
            ("网易公司", "陈经理", "13800002005", "chen@163.com", "杭州市滨江区网商路399号"),
            ("新浪公司", "赵总", "13800002006", "zhao@sina.com", "北京市海淀区北四环西路58号理想国际大厦"),
            ("搜狐公司", "王经理", "13800002007", "wang@sohu.com", "北京市海淀区科学院南路2号融科资讯中心"),
            ("字节跳动科技有限公司", "周总", "13800002008", "zhou@bytedance.com", "北京市海淀区北三环西路甲18号"),
            ("美团点评", "吴经理", "13800002009", "wu@meituan.com", "北京市朝阳区望京东路6号"),
            ("滴滴出行科技有限公司", "郑总", "13800002010", "zheng@didiglobal.com", "北京市海淀区中关村软件园")
        ]

        for name, contact, phone, email, address in customers_data:
            customer = Customer(
                name=name,
                contact_person=contact,
                phone=phone,
                email=email,
                address=address
            )
            db.add(customer)

        # 创建更多商品
        products_data = [
            ("ThinkPad X1 Carbon", "LP-001", "联想超极本", "台", 6800.00, 8999.00, 5),
            ("MacBook Pro 13", "MB-013", "苹果笔记本电脑", "台", 9299.00, 11999.00, 3),
            ("Dell XPS 13", "DX-013", "戴尔超极本", "台", 7200.00, 9499.00, 4),
            ("HP EliteBook", "HE-001", "惠普商务本", "台", 5800.00, 7999.00, 6),
            ("Surface Laptop", "SL-001", "微软笔记本", "台", 6500.00, 8888.00, 4),
            ("iPad Pro 11", "IP-011", "苹果平板电脑", "台", 5299.00, 6999.00, 8),
            ("Samsung Galaxy Tab", "SG-001", "三星平板", "台", 3200.00, 4299.00, 10),
            ("AirPods Pro", "AP-001", "苹果无线耳机", "个", 1299.00, 1999.00, 20),
            ("Sony WH-1000XM4", "SN-001", "索尼降噪耳机", "个", 1899.00, 2499.00, 15),
            ("Logitech MX Master", "LM-001", "罗技大师鼠标", "个", 599.00, 799.00, 25),
            ("Razer DeathAdder", "RD-001", "雷蛇游戏鼠标", "个", 299.00, 399.00, 30),
            ("Corsair K95", "CK-001", "海盗船机械键盘", "个", 899.00, 1299.00, 12),
            ("Dell UltraSharp 27", "DU-027", "戴尔显示器", "台", 2299.00, 2999.00, 8),
            ("LG 27UK850", "LG-027", "LG 4K显示器", "台", 2899.00, 3799.00, 6),
            ("BenQ PD2700U", "BQ-027", "明基设计师显示器", "台", 3299.00, 4299.00, 5),
            ("WD My Passport", "WD-001", "西部数据移动硬盘", "个", 399.00, 599.00, 40),
            ("Samsung T7", "ST-001", "三星固态移动硬盘", "个", 599.00, 899.00, 25),
            ("SanDisk Extreme", "SD-001", "闪迪U盘", "个", 89.00, 129.00, 100),
            ("Netgear Nighthawk", "NN-001", "网件路由器", "台", 899.00, 1299.00, 15),
            ("TP-Link Deco", "TD-001", "TP-Link mesh路由器", "套", 799.00, 1199.00, 18)
        ]

        products = []
        for name, sku, desc, unit, cost, price, reorder in products_data:
            product = Product(
                name=name,
                sku=sku,
                description=desc,
                unit=unit,
                cost_price=cost,
                selling_price=price,
                reorder_level=reorder
            )
            products.append(product)
            db.add(product)

        # 提交商品数据以便获取ID
        db.commit()

        # 为每个商品创建库存记录
        inventories = []
        for product in products:
            # 随机生成库存数量
            quantity = random.randint(5, 200)
            inventory = Inventory(
                product_id=product.id,
                quantity=quantity,
                avg_cost=product.cost_price
            )
            inventories.append(inventory)
            db.add(inventory)

        db.commit()

        # 获取所有用户、供应商、客户
        all_users = db.query(User).all()
        all_suppliers = db.query(Supplier).all()
        all_customers = db.query(Customer).all()
        all_products = db.query(Product).all()
        all_inventories = db.query(Inventory).all()

        # 创建采购订单
        print("创建采购订单...")
        for i in range(30):  # 创建30个采购订单
            purchase_date = datetime.now() - timedelta(days=random.randint(1, 90))
            purchase = Purchase(
                supplier_id=random.choice(all_suppliers).id,
                user_id=random.choice(all_users).id,
                purchase_number=f"PO{datetime.now().strftime('%Y%m%d')}{i+1:03d}",
                purchase_date=purchase_date.date(),
                total_amount=0,  # 稍后计算
                status=random.choice(["pending", "completed", "cancelled"])
            )
            db.add(purchase)
            db.flush()  # 获取purchase.id

            # 为采购订单添加商品
            num_items = random.randint(1, 5)
            total_amount = 0
            for _ in range(num_items):
                product = random.choice(all_products)
                quantity = random.randint(1, 20)
                unit_price = product.cost_price * Decimal(str(random.uniform(0.9, 1.1)))
                total_price = quantity * unit_price

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    total_price=round(total_price, 2)
                )
                db.add(purchase_item)
                total_amount += total_price

                # 如果采购订单已完成，更新库存
                if purchase.status == "completed":
                    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
                    if inventory:
                        inventory.quantity += quantity

            purchase.total_amount = round(total_amount, 2)

        # 创建销售订单
        print("创建销售订单...")
        for i in range(50):  # 创建50个销售订单
            sale_date = datetime.now() - timedelta(days=random.randint(1, 60))
            sale = Sale(
                customer_id=random.choice(all_customers).id,
                user_id=random.choice(all_users).id,
                sale_number=f"SO{datetime.now().strftime('%Y%m%d')}{i+1:03d}",
                sale_date=sale_date.date(),
                total_amount=0,  # 稍后计算
                status=random.choice(["pending", "completed", "cancelled"])
            )
            db.add(sale)
            db.flush()  # 获取sale.id

            # 为销售订单添加商品
            num_items = random.randint(1, 4)
            total_amount = 0
            for _ in range(num_items):
                product = random.choice(all_products)
                quantity = random.randint(1, 10)
                unit_price = product.selling_price * Decimal(str(random.uniform(0.9, 1.1)))  # 价格有浮动
                total_price = quantity * unit_price

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    total_price=round(total_price, 2)
                )
                db.add(sale_item)
                total_amount += total_price

                # 如果销售订单已完成，更新库存
                if sale.status == "completed":
                    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
                    if inventory and inventory.quantity >= quantity:
                        inventory.quantity -= quantity

            sale.total_amount = round(total_amount, 2)

        # 提交所有更改
        db.commit()
        print("测试数据创建完成！")
        print(f"创建了 {len(users)} 个用户")
        print(f"创建了 {len(suppliers_data)} 个供应商")
        print(f"创建了 {len(customers_data)} 个客户")
        print(f"创建了 {len(products_data)} 个商品")
        print(f"创建了 30 个采购订单")
        print(f"创建了 50 个销售订单")

    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()