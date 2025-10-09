from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.config import settings
from app.crud import user as user_crud
from app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """获取当前用户 - 已禁用认证"""
    return None


def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """获取当前活跃用户 - 已禁用认证"""
    return None


def get_current_active_superuser(
    current_user = Depends(get_current_user),
):
    """获取当前超级用户 - 已禁用认证"""
    return None


def get_optional_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """获取可选的当前用户 - 已禁用认证"""
    return None
