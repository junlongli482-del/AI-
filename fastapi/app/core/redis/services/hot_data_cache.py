"""
热门数据缓存服务
功能：专门处理热门文档和最新文档的缓存逻辑
"""
import json
import time
from typing import Dict, Any, Optional, Callable
from sqlalchemy.orm import Session

from ..client import RedisClient


class HotDataCacheService:
    """热门数据缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient()

        # 缓存配置
        self.hot_docs_ttl = 600  # 热门文档缓存10分钟
        self.latest_docs_ttl = 300  # 最新文档缓存5分钟
        self.key_prefix = "hot_data"

        print(f"🔥 [CACHE] 热门数据缓存服务初始化")
        print(f"🔥 [CACHE] 热门文档TTL: {self.hot_docs_ttl}秒, 最新文档TTL: {self.latest_docs_ttl}秒")
        print(f"🔥 [CACHE] Redis可用: {self.redis_client.is_available()}")

    def _build_hot_docs_cache_key(self, limit: int) -> str:
        """构建热门文档缓存Key"""
        key = f"{self.key_prefix}:hot_docs:limit_{limit}"
        print(f"🔑 [CACHE] 构建热门文档缓存Key: {key}")
        return key

    def _build_latest_docs_cache_key(self, limit: int) -> str:
        """构建最新文档缓存Key"""
        key = f"{self.key_prefix}:latest_docs:limit_{limit}"
        print(f"🔑 [CACHE] 构建最新文档缓存Key: {key}")
        return key

    async def get_hot_documents(self, db: Session, query_func: Callable, limit: int = 10) -> Dict[str, Any]:
        """
        获取热门文档列表（缓存优化版）
        """
        cache_key = self._build_hot_docs_cache_key(limit)

        print(f"🔥 [CACHE] 开始获取热门文档缓存...")
        print(f"🔥 [CACHE] 限制数量: {limit}, 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [CACHE] 热门文档缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key)
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [CACHE] 热门文档缓存未命中，查询数据库...")
        docs_data = await self._query_hot_documents(db, query_func, limit)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, docs_data, self.hot_docs_ttl)

        # 添加缓存信息
        docs_data["cache_info"] = {
            "cached": False,
            "cache_time": docs_data.get("_cache_time"),
            "ttl_remaining": self.hot_docs_ttl
        }

        return docs_data

    async def get_latest_documents(self, db: Session, query_func: Callable, limit: int = 10) -> Dict[str, Any]:
        """
        获取最新文档列表（缓存优化版）
        """
        cache_key = self._build_latest_docs_cache_key(limit)

        print(f"📅 [CACHE] 开始获取最新文档缓存...")
        print(f"📅 [CACHE] 限制数量: {limit}, 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [CACHE] 最新文档缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key)
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [CACHE] 最新文档缓存未命中，查询数据库...")
        docs_data = await self._query_latest_documents(db, query_func, limit)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, docs_data, self.latest_docs_ttl)

        # 添加缓存信息
        docs_data["cache_info"] = {
            "cached": False,
            "cache_time": docs_data.get("_cache_time"),
            "ttl_remaining": self.latest_docs_ttl
        }

        return docs_data

    async def _query_hot_documents(self, db: Session, query_func: Callable, limit: int) -> Dict[str, Any]:
        """查询热门文档数据（带性能监控）"""
        print(f"🗄️ [CACHE] 开始查询热门文档数据库...")
        start_time = time.time()

        try:
            # 调用传入的查询函数
            result = query_func(limit=limit)

            query_time = (time.time() - start_time) * 1000
            print(f"✅ [CACHE] 热门文档数据库查询完成，总耗时: {query_time:.2f}ms")

            # 转换为字典格式
            if hasattr(result, 'model_dump'):
                result_dict = result.model_dump()
            elif hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = result

            # 添加性能信息
            result_dict.update({
                "_cache_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "_query_performance": {
                    "query_type": "hot_documents",
                    "limit": limit,
                    "total_ms": round(query_time, 2)
                }
            })

            print(f"🗄️ [CACHE] 热门文档数量: {len(result_dict.get('documents', []))}")
            return result_dict

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [CACHE] 热门文档数据库查询失败 ({query_time:.2f}ms): {e}")
            raise

    async def _query_latest_documents(self, db: Session, query_func: Callable, limit: int) -> Dict[str, Any]:
        """查询最新文档数据（带性能监控）"""
        print(f"🗄️ [CACHE] 开始查询最新文档数据库...")
        start_time = time.time()

        try:
            # 调用传入的查询函数
            result = query_func(limit=limit)

            query_time = (time.time() - start_time) * 1000
            print(f"✅ [CACHE] 最新文档数据库查询完成，总耗时: {query_time:.2f}ms")

            # 转换为字典格式
            if hasattr(result, 'model_dump'):
                result_dict = result.model_dump()
            elif hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = result

            # 添加性能信息
            result_dict.update({
                "_cache_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "_query_performance": {
                    "query_type": "latest_documents",
                    "limit": limit,
                    "total_ms": round(query_time, 2)
                }
            })

            print(f"🗄️ [CACHE] 最新文档数量: {len(result_dict.get('documents', []))}")
            return result_dict

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [CACHE] 最新文档数据库查询失败 ({query_time:.2f}ms): {e}")
            raise

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，跳过缓存读取")
            return None

        try:
            start_time = time.time()
            cached_str = self.redis_client.get(cache_key)
            read_time = (time.time() - start_time) * 1000

            if cached_str:
                data = json.loads(cached_str)
                print(f"💾 [CACHE] 缓存读取成功 ({read_time:.2f}ms), 数据大小: {len(cached_str)} bytes")
                return data
            else:
                print(f"💾 [CACHE] 缓存Key不存在 ({read_time:.2f}ms)")
                return None

        except Exception as e:
            print(f"❌ [CACHE] 缓存读取失败: {e}")
            return None

    async def _save_to_cache(self, cache_key: str, data: Dict[str, Any], ttl: int) -> bool:
        """保存数据到缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，跳过缓存写入")
            return False

        try:
            start_time = time.time()
            data_str = json.dumps(data, ensure_ascii=False, default=str)
            success = self.redis_client.setex(cache_key, ttl, data_str)
            write_time = (time.time() - start_time) * 1000

            if success:
                print(f"💾 [CACHE] 缓存写入成功 ({write_time:.2f}ms)")
                print(f"💾 [CACHE] 数据大小: {len(data_str)} bytes, TTL: {ttl}秒")
                return True
            else:
                print(f"⚠️ [CACHE] 缓存写入失败 ({write_time:.2f}ms)")
                return False

        except Exception as e:
            print(f"❌ [CACHE] 缓存写入异常: {e}")
            return False

    async def invalidate_hot_documents_cache(self) -> bool:
        """清除所有热门文档缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            # 获取所有热门文档缓存Key
            pattern = f"{self.key_prefix}:hot_docs:*"
            keys = self.redis_client.scan_iter(match=pattern)

            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [CACHE] 热门文档缓存已清除: {deleted_count}个Key")
            return True

        except Exception as e:
            print(f"❌ [CACHE] 清除热门文档缓存失败: {e}")
            return False

    async def invalidate_latest_documents_cache(self) -> bool:
        """清除所有最新文档缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            # 获取所有最新文档缓存Key
            pattern = f"{self.key_prefix}:latest_docs:*"
            keys = self.redis_client.scan_iter(match=pattern)

            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [CACHE] 最新文档缓存已清除: {deleted_count}个Key")
            return True

        except Exception as e:
            print(f"❌ [CACHE] 清除最新文档缓存失败: {e}")
            return False

    async def invalidate_all_hot_data_cache(self) -> bool:
        """清除所有热门数据缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            # 获取所有热门数据缓存Key
            pattern = f"{self.key_prefix}:*"
            keys = self.redis_client.scan_iter(match=pattern)

            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [CACHE] 所有热门数据缓存已清除: {deleted_count}个Key")
            return True

        except Exception as e:
            print(f"❌ [CACHE] 清除所有热门数据缓存失败: {e}")
            return False


# 全局实例
hot_data_cache_service = HotDataCacheService()