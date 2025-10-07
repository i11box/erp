from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=255, description="地址")


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=255, description="地址")


class Supplier(SupplierBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True