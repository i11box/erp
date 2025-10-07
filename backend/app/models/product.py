from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    sku = Column(String(50), unique=True, index=True)
    description = Column(String(255))
    unit = Column(String(20), default="个")
    cost_price = Column(Numeric(10, 2), default=0)
    selling_price = Column(Numeric(10, 2), default=0)
    reorder_level = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())