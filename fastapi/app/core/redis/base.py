"""
Redis缓存基类 - 提供通用缓存操作
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from .client import redis_client
from ..config import settings


class BaseCacheService(ABC):
    """缓存服务基类"""

    def __init__(self, cache_name: str, default_ttl: int = 3600):
        self.redis_client = redis_client
        self.cache_name = cache_name
        self.default_ttl = default_ttl
        self.key_prefix = f"{settings.CACHE_KEY_PREFIX}:{cache_name}"

    def _make_key(self, identifier: str) -> str:
        """生成缓存key"""
        return f"{self.key_prefix}:{identifier}"

    def get(self, identifier: str) -> Optional[Any]:
        """获取缓存数据"""
        key = self._make_key(identifier)
        return self.redis_client.get(key)

    def set(self, identifier: str, data: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        key = self._make_key(identifier)
        ttl = ttl or self.default_ttl
        return self.redis_client.set(key, data, ttl)

    def delete(self, identifier: str) -> bool:
        """删除缓存数据"""
        key = self._make_key(identifier)
        return self.redis_client.delete(key)

    def exists(self, identifier: str) -> bool:
        """检查缓存是否存在"""
        key = self._make_key(identifier)
        return self.redis_client.exists(key)

    def refresh(self, identifier: str, data: Any, ttl: int = None) -> bool:
        """刷新缓存数据"""
        self.delete(identifier)
        return self.set(identifier, data, ttl)

    @abstractmethod
    def get_cache_key_pattern(self) -> str:
        """返回缓存key的模式，用于监控和清理"""
        pass