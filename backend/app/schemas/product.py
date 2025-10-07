from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    sku: Optional[str] = Field(None, max_length=50, description="商品编码")
    description: Optional[str] = Field(None, max_length=255, description="商品描述")
    unit: str = Field("个", max_length=20, description="计量单位")
    cost_price: Decimal = Field(0, ge=0, description="成本价")
    selling_price: Decimal = Field(0, ge=0, description="销售价")
    reorder_level: int = Field(0, ge=0, description="库存预警值")

    @validator('selling_price')
    def selling_price_must_be_greater_than_cost(cls, v, values):
        if 'cost_price' in values and v < values['cost_price']:
            raise ValueError('销售价不能低于成本价')
        return v


class ProductCreate(ProductBase):
    @validator('sku')
    def validate_sku(cls, v):
        if v and not v.strip():
            raise ValueError('SKU不能为空字符串')
        return v.strip() if v else None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="商品名称")
    sku: Optional[str] = Field(None, max_length=50, description="商品编码")
    description: Optional[str] = Field(None, max_length=255, description="商品描述")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价")
    selling_price: Optional[Decimal] = Field(None, ge=0, description="销售价")
    reorder_level: Optional[int] = Field(None, ge=0, description="库存预警值")

    @validator('selling_price')
    def selling_price_must_be_greater_than_cost(cls, v, values):
        if v is not None and 'cost_price' in values and values['cost_price'] is not None:
            if v < values['cost_price']:
                raise ValueError('销售价不能低于成本价')
        return v

    @validator('sku')
    def validate_sku(cls, v):
        if v and not v.strip():
            raise ValueError('SKU不能为空字符串')
        return v.strip() if v else None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductWithInventory(Product):
    """包含库存信息的商品"""
    quantity: int = Field(0, description="当前库存数量")
    avg_cost: Decimal = Field(0, description="平均成本")

    class Config:
        from_attributes = True