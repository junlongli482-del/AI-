"""
用户缓存服务 - 专门处理用户信息缓存
"""
from typing import Optional, Dict, Any
from datetime import datetime
from ....core.redis.base import BaseCacheService
from ....core.config import settings


class UserCacheService(BaseCacheService):
    """用户缓存服务"""

    def __init__(self):
        super().__init__(
            cache_name="user",
            default_ttl=settings.USER_CACHE_TTL
        )

    def get_cache_key_pattern(self) -> str:
        """返回用户缓存key模式"""
        return f"{self.key_prefix}:*"

    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户信息缓存"""
        return self.get(str(user_id))

    def set_user_info(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """设置用户信息缓存"""
        print(f"💾 [DEBUG] 开始写入缓存，用户ID: {user_id}")
        print(f"💾 [DEBUG] Redis客户端可用性: {self.redis_client.is_available()}")

        result = self.set(str(user_id), user_data)
        print(f"💾 [DEBUG] 缓存写入最终结果: {result}")
        return result

    def delete_user_info(self, user_id: int) -> bool:
        """删除用户信息缓存"""
        return self.delete(str(user_id))

    def refresh_user_info(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """刷新用户信息缓存"""
        return self.refresh(str(user_id), user_data)

    def format_user_data(self, user) -> Dict[str, Any]:
        """格式化用户数据用于缓存"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            # 可以根据User模型添加更多字段
        }

    def create_user_object(self, cached_data: Dict[str, Any]):
        """从缓存数据创建User对象"""
        from ....modules.v1.user_auth.models import User

        user = User()
        user.id = cached_data["id"]
        user.username = cached_data["username"]
        user.email = cached_data["email"]
        user.is_active = cached_data["is_active"]
        user.created_at = datetime.fromisoformat(cached_data["created_at"])
        return user


# 全局用户缓存服务实例
user_cache = UserCacheService()