from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., max_length=100, description="邮箱地址")
    role: str = Field(default="user", max_length=20, description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255, description="密码")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    role: Optional[str] = Field(None, max_length=20, description="用户角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="密码")


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None