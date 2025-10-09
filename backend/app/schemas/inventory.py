from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    quantity: int = Field(default=0, description="库存数量")
    avg_cost: Decimal = Field(default=0, description="平均成本")


class InventoryCreate(InventoryBase):
    product_id: int = Field(..., description="产品ID")


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, description="库存数量")
    avg_cost: Optional[Decimal] = Field(None, description="平均成本")


class Inventory(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime

    class Config:
        from_attributes = True


# 添加一个新的schema，包含产品信息
class ProductInfo(BaseModel):
    id: int
    name: str
    sku: Optional[str]
    description: Optional[str]
    unit: str
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int

    class Config:
        from_attributes = True


class InventoryWithProduct(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime
    product: Optional[ProductInfo] = None

    class Config:
        from_attributes = True


class InventoryMovementBase(BaseModel):
    movement_type: str = Field(..., max_length=20, description="移动类型(in/out/adjustment)")
    quantity: int = Field(..., description="移动数量")
    reference_type: Optional[str] = Field(None, max_length=20, description="关联类型(purchase/sale/adjustment)")
    reference_id: Optional[int] = Field(None, description="关联ID")
    reason: Optional[str] = Field(None, max_length=255, description="原因")


class InventoryMovementCreate(InventoryMovementBase):
    product_id: int = Field(..., description="产品ID")


class InventoryMovement(InventoryMovementBase):
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True