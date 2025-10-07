from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud import product as product_crud
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductWithInventory

router = APIRouter()


@router.get("/", response_model=List[Product])
def get_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    include_inventory: bool = Query(False)
):
    """获取商品列表"""
    if search:
        products = product_crud.search(
            db=db, keyword=search, skip=skip, limit=limit
        )
    elif include_inventory:
        products = product_crud.get_multi_with_inventory(
            db=db, skip=skip, limit=limit
        )
    else:
        products = product_crud.get_multi(db=db, skip=skip, limit=limit)
    return products


@router.get("/low-stock", response_model=List[ProductWithInventory])
def get_low_stock_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取库存不足的商品"""
    products = product_crud.get_low_stock_products(db=db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate
):
    """创建新商品"""
    # 检查SKU是否已存在
    if product_in.sku:
        existing = product_crud.get_by_sku(db=db, sku=product_in.sku)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="商品SKU已存在"
            )

    # 检查名称是否已存在
    existing = product_crud.get_by_name(db=db, name=product_in.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="商品名称已存在"
        )

    product = product_crud.create(db=db, obj_in=product_in)

    # 为新商品创建库存记录
    from app.models.inventory import Inventory
    inventory = Inventory(
        product_id=product.id,
        quantity=0,
        avg_cost=product.cost_price
    )
    db.add(inventory)
    db.commit()

    return product


@router.get("/{product_id}", response_model=Product)
def get_product(
    *,
    db: Session = Depends(get_db),
    product_id: int
):
    """获取商品详情"""
    product = product_crud.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate
):
    """更新商品信息"""
    product = product_crud.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查SKU是否与其他商品重复
    if product_in.sku and product_in.sku != product.sku:
        existing = product_crud.get_by_sku(db=db, sku=product_in.sku)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="商品SKU已存在"
            )

    # 检查名称是否与其他商品重复
    if product_in.name and product_in.name != product.name:
        existing = product_crud.get_by_name(db=db, name=product_in.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="商品名称已存在"
            )

    product = product_crud.update(db=db, db_obj=product, obj_in=product_in)
    return product


@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int
):
    """删除商品"""
    product = product_crud.get(db=db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查是否有关联的交易记录
    if product_crud.has_transactions(db=db, product_id=product_id):
        raise HTTPException(
            status_code=400,
            detail="该商品有关联的交易记录，无法删除"
        )

    # 删除相关的库存记录
    from app.models.inventory import Inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inventory:
        db.delete(inventory)

    product_crud.remove(db=db, id=product_id)
    return {"message": "商品删除成功"}