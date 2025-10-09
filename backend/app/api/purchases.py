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


@router.get("/")
def read_purchases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    # current_user: User = Depends(get_optional_user)
):
    """获取采购订单列表"""
    if supplier_id:
        purchases = purchase_crud.get_by_supplier_flattened(
            db, supplier_id=supplier_id, skip=skip, limit=limit
        )
    elif status:
        purchases = purchase_crud.get_by_status_flattened(
            db, status=status, skip=skip, limit=limit
        )
    elif search:
        purchases = purchase_crud.search_purchases_flattened(
            db, query=search, skip=skip, limit=limit
        )
    else:
        purchases = purchase_crud.get_multi_with_items_flattened(
            db, skip=skip, limit=limit
        )
    return purchases


@router.post("/")
def create_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_in: PurchaseCreate,
    # current_user: User = Depends(get_optional_user)
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
        db, purchase_in=purchase_in, user_id= None #current_user.id if current_user else None
    )
    
    # Return flattened version
    flattened_purchase = {
        "id": purchase.id,
        "supplier_id": purchase.supplier_id,
        "user_id": purchase.user_id,
        "purchase_number": purchase.purchase_number,
        "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
        "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
        "status": purchase.status,
        "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
        "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
        "items": [
            {
                "id": item.id,
                "purchase_id": item.purchase_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else 0,
                "total_price": float(item.total_price) if item.total_price else 0,
                "product_name": item.product.name if item.product else None,
                "product_sku": item.product.sku if item.product else None
            }
            for item in purchase.items
        ]
    }
    return flattened_purchase


@router.get("/{purchase_id}")
def read_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    # current_user: User = Depends(get_optional_user)
):
    """获取采购订单详情"""
    purchase = purchase_crud.get_with_items(db, id=purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    
    # Return flattened version
    flattened_purchase = {
        "id": purchase.id,
        "supplier_id": purchase.supplier_id,
        "user_id": purchase.user_id,
        "purchase_number": purchase.purchase_number,
        "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
        "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
        "status": purchase.status,
        "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
        "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
        "items": [
            {
                "id": item.id,
                "purchase_id": item.purchase_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else 0,
                "total_price": float(item.total_price) if item.total_price else 0,
                "product_name": item.product.name if item.product else None,
                "product_sku": item.product.sku if item.product else None
            }
            for item in purchase.items
        ]
    }
    return flattened_purchase


@router.put("/{purchase_id}")
def update_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    purchase_in: PurchaseUpdate,
    # current_user: User = Depends(get_optional_user)
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
    
    db.refresh(purchase)
    
    # Return flattened version
    flattened_purchase = {
        "id": purchase.id,
        "supplier_id": purchase.supplier_id,
        "user_id": purchase.user_id,
        "purchase_number": purchase.purchase_number,
        "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
        "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
        "status": purchase.status,
        "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
        "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
        "items": []
    }
    return flattened_purchase


@router.patch("/{purchase_id}/status")
def update_purchase_status(
    *,
    db: Session = Depends(get_db),
    purchase_id: int,
    status: str,
    # current_user: User = Depends(get_optional_user)
):
    """更新采购订单状态"""
    purchase = purchase_crud.get(db, id=purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    
    purchase = purchase_crud.update_status(db, db_obj=purchase, status=status)
    
    # Return flattened version
    flattened_purchase = {
        "id": purchase.id,
        "supplier_id": purchase.supplier_id,
        "user_id": purchase.user_id,
        "purchase_number": purchase.purchase_number,
        "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
        "total_amount": float(purchase.total_amount) if purchase.total_amount else 0,
        "status": purchase.status,
        "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
        "updated_at": purchase.updated_at.isoformat() if purchase.updated_at else None,
        "items": []
    }
    return flattened_purchase