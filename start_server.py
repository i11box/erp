#!/usr/bin/env python3
"""
ERP系统启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        sys.exit(1)
    print(f"Python版本: {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    print("检查Python依赖...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 核心依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

def setup_database():
    """设置数据库"""
    print("设置数据库...")

    # 检查数据库文件是否存在
    db_file = Path("backend/inventory.db")
    if not db_file.exists():
        print("创建数据库表...")
        result = subprocess.run([
            sys.executable, "create_models.py"
        ], cwd="backend")
        if result.returncode != 0:
            print("❌ 创建数据库表失败")
            return False

        print("初始化示例数据...")
        result = subprocess.run([
            sys.executable, "init_db.py"
        ], cwd="backend")
        if result.returncode != 0:
            print("❌ 初始化数据失败")
            return False

    print("✅ 数据库设置完成")
    return True

def start_server():
    """启动FastAPI服务器"""
    print("启动FastAPI服务器...")
    print("服务器将在 http://localhost:8000 启动")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务器")

    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], cwd="backend")
    except KeyboardInterrupt:
        print("\n服务器已停止")

def main():
    """主函数"""
    print("=== ERP进销存管理系统 ===")
    print()

    # 检查Python版本
    check_python_version()

    # 检查依赖
    check_dependencies()

    # 设置数据库
    if not setup_database():
        print("❌ 数据库设置失败，退出")
        sys.exit(1)

    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()