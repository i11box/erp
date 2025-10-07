#!/usr/bin/env python3
"""
简化的启动脚本，用于测试和快速启动
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动应用"""
    try:
        print("🚀 正在启动ERP进销存管理系统...")

        # 简化的导入测试
        print("📦 正在加载模块...")

        # 导入配置
        print("   - 配置模块...")
        from app.config import settings
        print(f"     ✅ API版本: {settings.API_V1_STR}")

        # 导入数据库
        print("   - 数据库模块...")
        from app.database import SessionLocal
        print("     ✅ 数据库连接已设置")

        # 导入FastAPI
        print("   - Web框架...")
        from fastapi import FastAPI
        print("     ✅ FastAPI已加载")

        # 创建应用
        print("🔧 正在创建应用...")
        app = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description="ERP进销存管理系统API"
        )

        print("✅ 应用创建成功!")
        print(f"📊 项目名称: {settings.PROJECT_NAME}")
        print(f"🔢 项目版本: {settings.VERSION}")
        print(f"📡 API前缀: {settings.API_V1_STR}")

        # 简单的健康检查路由
        @app.get("/")
        def read_root():
            return {
                "message": "ERP进销存管理系统 API",
                "status": "running",
                "version": settings.VERSION
            }

        @app.get("/health")
        def health_check():
            return {"status": "healthy"}

        print("\n🎯 API端点:")
        print("   - GET  http://localhost:8000/")
        print("   - GET  http://localhost:8000/health")

        print("\n🚀 启动开发服务器...")
        print("   服务器将在 http://localhost:8000 启动")
        print("   API文档: http://localhost:8000/docs")
        print("   按 Ctrl+C 停止服务器")

        # 启动服务器
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n💡 解决方案:")
        print("   1. 确保已安装所需依赖:")
        print("      pip install fastapi uvicorn")
        print("   2. 检查Python版本: python --version")
        print("   3. 确保在正确的目录中运行此脚本")
        return 1

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())