from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel

from app.api.deps import get_optional_user, get_db
from app.crud import inventory as inventory_crud
from app.crud import product as product_crud
from app.models.user import User
from app.schemas.inventory import InventoryMovement, InventoryMovementCreate

router = APIRouter()


class InventoryAdjust(BaseModel):
    product_id: int
    adjustment_quantity: int
    reason: str
    new_avg_cost: Optional[float] = None


@router.get("/")
def read_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    low_stock: bool = Query(False),
    out_of_stock: bool = Query(False),
    # current_user: User = Depends(get_optional_user)
):
    """获取库存列表（扁平化数据结构）"""
    if low_stock:
        inventory_items = inventory_crud.get_low_stock_items_flattened(
            db, skip=skip, limit=limit
        )
    elif out_of_stock:
        inventory_items = inventory_crud.get_out_of_stock_items_flattened(
            db, skip=skip, limit=limit
        )
    elif search:
        # 搜索功能暂用通用方法替代
        inventory_items = inventory_crud.get_with_product_flattened(
            db, skip=skip, limit=limit
        )
    else:
        inventory_items = inventory_crud.get_with_product_flattened(
            db, skip=skip, limit=limit
        )
    return inventory_items


@router.get("/low-stock")
def read_low_stock_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: User = Depends(get_optional_user)
):
    """获取库存不足商品（扁平化数据结构）"""
    return inventory_crud.get_low_stock_items_flattened(
        db, skip=skip, limit=limit
    )


@router.get("/out-of-stock")
def read_out_of_stock_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: User = Depends(get_optional_user)
):
    """获取缺货商品（扁平化数据结构）"""
    return inventory_crud.get_out_of_stock_items_flattened(
        db, skip=skip, limit=limit
    )


@router.get("/summary")
def read_inventory_summary(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_optional_user)
):
    """获取库存汇总信息"""
    return inventory_crud.get_inventory_summary(db)


@router.get("/{product_id}")
def read_product_inventory(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    # current_user: User = Depends(get_optional_user)
):
    """获取指定商品的库存信息（扁平化数据结构）"""
    inventory = inventory_crud.get_by_product(db, product_id=product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    
    # 转换为扁平化格式
    if inventory.product:
        flattened_item = {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "quantity": inventory.quantity,
            "avg_cost": float(inventory.avg_cost) if inventory.avg_cost else 0,
            "last_updated": inventory.last_updated.isoformat() if inventory.last_updated else None,
            "product_name": inventory.product.name,
            "product_sku": inventory.product.sku,
            "product_description": inventory.product.description,
            "unit": inventory.product.unit,
            "cost_price": float(inventory.product.cost_price) if inventory.product.cost_price else 0,
            "selling_price": float(inventory.product.selling_price) if inventory.product.selling_price else 0,
            "reorder_level": inventory.product.reorder_level
        }
        return flattened_item
    else:
        return inventory


@router.post("/adjust")
def adjust_inventory(
    *,
    db: Session = Depends(get_db),
    adjustment: InventoryAdjust,
    # current_user: User = Depends(get_optional_user)
):
    """调整库存数量"""
    # Validate product exists
    product = product_crud.get(db, id=adjustment.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # Validate adjustment quantity
    if adjustment.adjustment_quantity == 0:
        raise HTTPException(status_code=400, detail="调整数量不能为0")

    # Perform inventory adjustment
    inventory = inventory_crud.adjust_inventory(
        db,
        product_id=adjustment.product_id,
        adjustment_quantity=adjustment.adjustment_quantity,
        reason=adjustment.reason,
        # user_id=current_user.id if current_user else None,
        user_id=None,
        new_avg_cost=adjustment.new_avg_cost
    )

    return {"message": "库存调整成功", "inventory": inventory}


@router.get("/movements/", response_model=List[InventoryMovement])
def read_inventory_movements(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    # current_user: User = Depends(get_optional_user)
):
    """获取库存变动记录"""
    if product_id:
        movements = inventory_crud.inventory_movement.get_by_product(
            db, product_id=product_id, skip=skip, limit=limit
        )
    elif start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            movements = inventory_crud.inventory_movement.get_movements_by_date_range(
                db, start_date=start_dt, end_date=end_dt, skip=skip, limit=limit
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    else:
        movements = inventory_crud.inventory_movement.get_all_movements(
            db, skip=skip, limit=limit, movement_type=movement_type
        )
    return movements


@router.get("/movements/{product_id}", response_model=List[InventoryMovement])
def read_product_movements(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    # current_user: User = Depends(get_optional_user)
):
    """获取指定商品的库存变动记录"""
    # Validate product exists
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    movements = inventory_crud.inventory_movement.get_by_product(
        db, product_id=product_id, skip=skip, limit=limit
    )
    return movements