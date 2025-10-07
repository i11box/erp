from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud import supplier as supplier_crud
from app.schemas.supplier import Supplier, SupplierCreate, SupplierUpdate

router = APIRouter()


@router.get("/", response_model=List[Supplier])
def get_suppliers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """获取供应商列表"""
    if search:
        suppliers = supplier_crud.search(
            db=db, keyword=search, skip=skip, limit=limit
        )
    else:
        suppliers = supplier_crud.get_multi(db=db, skip=skip, limit=limit)
    return suppliers


@router.post("/", response_model=Supplier)
def create_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_in: SupplierCreate
):
    """创建新供应商"""
    # 检查名称是否已存在
    existing = supplier_crud.get_by_name(db=db, name=supplier_in.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="供应商名称已存在"
        )

    # 如果提供了邮箱，检查邮箱是否已存在
    if supplier_in.email:
        existing = supplier_crud.get_by_email(db=db, email=supplier_in.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="邮箱地址已存在"
            )

    supplier = supplier_crud.create(db=db, obj_in=supplier_in)
    return supplier


@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_id: int
):
    """获取供应商详情"""
    supplier = supplier_crud.get(db=db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


@router.put("/{supplier_id}", response_model=Supplier)
def update_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_id: int,
    supplier_in: SupplierUpdate
):
    """更新供应商信息"""
    supplier = supplier_crud.get(db=db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 检查名称是否与其他供应商重复
    if supplier_in.name and supplier_in.name != supplier.name:
        existing = supplier_crud.get_by_name(db=db, name=supplier_in.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="供应商名称已存在"
            )

    # 检查邮箱是否与其他供应商重复
    if supplier_in.email and supplier_in.email != supplier.email:
        existing = supplier_crud.get_by_email(db=db, email=supplier_in.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="邮箱地址已存在"
            )

    supplier = supplier_crud.update(db=db, db_obj=supplier, obj_in=supplier_in)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_id: int
):
    """删除供应商"""
    supplier = supplier_crud.get(db=db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 检查是否有关联的采购记录
    if supplier_crud.has_purchases(db=db, supplier_id=supplier_id):
        raise HTTPException(
            status_code=400,
            detail="该供应商有关联的采购记录，无法删除"
        )

    supplier_crud.remove(db=db, id=supplier_id)
    return {"message": "供应商删除成功"}