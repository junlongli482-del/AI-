"""
文档管理模块 - 依赖注入
功能：提供数据库会话和用户认证依赖
"""
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.core.database import SessionLocal
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v1.user_register.models import User

def get_db():
    """
    获取数据库会话
    这是一个依赖函数，FastAPI会自动管理数据库连接的生命周期
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取当前活跃用户
    复用v1版本的用户认证，确保用户已登录且账户激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    return current_user

# 组合依赖：同时获取数据库会话和当前用户
def get_db_and_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    组合依赖：同时提供数据库会话和当前用户
    这样在路由中就不需要重复声明两个依赖了
    """
    return db, current_user