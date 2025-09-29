"""
用户认证模块 - 依赖注入
提供JWT令牌验证和用户身份验证的依赖
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from .services import AuthService
from .models import User

# HTTP Bearer 认证方案
security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户的依赖函数
    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话
    Returns:
        User: 当前用户对象
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    # 提取令牌
    token = credentials.credentials

    # 验证令牌并获取用户
    user = AuthService.get_current_user(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已被禁用"
        )

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户的依赖函数
    Args:
        current_user: 当前用户
    Returns:
        User: 活跃用户对象
    """
    return current_user