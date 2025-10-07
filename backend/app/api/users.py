from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """获取用户列表"""
    return {"message": "用户管理功能待实现"}