from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud import customer as customer_crud
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()


@router.get("/", response_model=List[Customer])
def get_customers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """获取客户列表"""
    if search:
        customers = customer_crud.search(
            db=db, keyword=search, skip=skip, limit=limit
        )
    else:
        customers = customer_crud.get_multi(db=db, skip=skip, limit=limit)
    return customers


@router.post("/", response_model=Customer)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate
):
    """创建新客户"""
    # 检查名称是否已存在
    existing = customer_crud.get_by_name(db=db, name=customer_in.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="客户名称已存在"
        )

    # 如果提供了邮箱，检查邮箱是否已存在
    if customer_in.email:
        existing = customer_crud.get_by_email(db=db, email=customer_in.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="邮箱地址已存在"
            )

    customer = customer_crud.create(db=db, obj_in=customer_in)
    return customer


@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int
):
    """获取客户详情"""
    customer = customer_crud.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: CustomerUpdate
):
    """更新客户信息"""
    customer = customer_crud.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 检查名称是否与其他客户重复
    if customer_in.name and customer_in.name != customer.name:
        existing = customer_crud.get_by_name(db=db, name=customer_in.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="客户名称已存在"
            )

    # 检查邮箱是否与其他客户重复
    if customer_in.email and customer_in.email != customer.email:
        existing = customer_crud.get_by_email(db=db, email=customer_in.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="邮箱地址已存在"
            )

    customer = customer_crud.update(db=db, db_obj=customer, obj_in=customer_in)
    return customer


@router.delete("/{customer_id}")
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int
):
    """删除客户"""
    customer = customer_crud.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 检查是否有关联的销售记录
    if customer_crud.has_sales(db=db, customer_id=customer_id):
        raise HTTPException(
            status_code=400,
            detail="该客户有关联的销售记录，无法删除"
        )

    customer_crud.remove(db=db, id=customer_id)
    return {"message": "客户删除成功"}