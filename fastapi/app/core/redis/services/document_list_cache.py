"""
文档列表缓存服务
功能：专门处理文档列表查询的缓存逻辑
"""
import json
import time
import hashlib
from typing import Dict, Any, Optional, Union
from sqlalchemy.orm import Session

from ..client import RedisClient


class DocumentListCacheService:
    """文档列表缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient()

        # 缓存配置
        self.public_list_ttl = 600  # 技术广场列表：10分钟
        self.user_list_ttl = 1200  # 个人文档列表：20分钟
        self.key_prefix = "doc_list"

        print(f"📄 [DOC_LIST_CACHE] 文档列表缓存服务初始化")
        print(f"📄 [DOC_LIST_CACHE] 公开列表TTL: {self.public_list_ttl}秒")
        print(f"📄 [DOC_LIST_CACHE] 用户列表TTL: {self.user_list_ttl}秒")
        print(f"📄 [DOC_LIST_CACHE] Redis可用: {self.redis_client.is_available()}")

    def _generate_search_hash(self, search_text: Optional[str]) -> str:
        """生成搜索关键词的哈希值（避免Key过长）"""
        if not search_text:
            return "none"

        # 使用MD5生成短哈希
        hash_obj = hashlib.md5(search_text.encode('utf-8'))
        hash_value = hash_obj.hexdigest()[:8]  # 取前8位

        print(f"🔍 [DOC_LIST_CACHE] 搜索词哈希: '{search_text}' -> {hash_value}")
        return hash_value

    def _build_public_cache_key(
            self,
            page: int,
            size: int,
            search: Optional[str] = None,
            file_type: Optional[str] = None,
            time_filter: Optional[str] = None,
            sort_by: str = "latest"
    ) -> str:
        """构建技术广场文档列表缓存Key"""

        # 处理可选参数
        search_hash = self._generate_search_hash(search)
        file_type_str = file_type or "none"
        time_filter_str = time_filter or "none"

        # 构建缓存Key
        key = f"{self.key_prefix}:public:p{page}:s{size}:q{search_hash}:t{file_type_str}:time{time_filter_str}:sort{sort_by}"

        print(f"🔑 [DOC_LIST_CACHE] 构建公开列表缓存Key: {key}")
        print(
            f"🔑 [DOC_LIST_CACHE] 参数详情: page={page}, size={size}, search='{search}', type={file_type_str}, time={time_filter_str}, sort={sort_by}")

        return key

    def _build_user_cache_key(
            self,
            user_id: int,
            page: int,
            size: int,
            folder_id: Optional[int] = None
    ) -> str:
        """构建个人文档列表缓存Key"""

        folder_str = str(folder_id) if folder_id is not None else "none"
        key = f"{self.key_prefix}:user{user_id}:p{page}:s{size}:f{folder_str}"

        print(f"🔑 [DOC_LIST_CACHE] 构建用户列表缓存Key: {key}")
        print(f"🔑 [DOC_LIST_CACHE] 参数详情: user_id={user_id}, page={page}, size={size}, folder_id={folder_id}")

        return key

    async def get_public_document_list(
            self,
            db: Session,
            query_func,  # 传入查询函数
            page: int,
            size: int,
            search: Optional[str] = None,
            file_type: Optional[str] = None,
            time_filter: Optional[str] = None,
            sort_by: str = "latest",
            **kwargs
    ) -> Dict[str, Any]:
        """
        获取技术广场文档列表（缓存优化版）

        Args:
            db: 数据库会话
            query_func: 实际的查询函数
            page: 页码
            size: 每页数量
            search: 搜索关键词
            file_type: 文件类型筛选
            time_filter: 时间筛选
            sort_by: 排序方式
            **kwargs: 其他参数传递给查询函数
        """
        cache_key = self._build_public_cache_key(page, size, search, file_type, time_filter, sort_by)

        print(f"📄 [DOC_LIST_CACHE] 开始获取技术广场文档列表缓存...")
        print(f"📄 [DOC_LIST_CACHE] 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [DOC_LIST_CACHE] 缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key),
                "cache_type": "public_document_list",
                "cache_key": cache_key
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [DOC_LIST_CACHE] 缓存未命中，查询数据库...")
        list_data = await self._query_public_list(db, query_func, page, size, search, file_type, time_filter, sort_by,
                                                  **kwargs)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, list_data, self.public_list_ttl)

        # 添加缓存信息
        list_data["cache_info"] = {
            "cached": False,
            "cache_time": list_data.get("_cache_time"),
            "ttl_remaining": self.public_list_ttl,
            "cache_type": "public_document_list",
            "cache_key": cache_key
        }

        return list_data

    async def get_user_document_list(
            self,
            db: Session,
            query_func,  # 传入查询函数
            user_id: int,
            page: int,
            size: int,
            folder_id: Optional[int] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        获取个人文档列表（缓存优化版）

        Args:
            db: 数据库会话
            query_func: 实际的查询函数
            user_id: 用户ID
            page: 页码
            size: 每页数量
            folder_id: 文件夹ID筛选
            **kwargs: 其他参数传递给查询函数
        """
        cache_key = self._build_user_cache_key(user_id, page, size, folder_id)

        print(f"📄 [DOC_LIST_CACHE] 开始获取用户文档列表缓存...")
        print(f"📄 [DOC_LIST_CACHE] 缓存Key: {cache_key}")

        # 🔍 第一步：尝试从缓存获取
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            print(f"✅ [DOC_LIST_CACHE] 缓存命中! 返回缓存数据")

            # 添加缓存信息
            cached_data["cache_info"] = {
                "cached": True,
                "cache_time": cached_data.get("_cache_time"),
                "ttl_remaining": self.redis_client.ttl(cache_key),
                "cache_type": "user_document_list",
                "cache_key": cache_key
            }

            return cached_data

        # 🗄️ 第二步：缓存未命中，查询数据库
        print(f"❌ [DOC_LIST_CACHE] 缓存未命中，查询数据库...")
        list_data = await self._query_user_list(db, query_func, user_id, page, size, folder_id, **kwargs)

        # 💾 第三步：写入缓存
        await self._save_to_cache(cache_key, list_data, self.user_list_ttl)

        # 添加缓存信息
        list_data["cache_info"] = {
            "cached": False,
            "cache_time": list_data.get("_cache_time"),
            "ttl_remaining": self.user_list_ttl,
            "cache_type": "user_document_list",
            "cache_key": cache_key
        }

        return list_data

    async def _query_public_list(self, db: Session, query_func, page: int, size: int, search: Optional[str],
                                 file_type: Optional[str], time_filter: Optional[str], sort_by: str, **kwargs) -> Dict[
        str, Any]:
        """查询技术广场文档列表（带详细性能监控）"""
        print(f"🗄️ [DOC_LIST_CACHE] 开始技术广场文档列表数据库查询...")
        start_time = time.time()

        try:
            # 调用实际的查询函数
            result = query_func(
                page=page,
                size=size,
                search=search,
                file_type=file_type,
                time_filter=time_filter,
                sort_by=sort_by,
                **kwargs
            )

            query_time = (time.time() - start_time) * 1000

            # 转换为字典格式（如果是Pydantic模型）
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
                    "query_type": "public_document_list",
                    "total_ms": round(query_time, 2),
                    "page": page,
                    "size": size,
                    "total_documents": result_dict.get("total", 0),
                    "returned_documents": len(result_dict.get("documents", []))
                }
            })

            print(f"✅ [DOC_LIST_CACHE] 技术广场列表查询完成，总耗时: {query_time:.2f}ms")
            print(
                f"📊 [DOC_LIST_CACHE] 查询结果: 总数{result_dict.get('total', 0)}, 返回{len(result_dict.get('documents', []))}条")

            return result_dict

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [DOC_LIST_CACHE] 技术广场列表查询失败 ({query_time:.2f}ms): {e}")
            raise

    async def _query_user_list(self, db: Session, query_func, user_id: int, page: int, size: int,
                               folder_id: Optional[int], **kwargs) -> Dict[str, Any]:
        """查询个人文档列表（带详细性能监控）"""
        print(f"🗄️ [DOC_LIST_CACHE] 开始用户文档列表数据库查询...")
        start_time = time.time()

        try:
            # 调用实际的查询函数
            result = query_func(
                db=db,
                user_id=user_id,
                folder_id=folder_id,
                page=page,
                page_size=size,
                **kwargs
            )

            query_time = (time.time() - start_time) * 1000

            # 转换为字典格式（如果是Pydantic模型）
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
                    "query_type": "user_document_list",
                    "total_ms": round(query_time, 2),
                    "user_id": user_id,
                    "folder_id": folder_id,
                    "page": page,
                    "size": size,
                    "total_documents": result_dict.get("total", 0),
                    "returned_documents": len(result_dict.get("documents", []))
                }
            })

            print(f"✅ [DOC_LIST_CACHE] 用户文档列表查询完成，总耗时: {query_time:.2f}ms")
            print(
                f"📊 [DOC_LIST_CACHE] 查询结果: 用户{user_id}, 总数{result_dict.get('total', 0)}, 返回{len(result_dict.get('documents', []))}条")

            return result_dict

        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            print(f"❌ [DOC_LIST_CACHE] 用户文档列表查询失败 ({query_time:.2f}ms): {e}")
            raise

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if not self.redis_client.is_available():
            print(f"⚠️ [DOC_LIST_CACHE] Redis不可用，跳过缓存读取")
            return None

        try:
            start_time = time.time()
            cached_str = self.redis_client.get(cache_key)
            read_time = (time.time() - start_time) * 1000

            if cached_str:
                data = json.loads(cached_str)
                print(f"💾 [DOC_LIST_CACHE] 缓存读取成功 ({read_time:.2f}ms), 数据大小: {len(cached_str)} bytes")
                return data
            else:
                print(f"💾 [DOC_LIST_CACHE] 缓存Key不存在 ({read_time:.2f}ms)")
                return None

        except Exception as e:
            print(f"❌ [DOC_LIST_CACHE] 缓存读取失败: {e}")
            return None

    async def _save_to_cache(self, cache_key: str, data: Dict[str, Any], ttl: int) -> bool:
        """保存数据到缓存"""
        if not self.redis_client.is_available():
            print(f"⚠️ [DOC_LIST_CACHE] Redis不可用，跳过缓存写入")
            return False

        try:
            start_time = time.time()
            data_str = json.dumps(data, ensure_ascii=False, default=str)  # default=str处理datetime等类型
            success = self.redis_client.setex(cache_key, ttl, data_str)
            write_time = (time.time() - start_time) * 1000

            if success:
                print(f"💾 [DOC_LIST_CACHE] 缓存写入成功 ({write_time:.2f}ms)")
                print(f"💾 [DOC_LIST_CACHE] 数据大小: {len(data_str)} bytes, TTL: {ttl}秒")
                return True
            else:
                print(f"⚠️ [DOC_LIST_CACHE] 缓存写入失败 ({write_time:.2f}ms)")
                return False

        except Exception as e:
            print(f"❌ [DOC_LIST_CACHE] 缓存写入异常: {e}")
            return False

    async def invalidate_public_list_cache(self, pattern: str = "doc_list:public:*") -> int:
        """清除技术广场文档列表缓存（当有新文档发布时调用）"""
        if not self.redis_client.is_available():
            print(f"⚠️ [DOC_LIST_CACHE] Redis不可用，无法清除缓存")
            return 0

        try:
            # 获取匹配的Key
            keys = self.redis_client.keys(pattern)
            if not keys:
                print(f"ℹ️ [DOC_LIST_CACHE] 没有找到匹配的公开列表缓存Key")
                return 0

            # 批量删除
            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [DOC_LIST_CACHE] 已清除{deleted_count}个技术广场列表缓存")
            return deleted_count

        except Exception as e:
            print(f"❌ [DOC_LIST_CACHE] 清除公开列表缓存失败: {e}")
            return 0

    async def invalidate_user_list_cache(self, user_id: int) -> int:
        """清除指定用户的文档列表缓存（当用户文档变更时调用）"""
        if not self.redis_client.is_available():
            print(f"⚠️ [DOC_LIST_CACHE] Redis不可用，无法清除缓存")
            return 0

        try:
            pattern = f"doc_list:user{user_id}:*"
            keys = self.redis_client.keys(pattern)

            if not keys:
                print(f"ℹ️ [DOC_LIST_CACHE] 没有找到用户{user_id}的列表缓存")
                return 0

            # 批量删除
            deleted_count = 0
            for key in keys:
                if self.redis_client.delete(key):
                    deleted_count += 1

            print(f"✅ [DOC_LIST_CACHE] 已清除用户{user_id}的{deleted_count}个列表缓存")
            return deleted_count

        except Exception as e:
            print(f"❌ [DOC_LIST_CACHE] 清除用户列表缓存失败: {e}")
            return 0


# 全局实例
document_list_cache_service = DocumentListCacheService()