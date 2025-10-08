#!/usr/bin/env python3
"""
快速修复SKU重复问题的脚本
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("开始修复数据问题...")

    # 检查数据库文件
    db_path = "test.db"
    if os.path.exists(db_path):
        print(f"数据库文件存在: {db_path}")
        os.remove(db_path)
        print("已删除旧数据库文件")

    # 重新初始化数据库
    print("正在重新初始化数据库...")
    os.system("python init_db.py")

    # 创建新的测试数据
    print("正在创建测试数据...")
    os.system("python create_test_data.py")

    print("数据修复完成！")

if __name__ == "__main__":
    main()