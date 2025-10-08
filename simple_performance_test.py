#!/usr/bin/env python3
"""
ERP进销存管理系统 - 简单性能测试脚本
不依赖Locust的轻量级性能测试
"""

import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class ERPPerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.results = []

    def login(self):
        """登录获取token"""
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
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
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

    def test_endpoint(self, endpoint, description=""):
        """测试单个端点"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒

            result = {
                "endpoint": endpoint,
                "description": description,
                "response_time": response_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }

            return result
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            result = {
                "endpoint": endpoint,
                "description": description,
                "response_time": response_time,
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
            return result

    def run_single_user_test(self):
        """单用户测试所有端点"""
        print("\n🔄 开始单用户性能测试...")

        endpoints = [
            ("/api/analytics/dashboard", "仪表板数据"),
            ("/api/products/", "商品列表"),
            ("/api/customers/", "客户列表"),
            ("/api/suppliers/", "供应商列表"),
            ("/api/inventory/", "库存列表"),
            ("/api/purchases/", "采购订单"),
            ("/api/sales/", "销售订单"),
            ("/api/inventory/summary", "库存汇总"),
            ("/api/analytics/sales-report", "销售报表"),
            ("/api/analytics/top-products", "热销商品"),
        ]

        results = []
        for endpoint, description in endpoints:
            result = self.test_endpoint(endpoint, description)
            results.append(result)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {description}: {result['response_time']:.2f}ms")

        return results

    def run_concurrent_test(self, num_users=10, num_requests=5):
        """并发用户测试"""
        print(f"\n🚀 开始并发测试: {num_users}个用户，每用户{num_requests}次请求")

        endpoints = [
            "/api/analytics/dashboard",
            "/api/products/",
            "/api/customers/",
            "/api/inventory/"
        ]

        all_results = []

        def user_worker(user_id):
            """单个用户的工作线程"""
            user_results = []
            for i in range(num_requests):
                endpoint = endpoints[i % len(endpoints)]
                result = self.test_endpoint(endpoint, f"用户{user_id}-请求{i}")
                user_results.append(result)
                time.sleep(0.1)  # 请求间隔
            return user_results

        # 使用线程池执行并发测试
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_worker, i) for i in range(num_users)]

            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"❌ 用户测试异常: {e}")

        return all_results

    def analyze_results(self, results, test_name=""):
        """分析测试结果"""
        if not results:
            print("❌ 没有测试结果可分析")
            return

        print(f"\n📊 {test_name} - 性能测试结果分析")
        print("=" * 50)

        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]

        success_rate = len(successful_results) / len(results) * 100
        print(f"总请求数: {len(results)}")
        print(f"成功请求: {len(successful_results)}")
        print(f"失败请求: {len(failed_results)}")
        print(f"成功率: {success_rate:.2f}%")

        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            print(f"平均响应时间: {statistics.mean(response_times):.2f}ms")
            print(f"最快响应时间: {min(response_times):.2f}ms")
            print(f"最慢响应时间: {max(response_times):.2f}ms")
            print(f"中位数响应时间: {statistics.median(response_times):.2f}ms")

            # 响应时间分布
            fast_requests = len([t for t in response_times if t < 200])
            medium_requests = len([t for t in response_times if 200 <= t < 500])
            slow_requests = len([t for t in response_times if t >= 500])

            print(f"\n响应时间分布:")
            print(f"  快速(<200ms): {fast_requests} ({fast_requests/len(response_times)*100:.1f}%)")
            print(f"  中等(200-500ms): {medium_requests} ({medium_requests/len(response_times)*100:.1f}%)")
            print(f"  慢速(>=500ms): {slow_requests} ({slow_requests/len(response_times)*100:.1f}%)")

        if failed_results:
            print(f"\n失败请求详情:")
            for result in failed_results[:5]:  # 只显示前5个失败请求
                print(f"  {result['endpoint']}: {result.get('error', 'Unknown error')}")

    def save_results(self, results, filename="performance_results.json"):
        """保存测试结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 测试结果已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")

    def run_full_test(self):
        """运行完整测试套件"""
        print("🎯 ERP进销存管理系统 - 性能测试")
        print("=" * 50)

        # 登录
        if not self.login():
            return

        # 单用户测试
        single_results = self.run_single_user_test()
        self.analyze_results(single_results, "单用户测试")

        # 并发测试
        concurrent_results = self.run_concurrent_test(num_users=10, num_requests=3)
        self.analyze_results(concurrent_results, "并发测试")

        # 保存结果
        all_results = {
            "single_user": single_results,
            "concurrent": concurrent_results,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_results(all_results)

        print("\n🎉 性能测试完成！")

if __name__ == "__main__":
    # 检查后端服务是否运行
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ 后端服务未正常运行，请先启动后端服务")
            exit(1)
    except:
        print("❌ 无法连接到后端服务，请确保后端服务在 http://localhost:8000 运行")
        exit(1)

    # 运行性能测试
    tester = ERPPerformanceTester()
    tester.run_full_test()