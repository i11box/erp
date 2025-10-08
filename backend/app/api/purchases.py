from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user, get_db
from app.crud import purchase as purchase_crud
from app.crud import supplier as supplier_crud
from app.models.user import User
from app.schemas.purchase import Purchase, PurchaseCreate, PurchaseUpdate
from app.schemas.purchase import PurchaseItem as PurchaseItemSchema

router = APIRouter()


@router.get("/", response_model=List[Purchase])
def read_purchases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_optional_user)
):
    """获取采购订单列表"""
    if supplier_id:
        purchases = purchase_crud.get_by_supplier(
            db, supplier_id=supplier_id, skip=skip, limit=limit
        )
    elif status:
        purchases = purchase_crud.get_by_status(
            db, status=status, skip=skip, limit=limit
        )
    elif search:
        purchases = purchase_crud.search_purchases(
            db, query=search, skip=skip, limit=limit
        )
    else:
        purchases = purchase_crud.get_multi_with_items(
            db, skip=skip, limit=limit
        )
    return purchases


@router.post("/", response_model=Purchase)
def create_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_in: PurchaseCreate,
    current_user: User = Depends(get_optional_user)
):
    """创建采购订单"""
    # Validate supplier exists
    supplier = supplier_crud.get(db, id=purchase_in.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # Validate items
    if not purchase_in.items:
        raise HTTPException(status_code=400, detail="采购订单必须包含商品")

    # Create purchase with items
    purchase = purchase_crud.create_purchase_with_items(
        db, purchase_in=purchase_in, user_id=current_user.id if current_user else None
    )
    return purchase


@router.get("/{purchase_id}", response_model=Purchase)
def read_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    current_user: User = Depends(get_optional_user)
):
    """获取采购订单详情"""
    purchase = purchase_crud.get_with_items(db, id=purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    return purchase


@router.put("/{purchase_id}", response_model=Purchase)
def update_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    purchase_in: PurchaseUpdate,
    current_user: User = Depends(get_optional_user)
):
    """更新采购订单"""
    purchase = purchase_crud.get(db, id=purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="采购订单不存在")

    # Only allow updating status for completed purchases
    if purchase.status == "completed":
        if purchase_in.status and purchase_in.status != purchase.status:
            purchase = purchase_crud.update_status(
                db, db_obj=purchase, status=purchase_in.status
            )
    else:
        purchase = purchase_crud.update_purchase_with_items(
            db, db_obj=purchase, purchase_in=purchase_in
        )
    return purchase


@router.delete("/{purchase_id}")
def delete_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    current_user: User = Depends(get_optional_user)
):
    """删除采购订单"""
    purchase = purchase_crud.get(db, id=purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    
    # Don't allow deleting completed purchases
    if purchase.status == "completed":
        raise HTTPException(status_code=400, detail="已完成的采购订单不能删除")
    
    purchase_crud.remove(db, id=purchase_id)
    return {"message": "采购订单删除成功"}