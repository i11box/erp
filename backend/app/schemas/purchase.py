from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class PurchaseItemBase(BaseModel):
    product_id: int = Field(..., description="产品ID")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Decimal = Field(..., gt=0, description="单价")


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItem(PurchaseItemBase):
    id: int
    purchase_id: int
    total_price: Decimal

    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    supplier_id: int = Field(..., description="供应商ID")
    total_amount: Decimal = Field(default=0, description="总金额")
    status: str = Field(default="pending", max_length=20, description="状态")


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate] = Field(..., description="采购项目列表")


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    total_amount: Optional[Decimal] = Field(None, description="总金额")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class Purchase(PurchaseBase):
    id: int
    user_id: int
    purchase_number: str
    purchase_date: datetime
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseItem] = []

    class Config:
        from_attributes = True