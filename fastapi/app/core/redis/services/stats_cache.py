"""
统计数据缓存服务
功能：专门处理统计数据的缓存逻辑
"""
import json
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..client import RedisClient
from ....modules.v2.document_manager.models import Document, Folder, DocumentStatus


class StatsCacheService:
    """统计缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient()

        # 缓存配置
        self.ttl = 1800  # 30分钟 (统计数据变化不频繁)
        self.key_prefix = "stats"

        print(f"💾 [CACHE] 统计缓存服务初始化")
        print(f"💾 [CACHE] TTL: {self.ttl}秒, Redis可用: {self.redis_client.is_available()}")

    def _build_cache_key(self, cache_type: str, user_id: int) -> str:
        """构建缓存Key"""
        key = f"{self.key_prefix}:{cache_type}:{user_id}"
        print(f"🔑 [CACHE] 构建缓存Key: {key}")
        return key

    async def get_user_document_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取用户文档统计信息（缓存优化版）
        """
        cache_key = self._build_cache_key("user_docs", user_id)

        print(f"💾 [CACHE] 开始获取用户统计缓存...")
        print(f"💾 [CACHE] 用户ID: {user_id}, 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [CACHE] 缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key)
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [CACHE] 缓存未命中，查询数据库...")
        stats_data = await self._query_database_stats(db, user_id)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, stats_data)

        # 添加缓存信息
        stats_data["cache_info"] = {
            "cached": False,
            "cache_time": stats_data.get("_cache_time"),
            "ttl_remaining": self.ttl
        }

        return stats_data

    async def _query_database_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """查询数据库统计数据（带性能监控）"""
        print(f"🗄️ [CACHE] 开始数据库查询...")
        start_time = time.time()

        try:
            # 查询1：总文档数
            query1_start = time.time()
            total_docs = db.query(Document).filter(Document.user_id == user_id).count()
            query1_time = (time.time() - query1_start) * 1000
            print(f"🗄️ [CACHE] 查询1完成: 总文档数 = {total_docs} ({query1_time:.2f}ms)")

            # 查询2：按状态统计
            query2_start = time.time()
            status_stats = db.query(
                Document.status,
                func.count(Document.id)
            ).filter(
                Document.user_id == user_id
            ).group_by(Document.status).all()
            query2_time = (time.time() - query2_start) * 1000
            print(f"🗄️ [CACHE] 查询2完成: 状态统计 = {len(status_stats)}种状态 ({query2_time:.2f}ms)")

            # 查询3：文件夹数量
            query3_start = time.time()
            total_folders = db.query(Folder).filter(Folder.user_id == user_id).count()
            query3_time = (time.time() - query3_start) * 1000
            print(f"🗄️ [CACHE] 查询3完成: 文件夹数 = {total_folders} ({query3_time:.2f}ms)")

            # 格式化状态统计
            status_dict = {status.value: 0 for status in DocumentStatus}
            for status, count in status_stats:
                status_dict[status] = count

            # 构建结果
            result = {
                "total_documents": total_docs,
                "total_folders": total_folders,
                "documents_by_status": status_dict,
                "user_id": user_id,
                "_cache_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "_query_performance": {
                    "total_docs_ms": round(query1_time, 2),
                    "status_stats_ms": round(query2_time, 2),
                    "total_folders_ms": round(query3_time, 2),
                    "total_ms": round((time.time() - start_time) * 1000, 2)
                }
            }

            total_time = (time.time() - start_time) * 1000
            print(f"✅ [CACHE] 数据库查询完成，总耗时: {total_time:.2f}ms")

            return result

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [CACHE] 数据库查询失败 ({query_time:.2f}ms): {e}")
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
            data_str = json.dumps(data, ensure_ascii=False)
            success = self.redis_client.setex(cache_key, self.ttl, data_str)
            write_time = (time.time() - start_time) * 1000

            if success:
                print(f"💾 [CACHE] 缓存写入成功 ({write_time:.2f}ms)")
                print(f"💾 [CACHE] 数据大小: {len(data_str)} bytes, TTL: {self.ttl}秒")
                return True
            else:
                print(f"⚠️ [CACHE] 缓存写入失败 ({write_time:.2f}ms)")
                return False

        except Exception as e:
            print(f"❌ [CACHE] 缓存写入异常: {e}")
            return False

    async def invalidate_user_stats(self, user_id: int) -> bool:
        """清除用户统计缓存（当数据变更时调用）"""
        cache_key = self._build_cache_key("user_docs", user_id)

        if not self.redis_client.is_available():
            print(f"⚠️ [CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            result = self.redis_client.delete(cache_key)
            if result:
                print(f"✅ [CACHE] 用户统计缓存已清除: {cache_key}")
            else:
                print(f"ℹ️ [CACHE] 缓存Key不存在，无需清除: {cache_key}")
            return bool(result)

        except Exception as e:
            print(f"❌ [CACHE] 清除缓存失败: {e}")
            return False


# 全局实例
stats_cache_service = StatsCacheService()