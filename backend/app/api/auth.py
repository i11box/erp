from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.schemas import Token, User
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.config import settings
from app.crud import user as user_crud

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: LoginRequest = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_crud.authenticate(
        db, username=login_data.username, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }


@router.post("/login/test", response_model=User)
def test_login(
    *,
    db: Session = Depends(get_db),
    username: str,
    password: str
) -> Any:
    """
    测试登录接口，直接返回用户信息
    """
    user = user_crud.authenticate(
        db, username=username, password=password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return user


@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    用户登出 (客户端需要删除token)
    """
    return {"message": "登出成功"}


@router.get("/debug/users")
def debug_users(db: Session = Depends(get_db)) -> Any:
    """
    调试接口：查看所有用户信息
    """
    try:
        from app.crud import user as user_crud

        # 获取所有用户
        from sqlalchemy import text
        users = db.execute(text("SELECT id, username, email, role, is_active, password_hash FROM users")).fetchall()

        result = []
        for user in users:
            result.append({
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[3],
                "is_active": user[4],
                "password_hash": user[5][:20] + "..." if user[5] else None
            })

        return {"users": result, "total": len(result)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/debug/login")
def debug_login(login_data: LoginRequest = Body(...), db: Session = Depends(get_db)) -> Any:
    """
    调试接口：测试登录流程
    """
    try:
        from app.crud import user as user_crud
        from app.core.security import verify_password

        # 1. 查找用户
        user = user_crud.get_by_username(db, username=login_data.username)

        if not user:
            return {
                "success": False,
                "error": "用户不存在",
                "username": login_data.username
            }

        # 2. 检查用户状态
        if not user_crud.is_active(user):
            return {
                "success": False,
                "error": "用户已被禁用",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "is_active": user.is_active
                }
            }

        # 3. 验证密码
        is_password_valid = verify_password(login_data.password, user.password_hash)

        if not is_password_valid:
            return {
                "success": False,
                "error": "密码错误",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "password_hash": user.password_hash[:20] + "..."
                },
                "input_password": login_data.password
            }

        # 4. 登录成功
        return {
            "success": True,
            "message": "登录成功",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"系统错误: {str(e)}",
            "traceback": traceback.format_exc()
        }