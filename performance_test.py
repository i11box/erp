#!/usr/bin/env python3
"""
ERP进销存管理系统 - 性能测试脚本
使用Locust进行简单的API性能测试
"""

from locust import HttpUser, task, between
import random
import json

class ERPUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时执行登录"""
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            print("登录失败，无法进行性能测试")
            self.token = None
            self.headers = {}

    @task(3)
    def view_dashboard(self):
        """查看仪表板"""
        if self.token:
            self.client.get("/api/analytics/dashboard", headers=self.headers)

    @task(2)
    def view_products(self):
        """查看商品列表"""
        if self.token:
            self.client.get("/api/products/", headers=self.headers)

    @task(2)
    def view_customers(self):
        """查看客户列表"""
        if self.token:
            self.client.get("/api/customers/", headers=self.headers)

    @task(2)
    def view_suppliers(self):
        """查看供应商列表"""
        if self.token:
            self.client.get("/api/suppliers/", headers=self.headers)

    @task(2)
    def view_inventory(self):
        """查看库存列表"""
        if self.token:
            self.client.get("/api/inventory/", headers=self.headers)

    @task(1)
    def view_purchases(self):
        """查看采购订单"""
        if self.token:
            self.client.get("/api/purchases/", headers=self.headers)

    @task(1)
    def view_sales(self):
        """查看销售订单"""
        if self.token:
            self.client.get("/api/sales/", headers=self.headers)

    @task(1)
    def get_inventory_summary(self):
        """获取库存汇总"""
        if self.token:
            self.client.get("/api/inventory/summary", headers=self.headers)

    @task(1)
    def get_sales_report(self):
        """获取销售报表"""
        if self.token:
            self.client.get("/api/analytics/sales-report", headers=self.headers)

class AdminUser(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        """管理员用户登录"""
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            print("管理员登录失败")
            self.token = None
            self.headers = {}

    @task(3)
    def view_analytics(self):
        """查看各种分析报表"""
        if self.token:
            endpoints = [
                "/api/analytics/dashboard",
                "/api/analytics/sales-report",
                "/api/analytics/purchase-report",
                "/api/analytics/top-products",
                "/api/analytics/top-customers",
                "/api/analytics/profit-analysis"
            ]
            endpoint = random.choice(endpoints)
            self.client.get(endpoint, headers=self.headers)

    @task(2)
    def view_inventory_management(self):
        """库存管理相关操作"""
        if self.token:
            endpoints = [
                "/api/inventory/",
                "/api/inventory/low-stock",
                "/api/inventory/summary",
                "/api/inventory/movements/"
            ]
            endpoint = random.choice(endpoints)
            self.client.get(endpoint, headers=self.headers)

    @task(1)
    def create_test_data(self):
        """创建测试数据（只读取，不实际创建）"""
        if self.token:
            # 模拟获取创建表单所需的数据
            self.client.get("/api/products/", headers=self.headers)
            self.client.get("/api/customers/", headers=self.headers)
            self.client.get("/api/suppliers/", headers=self.headers)

if __name__ == "__main__":
    print("ERP进销存管理系统 - 性能测试")
    print("=" * 50)
    print("使用方法:")
    print("1. 安装Locust: pip install locust")
    print("2. 启动后端服务器")
    print("3. 运行测试: locust -f performance_test.py")
    print("4. 访问 http://localhost:8089 进行Web界面测试")
    print("")
    print("测试场景:")
    print("- 普通用户: 主要查看各种列表和仪表板")
    print("- 管理员: 查看分析报表和库存管理")
    print("")
    print("建议测试参数:")
    print("- 用户数量: 10-50")
    print(-" 每秒用户增长: 1-2")
    print("- 测试时间: 5-10分钟")