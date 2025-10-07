#!/usr/bin/env python3

"""
创建数据库表的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def create_tables():
    """创建所有数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        raise

if __name__ == "__main__":
    create_tables()