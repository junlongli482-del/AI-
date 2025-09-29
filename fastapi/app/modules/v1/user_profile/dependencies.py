"""
用户中心模块 - 依赖注入
定义模块专用的依赖注入函数
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

# 导入核心依赖
from ....core.database import get_db
from .services import UserProfileService

def get_user_profile_service(db: Session = Depends(get_db)) -> UserProfileService:
    """
    获取用户中心服务实例

    Args:
        db: 数据库会话

    Returns:
        UserProfileService: 用户中心服务实例
    """
    return UserProfileService(db)

# 类型别名，方便使用
UserProfileServiceDep = Annotated[UserProfileService, Depends(get_user_profile_service)]