"""
Redis模块 - 统一导出接口
"""
from .client import redis_client
from .services.user_cache import user_cache

# 统一导出，方便其他模块使用
__all__ = [
    "redis_client",
    "user_cache",
]

# 便捷导入函数
def get_redis_client():
    """获取Redis客户端"""
    return redis_client

def get_user_cache():
    """获取用户缓存服务"""
    return user_cache