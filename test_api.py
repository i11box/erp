#!/usr/bin/env python3
"""
API测试脚本
测试已完成的供应商、客户和商品管理API
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
            return True
        else:
            print("❌ 服务器健康检查失败")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        return False

def test_suppliers_api():
    """测试供应商API"""
    print("\n=== 测试供应商API ===")

    # 获取供应商列表
    response = requests.get(f"{BASE_URL}/api/suppliers/")
    if response.status_code == 200:
        suppliers = response.json()
        print(f"✅ 获取供应商列表成功，共 {len(suppliers)} 个供应商")

        if suppliers:
            supplier_id = suppliers[0]['id']

            # 获取单个供应商
            response = requests.get(f"{BASE_URL}/api/suppliers/{supplier_id}")
            if response.status_code == 200:
                print(f"✅ 获取供应商详情成功: {suppliers[0]['name']}")

            # 搜索供应商
            response = requests.get(f"{BASE_URL}/api/suppliers/?search=科技")
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ 搜索供应商成功，找到 {len(search_results)} 个结果")
    else:
        print("❌ 获取供应商列表失败")
        return False

    return True

def test_customers_api():
    """测试客户API"""
    print("\n=== 测试客户API ===")

    # 获取客户列表
    response = requests.get(f"{BASE_URL}/api/customers/")
    if response.status_code == 200:
        customers = response.json()
        print(f"✅ 获取客户列表成功，共 {len(customers)} 个客户")

        if customers:
            customer_id = customers[0]['id']

            # 获取单个客户
            response = requests.get(f"{BASE_URL}/api/customers/{customer_id}")
            if response.status_code == 200:
                print(f"✅ 获取客户详情成功: {customers[0]['name']}")

            # 搜索客户
            response = requests.get(f"{BASE_URL}/api/customers/?search=贸易")
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ 搜索客户成功，找到 {len(search_results)} 个结果")
    else:
        print("❌ 获取客户列表失败")
        return False

    return True

def test_products_api():
    """测试商品API"""
    print("\n=== 测试商品API ===")

    # 获取商品列表
    response = requests.get(f"{BASE_URL}/api/products/")
    if response.status_code == 200:
        products = response.json()
        print(f"✅ 获取商品列表成功，共 {len(products)} 个商品")

        if products:
            product_id = products[0]['id']

            # 获取单个商品
            response = requests.get(f"{BASE_URL}/api/products/{product_id}")
            if response.status_code == 200:
                product = response.json()
                print(f"✅ 获取商品详情成功: {product['name']} (成本价: {product['cost_price']})")

            # 获取包含库存信息的商品列表
            response = requests.get(f"{BASE_URL}/api/products/?include_inventory=true")
            if response.status_code == 200:
                products_with_inventory = response.json()
                print(f"✅ 获取包含库存信息的商品列表成功")
                if products_with_inventory:
                    print(f"   示例: {products_with_inventory[0]['name']}")

            # 获取库存不足的商品
            response = requests.get(f"{BASE_URL}/api/products/low-stock")
            if response.status_code == 200:
                low_stock_products = response.json()
                print(f"✅ 获取库存不足商品成功，共 {len(low_stock_products)} 个")

            # 搜索商品
            response = requests.get(f"{BASE_URL}/api/products/?search=笔记本")
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ 搜索商品成功，找到 {len(search_results)} 个结果")
    else:
        print("❌ 获取商品列表失败")
        return False

    return True

def test_create_data():
    """测试创建数据"""
    print("\n=== 测试创建数据 ===")

    # 创建新供应商
    supplier_data = {
        "name": "测试供应商公司",
        "contact_person": "测试联系人",
        "phone": "13800138999",
        "email": "test@example.com",
        "address": "测试地址"
    }

    response = requests.post(f"{BASE_URL}/api/suppliers/", json=supplier_data)
    if response.status_code == 200:
        new_supplier = response.json()
        print(f"✅ 创建供应商成功: {new_supplier['name']} (ID: {new_supplier['id']})")
        supplier_id = new_supplier['id']
    else:
        print(f"❌ 创建供应商失败: {response.text}")
        return False

    # 创建新客户
    customer_data = {
        "name": "测试客户公司",
        "contact_person": "测试客户联系人",
        "phone": "13800138888",
        "email": "customer@example.com",
        "address": "客户测试地址"
    }

    response = requests.post(f"{BASE_URL}/api/customers/", json=customer_data)
    if response.status_code == 200:
        new_customer = response.json()
        print(f"✅ 创建客户成功: {new_customer['name']} (ID: {new_customer['id']})")
        customer_id = new_customer['id']
    else:
        print(f"❌ 创建客户失败: {response.text}")
        return False

    # 创建新商品
    product_data = {
        "name": "测试商品",
        "sku": "TEST-001",
        "description": "这是一个测试商品",
        "unit": "个",
        "cost_price": 100.00,
        "selling_price": 150.00,
        "reorder_level": 10
    }

    response = requests.post(f"{BASE_URL}/api/products/", json=product_data)
    if response.status_code == 200:
        new_product = response.json()
        print(f"✅ 创建商品成功: {new_product['name']} (ID: {new_product['id']})")
        product_id = new_product['id']
    else:
        print(f"❌ 创建商品失败: {response.text}")
        return False

    return True

def main():
    """主函数"""
    print("=== ERP系统API测试 ===")
    print()

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)

    # 测试健康检查
    if not test_health():
        return

    # 测试各API模块
    success_count = 0

    if test_suppliers_api():
        success_count += 1

    if test_customers_api():
        success_count += 1

    if test_products_api():
        success_count += 1

    if test_create_data():
        success_count += 1

    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {success_count}/4")

    if success_count == 4:
        print("🎉 所有API测试通过！")
        print("\n可以使用以下URL访问API文档:")
        print("- Swagger UI: http://localhost:8000/docs")
        print("- ReDoc: http://localhost:8000/redoc")
    else:
        print("❌ 部分测试失败，请检查服务器状态")

if __name__ == "__main__":
    main()