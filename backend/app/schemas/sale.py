from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class SaleItemBase(BaseModel):
    product_id: int = Field(..., description="产品ID")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Decimal = Field(..., gt=0, description="单价")


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    total_price: Decimal

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    customer_id: int = Field(..., description="客户ID")
    total_amount: Decimal = Field(default=0, description="总金额")
    status: str = Field(default="pending", max_length=20, description="状态")


class SaleCreate(SaleBase):
    items: List[SaleItemCreate] = Field(..., description="销售项目列表")


class SaleUpdate(BaseModel):
    customer_id: Optional[int] = Field(None, description="客户ID")
    total_amount: Optional[Decimal] = Field(None, description="总金额")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class Sale(SaleBase):
    id: int
    user_id: int
    sale_number: str
    sale_date: datetime
    created_at: datetime
    updated_at: datetime
    items: List[SaleItem] = []

    class Config:
        from_attributes = True