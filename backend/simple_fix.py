#!/usr/bin/env python3
"""
简单修复脚本 - 使用强制输出
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def flush_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

def main():
    flush_print("=== 开始修复数据问题 ===")

    # 检查数据库文件
    db_path = "test.db"
    flush_print(f"检查数据库文件: {db_path}")

    if os.path.exists(db_path):
        flush_print("发现旧数据库文件，正在删除...")
        os.remove(db_path)
        flush_print("旧数据库文件已删除")
    else:
        flush_print("未发现旧数据库文件")

    # 重新初始化数据库
    flush_print("正在重新初始化数据库...")
    result = os.system("python init_db.py")
    flush_print(f"数据库初始化结果: {result}")

    # 创建新的测试数据
    flush_print("正在创建测试数据...")
    result = os.system("python create_test_data.py")
    flush_print(f"测试数据创建结果: {result}")

    flush_print("=== 数据修复完成 ===")

if __name__ == "__main__":
    main()