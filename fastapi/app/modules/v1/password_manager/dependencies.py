"""
密码管理模块 - 依赖注入
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings

# JWT认证方案
security = HTTPBearer()


def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> int:
    """
    从JWT令牌中获取当前用户ID

    Args:
        credentials: HTTP Bearer认证凭据
        db: 数据库会话

    Returns:
        int: 用户ID

    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码JWT令牌
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # 获取用户ID
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # 转换为整数
        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # 验证用户是否存在且激活
    from sqlalchemy import text
    query = text("SELECT id FROM us_users WHERE id = :user_id AND is_active = 1")
    result = db.execute(query, {"user_id": user_id})
    user = result.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    return user_id


def get_password_service():
    """
    获取密码服务实例

    Returns:
        PasswordService: 密码服务实例
    """
    from .services import PasswordService
    return PasswordService()