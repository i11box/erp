from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.crud import analytics as analytics_crud
from app.models.user import User

router = APIRouter()


class DateRangeQuery(BaseModel):
    start_date: str
    end_date: str
    group_by: Optional[str] = "day"


@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取仪表板数据"""
    dashboard_data = analytics_crud.get_dashboard_data(db)
    return dashboard_data


@router.get("/sales-report")
def get_sales_report(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    group_by: str = Query("day", description="分组方式: day/week/month"),
    # current_user: User = Depends(get_current_user)
):
    """获取销售报表"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    if group_by not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="分组方式必须是 day、week 或 month")

    sales_report = analytics_crud.get_sales_report(
        db, start_date=start_dt, end_date=end_dt, group_by=group_by
    )
    return sales_report


@router.get("/purchase-report")
def get_purchase_report(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    group_by: str = Query("day", description="分组方式: day/week/month"),
    current_user: User = Depends(get_current_user)
):
    """获取采购报表"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    if group_by not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="分组方式必须是 day、week 或 month")

    purchase_report = analytics_crud.get_purchase_report(
        db, start_date=start_dt, end_date=end_dt, group_by=group_by
    )
    return purchase_report


@router.get("/top-products")
def get_top_selling_products(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(10, description="返回记录数"),
    current_user: User = Depends(get_current_user)
):
    """获取热销商品排行"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    top_products = analytics_crud.get_top_selling_products(
        db, start_date=start_dt, end_date=end_dt, limit=limit
    )
    return top_products


@router.get("/top-customers")
def get_top_customers(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(10, description="返回记录数"),
    current_user: User = Depends(get_current_user)
):
    """获取重要客户排行"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    top_customers = analytics_crud.get_top_customers(
        db, start_date=start_dt, end_date=end_dt, limit=limit
    )
    return top_customers


@router.get("/profit-analysis")
def get_profit_analysis(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """获取利润分析"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    profit_analysis = analytics_crud.get_profit_analysis(
        db, start_date=start_dt, end_date=end_dt
    )
    return profit_analysis


@router.get("/inventory-turnover")
def get_inventory_turnover(
    db: Session = Depends(get_db),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """获取库存周转率分析"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式不正确，请使用 YYYY-MM-DD 格式")

    inventory_turnover = analytics_crud.get_inventory_turnover(
        db, start_date=start_dt, end_date=end_dt
    )
    return inventory_turnover