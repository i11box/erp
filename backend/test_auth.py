#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.crud import user as user_crud
from app.core.security import verify_password, get_password_hash

def test_auth():
    """测试认证逻辑"""
    db = SessionLocal()

    try:
        print("=== 测试认证逻辑 ===")

        # 1. 检查admin用户是否存在
        print("\n1. 检查admin用户:")
        admin_user = user_crud.get_by_username(db, username="admin")
        if admin_user:
            print(f"✓ 找到admin用户: ID={admin_user.id}, 用户名={admin_user.username}")
            print(f"  密码哈希: {admin_user.password_hash[:50]}...")
            print(f"  角色: {admin_user.role}, 激活状态: {admin_user.is_active}")
        else:
            print("✗ 未找到admin用户")
            return

        # 2. 测试密码验证
        print("\n2. 测试密码验证:")
        test_password = "admin123"
        is_valid = verify_password(test_password, admin_user.password_hash)
        print(f"测试密码: {test_password}")
        print(f"验证结果: {'✓ 密码正确' if is_valid else '✗ 密码错误'}")

        # 3. 测试完整的认证流程
        print("\n3. 测试完整认证流程:")
        authenticated_user = user_crud.authenticate(db, username="admin", password="admin123")
        if authenticated_user:
            print(f"✓ 认证成功: 用户ID={authenticated_user.id}, 用户名={authenticated_user.username}")
        else:
            print("✗ 认证失败")

        # 4. 测试错误密码
        print("\n4. 测试错误密码:")
        wrong_auth_user = user_crud.authenticate(db, username="admin", password="wrongpassword")
        if wrong_auth_user:
            print(f"✗ 错误密码竟然通过了认证!")
        else:
            print("✓ 错误密码正确地被拒绝了")

        # 5. 测试不存在的用户
        print("\n5. 测试不存在的用户:")
        nonexistent_user = user_crud.authenticate(db, username="nonexistent", password="anypassword")
        if nonexistent_user:
            print(f"✗ 不存在的用户竟然通过了认证!")
        else:
            print("✓ 不存在的用户正确地被拒绝了")

        # 6. 检查user用户
        print("\n6. 检查user用户:")
        test_user = user_crud.get_by_username(db, username="user")
        if test_user:
            print(f"✓ 找到user用户: ID={test_user.id}, 用户名={test_user.username}")
            user_auth = user_crud.authenticate(db, username="user", password="user123")
            print(f"密码user123验证: {'✓ 通过' if user_auth else '✗ 失败'}")
        else:
            print("✗ 未找到user用户")

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()