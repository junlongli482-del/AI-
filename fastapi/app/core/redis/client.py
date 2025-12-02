"""
Redis客户端 - 统一连接管理
"""
import json
import redis
from typing import Optional, Any
from ..config import settings


class RedisClient:
    """Redis客户端封装"""

    def __init__(self):
        print("🔍 [DEBUG] 初始化Redis客户端...")
        self._redis = None
        self._connect()
        print(f"🔍 [DEBUG] Redis客户端初始化完成，状态: {self.is_available()}")

    def _connect(self):
        """连接Redis"""
        try:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                db=settings.REDIS_DB,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            self._redis.ping()
            print("✅ Redis连接成功")
        except Exception as e:
            print(f"❌ Redis连接失败: {e}")
            print("📝 系统将使用数据库模式运行（无缓存）")
            self._redis = None

    def is_available(self) -> bool:
        """检查Redis是否可用"""
        if not self._redis:
            return False
        try:
            self._redis.ping()
            return True
        except:
            return False

    def get(self, key: str) -> Optional[str]:
        """获取数据（返回原始字符串，不自动解析JSON）"""
        if not self.is_available():
            return None
        try:
            return self._redis.get(key)
        except Exception as e:
            print(f"Redis GET错误: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置数据"""
        print(f"💾 [DEBUG] Redis SET - Key: {key}, TTL: {ttl}")
        print(f"💾 [DEBUG] Redis 可用性检查: {self.is_available()}")

        if not self.is_available():
            print("❌ [DEBUG] Redis不可用")
            return False

        try:
            data = json.dumps(value, default=str)
            print(f"💾 [DEBUG] 序列化数据: {data}")

            if ttl:
                result = self._redis.setex(key, ttl, data)
            else:
                result = self._redis.set(key, data)

            print(f"💾 [DEBUG] Redis SET 原始结果: {result}")
            return bool(result)
        except Exception as e:
            print(f"❌ [DEBUG] Redis SET错误: {e}")
            return False

    def setex(self, key: str, time: int, value: str) -> bool:
        """设置数据并指定过期时间（接受原始字符串）"""
        print(f"💾 [DEBUG] Redis SETEX - Key: {key}, TTL: {time}")
        print(f"💾 [DEBUG] Redis 可用性检查: {self.is_available()}")

        if not self.is_available():
            print("❌ [DEBUG] Redis不可用")
            return False

        try:
            result = self._redis.setex(key, time, value)
            print(f"💾 [DEBUG] Redis SETEX 原始结果: {result}")
            return bool(result)
        except Exception as e:
            print(f"❌ [DEBUG] Redis SETEX错误: {e}")
            return False

    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间（秒）"""
        if not self.is_available():
            return -1
        try:
            return self._redis.ttl(key)
        except Exception as e:
            print(f"❌ [DEBUG] Redis TTL错误: {e}")
            return -1

    def delete(self, key: str) -> bool:
        """删除数据"""
        if not self.is_available():
            return False
        try:
            return self._redis.delete(key) > 0
        except Exception as e:
            print(f"Redis DELETE错误: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if not self.is_available():
            return False
        try:
            return self._redis.exists(key) > 0
        except Exception as e:
            return False


# 全局Redis客户端实例
redis_client = RedisClient()