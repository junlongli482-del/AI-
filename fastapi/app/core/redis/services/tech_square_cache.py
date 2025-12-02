"""
技术广场统计缓存服务
功能：专门处理技术广场统计数据的缓存逻辑
"""
import json
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from ..client import RedisClient
from ....modules.v2.document_publish.models import PublishRecord
from ....modules.v2.document_manager.models import Document


class TechSquareStatsCacheService:
    """技术广场统计缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient()

        # 缓存配置 - 技术广场数据变化更频繁，TTL设置更短
        self.ttl = 900  # 15分钟
        self.key_prefix = "stats"
        self.cache_key = f"{self.key_prefix}:tech_square:global"

        print(f"🏛️ [TECH_SQUARE_CACHE] 技术广场统计缓存服务初始化")
        print(f"🏛️ [TECH_SQUARE_CACHE] TTL: {self.ttl}秒, Redis可用: {self.redis_client.is_available()}")
        print(f"🏛️ [TECH_SQUARE_CACHE] 缓存Key: {self.cache_key}")

    async def get_tech_square_stats(self, db: Session) -> Dict[str, Any]:
        """
        获取技术广场统计信息（缓存优化版）

        统计内容：
        - 总发布文档数
        - 总浏览量
        - 今日发布数
        - 精选文档数
        - 分类统计（MD/PDF）
        """
        print(f"🏛️ [TECH_SQUARE_CACHE] 开始获取技术广场统计缓存...")
        print(f"🏛️ [TECH_SQUARE_CACHE] 缓存Key: {self.cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache()
        if cached_data:
            print(f"✅ [TECH_SQUARE_CACHE] 缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(self.cache_key),
                "cache_type": "tech_square_stats"
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [TECH_SQUARE_CACHE] 缓存未命中，查询数据库...")
        stats_data = await self._query_database_stats(db)

        # 💾 第三步：写入缓存
        await self._save_to_cache(stats_data)

        # 添加缓存信息
        stats_data["cache_info"] = {
            "cached": False,
            "cache_time": stats_data.get("_cache_time"),
            "ttl_remaining": self.ttl,
            "cache_type": "tech_square_stats"
        }

        return stats_data

    async def _query_database_stats(self, db: Session) -> Dict[str, Any]:
        """查询数据库统计数据（带详细性能监控）"""
        print(f"🗄️ [TECH_SQUARE_CACHE] 开始数据库查询...")
        start_time = time.time()

        try:
            # 查询1：总发布文档数
            query1_start = time.time()
            total_documents = db.query(PublishRecord).filter(
                PublishRecord.publish_status == 'published'
            ).count()
            query1_time = (time.time() - query1_start) * 1000
            print(f"🗄️ [TECH_SQUARE_CACHE] 查询1完成: 总发布文档数 = {total_documents} ({query1_time:.2f}ms)")

            # 查询2：总浏览量
            query2_start = time.time()
            total_views = db.query(
                func.sum(PublishRecord.view_count)
            ).filter(
                PublishRecord.publish_status == 'published'
            ).scalar() or 0
            query2_time = (time.time() - query2_start) * 1000
            print(f"🗄️ [TECH_SQUARE_CACHE] 查询2完成: 总浏览量 = {total_views} ({query2_time:.2f}ms)")

            # 查询3：今日发布数
            query3_start = time.time()
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_published = db.query(PublishRecord).filter(
                PublishRecord.publish_status == 'published',
                PublishRecord.publish_time >= today_start
            ).count()
            query3_time = (time.time() - query3_start) * 1000
            print(f"🗄️ [TECH_SQUARE_CACHE] 查询3完成: 今日发布数 = {today_published} ({query3_time:.2f}ms)")

            # 查询4：精选文档数
            query4_start = time.time()
            featured_count = db.query(PublishRecord).filter(
                PublishRecord.publish_status == 'published',
                PublishRecord.is_featured == True
            ).count()
            query4_time = (time.time() - query4_start) * 1000
            print(f"🗄️ [TECH_SQUARE_CACHE] 查询4完成: 精选文档数 = {featured_count} ({query4_time:.2f}ms)")

            # 查询5：分类统计（MD/PDF）
            query5_start = time.time()
            category_stats = db.query(
                Document.file_type,
                func.count(Document.id)
            ).join(
                PublishRecord, Document.id == PublishRecord.document_id
            ).filter(
                PublishRecord.publish_status == 'published'
            ).group_by(Document.file_type).all()
            query5_time = (time.time() - query5_start) * 1000
            print(f"🗄️ [TECH_SQUARE_CACHE] 查询5完成: 分类统计 = {len(category_stats)}种类型 ({query5_time:.2f}ms)")

            # 格式化分类统计
            category_dict = {'md': 0, 'pdf': 0}
            for file_type, count in category_stats:
                if file_type in category_dict:
                    category_dict[file_type] = count

            # 构建结果
            result = {
                "total_documents": total_documents,
                "total_views": int(total_views),
                "today_published": today_published,
                "featured_count": featured_count,
                "category_stats": {
                    "md_count": category_dict['md'],
                    "pdf_count": category_dict['pdf'],
                    "total_count": category_dict['md'] + category_dict['pdf']
                },
                "_cache_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "_query_performance": {
                    "total_documents_ms": round(query1_time, 2),
                    "total_views_ms": round(query2_time, 2),
                    "today_published_ms": round(query3_time, 2),
                    "featured_count_ms": round(query4_time, 2),
                    "category_stats_ms": round(query5_time, 2),
                    "total_ms": round((time.time() - start_time) * 1000, 2)
                }
            }

            total_time = (time.time() - start_time) * 1000
            print(f"✅ [TECH_SQUARE_CACHE] 数据库查询完成，总耗时: {total_time:.2f}ms")
            print(
                f"📊 [TECH_SQUARE_CACHE] 统计结果: 文档{total_documents}篇, 浏览{total_views}次, 今日{today_published}篇, 精选{featured_count}篇")

            return result

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [TECH_SQUARE_CACHE] 数据库查询失败 ({query_time:.2f}ms): {e}")
            raise

    async def _get_from_cache(self) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if not self.redis_client.is_available():
            print(f"⚠️ [TECH_SQUARE_CACHE] Redis不可用，跳过缓存读取")
            return None

        try:
            start_time = time.time()
            cached_str = self.redis_client.get(self.cache_key)
            read_time = (time.time() - start_time) * 1000

            if cached_str:
                data = json.loads(cached_str)
                print(f"💾 [TECH_SQUARE_CACHE] 缓存读取成功 ({read_time:.2f}ms), 数据大小: {len(cached_str)} bytes")
                return data
            else:
                print(f"💾 [TECH_SQUARE_CACHE] 缓存Key不存在 ({read_time:.2f}ms)")
                return None

        except Exception as e:
            print(f"❌ [TECH_SQUARE_CACHE] 缓存读取失败: {e}")
            return None

    async def _save_to_cache(self, data: Dict[str, Any]) -> bool:
        """保存数据到缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [TECH_SQUARE_CACHE] Redis不可用，跳过缓存写入")
            return False

        try:
            start_time = time.time()
            data_str = json.dumps(data, ensure_ascii=False)
            success = self.redis_client.setex(self.cache_key, self.ttl, data_str)
            write_time = (time.time() - start_time) * 1000

            if success:
                print(f"💾 [TECH_SQUARE_CACHE] 缓存写入成功 ({write_time:.2f}ms)")
                print(f"💾 [TECH_SQUARE_CACHE] 数据大小: {len(data_str)} bytes, TTL: {self.ttl}秒")
                return True
            else:
                print(f"⚠️ [TECH_SQUARE_CACHE] 缓存写入失败 ({write_time:.2f}ms)")
                return False

        except Exception as e:
            print(f"❌ [TECH_SQUARE_CACHE] 缓存写入异常: {e}")
            return False

    async def invalidate_cache(self) -> bool:
        """清除技术广场统计缓存（当有文档发布/删除时调用）"""
        if not self.redis_client.is_available():
            print(f"⚠️ [TECH_SQUARE_CACHE] Redis不可用，无法清除缓存")
            return False

        try:
            result = self.redis_client.delete(self.cache_key)
            if result:
                print(f"✅ [TECH_SQUARE_CACHE] 技术广场统计缓存已清除: {self.cache_key}")
            else:
                print(f"ℹ️ [TECH_SQUARE_CACHE] 缓存Key不存在，无需清除: {self.cache_key}")
            return bool(result)

        except Exception as e:
            print(f"❌ [TECH_SQUARE_CACHE] 清除缓存失败: {e}")
            return False


# 全局实例
tech_square_stats_cache_service = TechSquareStatsCacheService()