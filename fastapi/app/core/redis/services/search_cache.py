"""
搜索结果缓存服务
功能：专门处理搜索结果的缓存逻辑
"""
import json
import time
import hashlib
from typing import Dict, Any, Optional, Callable
from sqlalchemy.orm import Session

from ..client import RedisClient


class SearchCacheService:
    """搜索结果缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient()

        # 缓存配置
        self.search_ttl = 480  # 搜索结果缓存8分钟
        self.key_prefix = "search_cache"

        print(f"🔍 [CACHE] 搜索缓存服务初始化")
        print(f"🔍 [CACHE] 搜索结果TTL: {self.search_ttl}秒")
        print(f"🔍 [CACHE] Redis可用: {self.redis_client.is_available()}")

    def _build_search_cache_key(self, keyword: str, page: int, size: int, file_type: Optional[str] = None) -> str:
        """构建搜索缓存Key"""
        # 对搜索关键词进行哈希处理，避免特殊字符和长度问题
        keyword_hash = self._generate_keyword_hash(keyword)
        file_type_str = file_type or "none"

        key = f"{self.key_prefix}:keyword_{keyword_hash}:p{page}:s{size}:t{file_type_str}"
        print(f"🔑 [CACHE] 构建搜索缓存Key: {key}")
        print(f"🔑 [CACHE] 原始关键词: '{keyword}' -> 哈希: {keyword_hash}")
        return key

    def _generate_keyword_hash(self, keyword: str) -> str:
        """生成关键词哈希"""
        # 使用MD5哈希，取前8位作为标识
        hash_obj = hashlib.md5(keyword.lower().strip().encode('utf-8'))
        keyword_hash = hash_obj.hexdigest()[:8]
        return keyword_hash

    async def get_search_results(
            self,
            db: Session,
            query_func: Callable,
            keyword: str,
            page: int = 1,
            size: int = 20,
            file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取搜索结果（缓存优化版）
        """
        cache_key = self._build_search_cache_key(keyword, page, size, file_type)

        print(f"🔍 [CACHE] 开始获取搜索结果缓存...")
        print(f"🔍 [CACHE] 搜索参数: keyword='{keyword}', page={page}, size={size}, file_type={file_type}")
        print(f"🔍 [CACHE] 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [CACHE] 搜索结果缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key),
                "search_keyword": keyword,
                "keyword_hash": self._generate_keyword_hash(keyword)
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [CACHE] 搜索结果缓存未命中，查询数据库...")
        search_data = await self._query_search_results(db, query_func, keyword, page, size, file_type)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, search_data)

        # 添加缓存信息
        search_data["cache_info"] = {
            "cached": False,
            "cache_time": search_data.get("_cache_time"),
            "ttl_remaining": self.search_ttl,
            "search_keyword": keyword,
            "keyword_hash": self._generate_keyword_hash(keyword)
        }

        return search_data

    async def _query_search_results(
            self,
            db: Session,
            query_func: Callable,
            keyword: str,
            page: int,
            size: int,
            file_type: Optional[str]
    ) -> Dict[str, Any]:
        """查询搜索结果数据（带性能监控）"""
        print(f"🗄️ [CACHE] 开始查询搜索结果数据库...")
        start_time = time.time()

        try:
            # 调用传入的查询函数
            result = query_func(
                keyword=keyword,
                page=page,
                size=size,
                file_type=file_type
            )

            query_time = (time.time() - start_time) * 1000
            print(f"✅ [CACHE] 搜索结果数据库查询完成，总耗时: {query_time:.2f}ms")

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
                    "query_type": "search_results",
                    "keyword": keyword,
                    "keyword_hash": self._generate_keyword_hash(keyword),
                    "page": page,
                    "size": size,
                    "file_type": file_type,
                    "total_ms": round(query_time, 2)
                }
            })

            result_count = len(result_dict.get('documents', []))
            total_count = result_dict.get('total', 0)
            print(f"🗄️ [CACHE] 搜索结果: 当前页{result_count}条, 总计{total_count}条")
            return result_dict

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [CACHE] 搜索结果数据库查询失败 ({query_time:.2f}ms): {e}")
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

    async def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """保存数据到缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，跳过缓存写入")
            return False

        try:
            start_time = time.time()
            data_str = json.dumps(data, ensure_ascii=False, default=str)
            success = self.redis_client.setex(cache_key, self.search_ttl, data_str)
            write_time = (time.time() - start_time) * 1000

            if success:
                print(f"💾 [CACHE] 缓存写入成功 ({write_time:.2f}ms)")
                print(f"💾 [CACHE] 数据大小: {len(data_str)} bytes, TTL: {self.search_ttl}秒")
                return True
            else:
                print(f"⚠️ [CACHE] 缓存写入失败 ({write_time:.2f}ms)")
                return False

        except Exception as e:
            print(f"❌ [CACHE] 缓存写入异常: {e}")
            return False

    async def invalidate_search_cache_by_keyword(self, keyword: str) -> bool:
        """清除指定关键词的所有搜索缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            keyword_hash = self._generate_keyword_hash(keyword)
            pattern = f"{self.key_prefix}:keyword_{keyword_hash}:*"
            keys = self.redis_client.scan_iter(match=pattern)

            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [CACHE] 关键词'{keyword}'的搜索缓存已清除: {deleted_count}个Key")
            return True

        except Exception as e:
            print(f"❌ [CACHE] 清除关键词搜索缓存失败: {e}")
            return False

    async def invalidate_all_search_cache(self) -> bool:
        """清除所有搜索缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            pattern = f"{self.key_prefix}:*"
            keys = self.redis_client.scan_iter(match=pattern)

            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [CACHE] 所有搜索缓存已清除: {deleted_count}个Key")
            return True

        except Exception as e:
            print(f"❌ [CACHE] 清除所有搜索缓存失败: {e}")
            return False

    async def get_search_cache_stats(self) -> Dict[str, Any]:
        """获取搜索缓存统计信息"""
        try:
            stats = {
                "total_search_keys": 0,
                "cache_size_bytes": 0,
                "unique_keywords": set(),
                "sample_keys": []
            }

            if not self.redis_client.is_available():
                stats["error"] = "Redis不可用"
                return stats

            # 获取所有搜索缓存Key
            pattern = f"{self.key_prefix}:*"
            keys = list(self.redis_client.scan_iter(match=pattern))

            stats["total_search_keys"] = len(keys)
            stats["sample_keys"] = keys[:5]  # 取前5个作为样本

            # 统计缓存大小和关键词
            total_size = 0
            for key in keys:
                try:
                    # 获取Key的大小
                    value = self.redis_client.get(key)
                    if value:
                        total_size += len(value)

                    # 提取关键词哈希
                    if ":keyword_" in key:
                        keyword_hash = key.split(":keyword_")[1].split(":")[0]
                        stats["unique_keywords"].add(keyword_hash)

                except Exception:
                    continue

            stats["cache_size_bytes"] = total_size
            stats["unique_keywords"] = len(stats["unique_keywords"])

            print(f"📊 [CACHE] 搜索缓存统计: {stats}")
            return stats

        except Exception as e:
            print(f"❌ [CACHE] 获取搜索缓存统计失败: {e}")
            return {"error": str(e)}


# 全局实例
search_cache_service = SearchCacheService()