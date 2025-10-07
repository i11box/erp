from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, suppliers, customers, products, purchases, sales, inventory, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="库存管理系统 API",
    description="进销存管理系统后端API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["供应商"])
app.include_router(customers.router, prefix="/api/customers", tags=["客户"])
app.include_router(products.router, prefix="/api/products", tags=["商品"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["采购"])
app.include_router(sales.router, prefix="/api/sales", tags=["销售"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["库存"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["统计分析"])

@app.get("/")
async def root():
    return {"message": "库存管理系统 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}