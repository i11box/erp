from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_optional_user, get_db
from app.crud import sale as sale_crud
from app.crud import customer as customer_crud
from app.models.user import User
from app.schemas.sale import Sale, SaleCreate, SaleUpdate

router = APIRouter()


@router.get("/")
def read_sales(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    # # current_user: User = Depends(get_optional_user)
):
    """获取销售订单列表"""
    if customer_id:
        sales = sale_crud.get_by_customer_flattened(
            db, customer_id=customer_id, skip=skip, limit=limit
        )
    elif status:
        sales = sale_crud.get_by_status_flattened(
            db, status=status, skip=skip, limit=limit
        )
    elif search:
        sales = sale_crud.search_sales_flattened(
            db, query=search, skip=skip, limit=limit
        )
    elif date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            date_dt = datetime.combine(date_obj, datetime.min.time())
            sales = sale_crud.get_daily_sales_flattened(
                db, date=date_dt, skip=skip, limit=limit
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")
    else:
        sales = sale_crud.get_multi_with_items_flattened(
            db, skip=skip, limit=limit
        )
    return sales


@router.post("/")
def create_sale(
    *,
    db: Session = Depends(get_db),
    sale_in: SaleCreate,
    # current_user: User = Depends(get_optional_user)
):
    """创建销售订单"""
    # Validate customer exists
    customer = customer_crud.get(db, id=sale_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    # Validate items
    if not sale_in.items:
        raise HTTPException(status_code=400, detail="销售订单必须包含商品")

    try:
        # Create sale with items (includes inventory check)
        sale = sale_crud.create_sale_with_items(
            db, sale_in=sale_in, user_id=None# user_id=current_user.id if current_user else None
        )
        
        # Return flattened version
        flattened_sale = {
            "id": sale.id,
            "customer_id": sale.customer_id,
            "user_id": sale.user_id,
            "sale_number": sale.sale_number,
            "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
            "total_amount": float(sale.total_amount) if sale.total_amount else 0,
            "status": sale.status,
            "created_at": sale.created_at.isoformat() if sale.created_at else None,
            "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
            "items": [
                {
                    "id": item.id,
                    "sale_id": item.sale_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price else 0,
                    "total_price": float(item.total_price) if item.total_price else 0,
                    "product_name": item.product.name if item.product else None,
                    "product_sku": item.product.sku if item.product else None
                }
                for item in sale.items
            ]
        }
        return flattened_sale
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{sale_id}")
def read_sale(
    *,
    db: Session = Depends(get_db),
    sale_id: int,
    # current_user: User = Depends(get_optional_user)
):
    """获取销售订单详情"""
    sale = sale_crud.get_with_items(db, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    
    # Return flattened version
    flattened_sale = {
        "id": sale.id,
        "customer_id": sale.customer_id,
        "user_id": sale.user_id,
        "sale_number": sale.sale_number,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "total_amount": float(sale.total_amount) if sale.total_amount else 0,
        "status": sale.status,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
        "items": [
            {
                "id": item.id,
                "sale_id": item.sale_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else 0,
                "total_price": float(item.total_price) if item.total_price else 0,
                "product_name": item.product.name if item.product else None,
                "product_sku": item.product.sku if item.product else None
            }
            for item in sale.items
        ]
    }
    return flattened_sale


@router.put("/{sale_id}")
def update_sale(
    *,
    db: Session = Depends(get_db),
    sale_id: int,
    sale_in: SaleUpdate,
    # current_user: User = Depends(get_optional_user)
):
    """更新销售订单"""
    sale = sale_crud.get(db, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    
    # Only allow updating status for completed sales
    if sale.status == "completed":
        if sale_in.status and sale_in.status != sale.status:
            sale = sale_crud.update_status(
                db, db_obj=sale, status=sale_in.status
            )
    else:
        sale = sale_crud.update_sale_with_items(
            db, db_obj=sale, sale_in=sale_in
        )
    
    db.refresh(sale)
    
    # Return flattened version
    flattened_sale = {
        "id": sale.id,
        "customer_id": sale.customer_id,
        "user_id": sale.user_id,
        "sale_number": sale.sale_number,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "total_amount": float(sale.total_amount) if sale.total_amount else 0,
        "status": sale.status,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
        "items": []
    }
    return flattened_sale


@router.patch("/{sale_id}/status")
def update_sale_status(
    *,
    db: Session = Depends(get_db),
    sale_id: int,
    status: str,
    # current_user: User = Depends(get_optional_user)
):
    """更新销售订单状态"""
    sale = sale_crud.get(db, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    
    sale = sale_crud.update_status(db, db_obj=sale, status=status)
    
    # Return flattened version
    flattened_sale = {
        "id": sale.id,
        "customer_id": sale.customer_id,
        "user_id": sale.user_id,
        "sale_number": sale.sale_number,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "total_amount": float(sale.total_amount) if sale.total_amount else 0,
        "status": sale.status,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
        "items": []
    }
    return flattened_sale


@router.delete("/{sale_id}")
def delete_sale(
    *,
    db: Session = Depends(get_db),
    sale_id: int,
    # current_user: User = Depends(get_optional_user)
):
    """删除销售订单"""
    sale = sale_crud.get(db, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    
    # Don't allow deleting completed sales
    if sale.status == "completed":
        raise HTTPException(status_code=400, detail="已完成的销售订单不能删除")
    
    sale_crud.remove(db, id=sale_id)
    return {"message": "销售订单删除成功"}