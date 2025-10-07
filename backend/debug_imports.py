#!/usr/bin/env python3

import sys
import os

print("=== 调试导入问题 ===")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}...")

# 测试基础导入
print("\n1. 测试基础模块导入...")
try:
    import fastapi
    print("✅ FastAPI 导入成功")
except Exception as e:
    print(f"❌ FastAPI 导入失败: {e}")

try:
    import sqlalchemy
    print("✅ SQLAlchemy 导入成功")
except Exception as e:
    print(f"❌ SQLAlchemy 导入失败: {e}")

# 测试配置文件
print("\n2. 测试配置文件...")
try:
    from app.config import settings
    print("✅ 配置文件导入成功")
    print(f"   API_V1_STR: {settings.API_V1_STR}")
    print(f"   secret_key: {settings.secret_key[:10]}...")
except Exception as e:
    print(f"❌ 配置文件导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试数据库
print("\n3. 测试数据库...")
try:
    from app.database import SessionLocal
    print("✅ 数据库模块导入成功")
except Exception as e:
    print(f"❌ 数据库导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试安全模块
print("\n4. 测试安全模块...")
try:
    from app.core.security import verify_token
    print("✅ 安全模块导入成功")
except Exception as e:
    print(f"❌ 安全模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试CRUD模块
print("\n5. 测试CRUD模块...")
try:
    from app.crud import user
    print("✅ CRUD模块导入成功")
except Exception as e:
    print(f"❌ CRUD模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试deps模块
print("\n6. 测试deps模块...")
try:
    from app.api.deps import get_db
    print("✅ deps模块导入成功")
except Exception as e:
    print(f"❌ deps模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试auth模块
print("\n7. 测试auth模块...")
try:
    from app.api.auth import router
    print("✅ auth模块导入成功")
except Exception as e:
    print(f"❌ auth模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试main模块
print("\n8. 测试main模块...")
try:
    from app.main import app
    print("✅ main模块导入成功")
    print("   FastAPI应用已加载")
except Exception as e:
    print(f"❌ main模块导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 调试完成 ===")