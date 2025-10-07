from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import Token, User
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.config import settings
from app.crud import user as user_crud

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_crud.authenticate(
        db, username=form_data.username, password=form_data.password
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
            "is_active": user.is_active
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