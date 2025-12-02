# app/modules/v2/tech_square/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
# 在文件最顶部添加
import time
# 修复导入路径 - 使用相对路径
from ....core.database import get_db  # 修改这行
from .services import TechSquareService
# 在现有导入中添加
from fastapi.responses import FileResponse, StreamingResponse
from .schemas import (
    DocumentListRequest, DocumentListResponse, DocumentDetailResponse,
    CategoryStatsResponse, HotDocumentsResponse, TechSquareStatsResponse,
    SearchRequest, SortOption, TimeFilter, FileTypeFilter,
    DocumentFileInfoResponse  # 新增
)
# 🆕 导入技术广场统计缓存服务# 🆕 导入缓存服务# 🆕 导入热门数据缓存服务
from ....core.redis.services import tech_square_stats_cache_service, document_list_cache_service, hot_data_cache_service, search_cache_service
router = APIRouter()

# 后面的代码保持不变...


@router.get("/test")
async def test_tech_square():
    """测试技术广场模块连通性"""
    return {
        "status": "success",
        "message": "Tech Square模块运行正常",
        "module": "tech_square",
        "version": "v2"
    }


@router.get("/documents", response_model=DocumentListResponse)
async def get_document_list(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
        file_type: Optional[FileTypeFilter] = Query(None, description="文件类型筛选"),
        time_filter: Optional[TimeFilter] = Query(None, description="时间筛选"),
        sort_by: SortOption = Query(SortOption.LATEST, description="排序方式"),
        db: Session = Depends(get_db)
):
    """
    获取文档列表（Redis缓存优化版）

    支持功能：
    - 分页查询
    - 关键词搜索（标题、摘要）
    - 文件类型筛选（md/pdf）
    - 时间筛选（今日/本周/本月）
    - 多种排序（最新/最热/推荐）

    性能优化：
    - ✅ Redis缓存：10分钟TTL
    - ✅ 智能缓存Key：基于查询参数生成
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    - ✅ 详细性能监控和调试信息
    """
    print("📄 [TECH_SQUARE_DOCS] 开始获取技术广场文档列表（缓存版）")
    print(
        f"📄 [TECH_SQUARE_DOCS] 查询参数: page={page}, size={size}, search='{search}', type={file_type}, time={time_filter}, sort={sort_by}")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取文档列表
        def query_function(**kwargs):
            """实际的数据库查询函数"""
            print(f"🗄️ [TECH_SQUARE_DOCS] 执行数据库查询...")

            # 构建请求对象
            request = DocumentListRequest(
                page=kwargs['page'],
                size=kwargs['size'],
                search=kwargs['search'],
                file_type=kwargs['file_type'],
                time_filter=kwargs['time_filter'],
                sort_by=kwargs['sort_by']
            )

            # 调用原有服务
            service = TechSquareService(db)
            return service.get_document_list(request)

        # 转换枚举参数为字符串
        file_type_str = file_type.value if file_type else None
        time_filter_str = time_filter.value if time_filter else None
        sort_by_str = sort_by.value

        result = await document_list_cache_service.get_public_document_list(
            db=db,
            query_func=query_function,
            page=page,
            size=size,
            search=search,
            file_type=file_type_str,
            time_filter=time_filter_str,
            sort_by=sort_by_str
        )

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False)
        print(f"📄 [TECH_SQUARE_DOCS] 文档列表获取完成，总耗时: {total_time:.2f}ms")
        print(f"📄 [TECH_SQUARE_DOCS] 缓存状态: {'命中' if is_cached else '未命中'}")
        print(
            f"📄 [TECH_SQUARE_DOCS] 返回结果: 总数{result.get('total', 0)}, 当前页{len(result.get('documents', []))}条")

        # 添加路由层的性能信息
        result["_route_debug_info"] = {
            "route_total_time_ms": round(total_time, 2),
            "cache_hit": is_cached,
            "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存",
            "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query_params": {
                "page": page,
                "size": size,
                "search": search,
                "file_type": file_type_str,
                "time_filter": time_filter_str,
                "sort_by": sort_by_str
            }
        }

        if is_cached:
            print(f"✅ [TECH_SQUARE_DOCS] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [TECH_SQUARE_DOCS] 缓存未命中，已查询数据库并写入缓存")

        # 转换为响应模型
        if isinstance(result, dict):
            # 如果是字典，需要转换为Pydantic模型
            return DocumentListResponse(**result)
        else:
            # 如果已经是模型，直接返回
            return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [TECH_SQUARE_DOCS] 获取文档列表失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [TECH_SQUARE_DOCS] 尝试使用原有服务作为降级方案...")
        try:
            request = DocumentListRequest(
                page=page,
                size=size,
                search=search,
                file_type=file_type,
                time_filter=time_filter,
                sort_by=sort_by
            )

            service = TechSquareService(db)
            fallback_result = service.get_document_list(request)

            print(f"✅ [TECH_SQUARE_DOCS] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_result._fallback_info = {
                    "used_fallback": True,
                    "fallback_reason": str(e),
                    "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            return fallback_result

        except Exception as fallback_error:
            print(f"❌ [TECH_SQUARE_DOCS] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取文档列表失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )

@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document_detail(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    获取文档详情

    返回已发布文档的完整信息，包括内容
    """
    try:
        service = TechSquareService(db)
        document = service.get_document_detail(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在或未发布")

        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档详情失败: {str(e)}")


@router.get("/search", response_model=DocumentListResponse)
async def search_documents(
        keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=50, description="每页数量"),
        file_type: Optional[FileTypeFilter] = Query(None, description="文件类型筛选"),
        db: Session = Depends(get_db)
):
    """
    搜索文档（Redis缓存优化版）

    智能搜索功能：
    - 标题匹配
    - 摘要内容匹配
    - 支持文件类型筛选

    性能优化：
    - ✅ Redis缓存：8分钟TTL
    - ✅ 智能Key设计：关键词哈希化 + 参数隔离
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    - ✅ 详细性能监控和调试信息
    """
    print("🔍 [SEARCH] 开始搜索文档（缓存版）")
    print(f"🔍 [SEARCH] 搜索参数: keyword='{keyword}', page={page}, size={size}, file_type={file_type}")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取搜索结果
        def query_function(**kwargs):
            """实际的数据库查询函数"""
            print(f"🗄️ [SEARCH] 执行数据库搜索查询...")

            # 构建搜索请求对象
            request = SearchRequest(
                keyword=kwargs['keyword'],
                page=kwargs['page'],
                size=kwargs['size'],
                file_type=FileTypeFilter(kwargs['file_type']) if kwargs['file_type'] else None
            )

            # 调用原有服务
            service = TechSquareService(db)
            return service.search_documents(request)

        # 转换枚举参数为字符串
        file_type_str = file_type.value if file_type else None

        result = await search_cache_service.get_search_results(
            db=db,
            query_func=query_function,
            keyword=keyword,
            page=page,
            size=size,
            file_type=file_type_str
        )

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False) if result else False
        print(f"🔍 [SEARCH] 搜索完成，总耗时: {total_time:.2f}ms")
        print(f"🔍 [SEARCH] 缓存状态: {'命中' if is_cached else '未命中'}")
        print(f"🔍 [SEARCH] 搜索结果: 当前页{len(result.get('documents', []))}条, 总计{result.get('total', 0)}条")

        # 添加路由层的性能信息
        if result:
            result["_route_debug_info"] = {
                "route_total_time_ms": round(total_time, 2),
                "cache_hit": is_cached,
                "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次搜索，已写入缓存",
                "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "search_params": {
                    "keyword": keyword,
                    "page": page,
                    "size": size,
                    "file_type": file_type_str
                }
            }

        if is_cached:
            print(f"✅ [SEARCH] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [SEARCH] 缓存未命中，已查询数据库并写入缓存")

        # 转换为响应模型
        if isinstance(result, dict):
            return DocumentListResponse(**result)
        else:
            return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [SEARCH] 搜索失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [SEARCH] 尝试使用原有服务作为降级方案...")
        try:
            request = SearchRequest(
                keyword=keyword,
                page=page,
                size=size,
                file_type=file_type
            )

            service = TechSquareService(db)
            fallback_result = service.search_documents(request)

            print(f"✅ [SEARCH] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_result._fallback_info = {
                    "used_fallback": True,
                    "fallback_reason": str(e),
                    "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            return fallback_result

        except Exception as fallback_error:
            print(f"❌ [SEARCH] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"搜索文档失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )

@router.get("/category-stats", response_model=CategoryStatsResponse)
async def get_category_stats(db: Session = Depends(get_db)):
    """
    获取分类统计信息

    返回各文件类型的文档数量
    """
    try:
        service = TechSquareService(db)
        return service.get_category_stats()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类统计失败: {str(e)}")


@router.get("/hot-documents", response_model=HotDocumentsResponse)
async def get_hot_documents(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db)
):
    """
    获取热门文档（Redis缓存优化版）

    按浏览量降序排序

    性能优化：
    - ✅ Redis缓存：10分钟TTL
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    - ✅ 详细性能监控和调试信息
    """
    print("🔥 [HOT_DOCS] 开始获取热门文档（缓存版）")
    print(f"🔥 [HOT_DOCS] 查询参数: limit={limit}")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取热门文档
        def query_function(**kwargs):
            """实际的数据库查询函数"""
            print(f"🗄️ [HOT_DOCS] 执行数据库查询...")
            service = TechSquareService(db)
            return service.get_hot_documents(kwargs['limit'])

        result = await hot_data_cache_service.get_hot_documents(
            db=db,
            query_func=query_function,
            limit=limit
        )

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False) if result else False
        print(f"🔥 [HOT_DOCS] 热门文档获取完成，总耗时: {total_time:.2f}ms")
        print(f"🔥 [HOT_DOCS] 缓存状态: {'命中' if is_cached else '未命中'}")
        print(f"🔥 [HOT_DOCS] 返回结果: {len(result.get('documents', [])) if result else 0}条")

        # 添加路由层的性能信息
        if result:
            result["_route_debug_info"] = {
                "route_total_time_ms": round(total_time, 2),
                "cache_hit": is_cached,
                "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存",
                "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "query_params": {"limit": limit}
            }

        if is_cached:
            print(f"✅ [HOT_DOCS] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [HOT_DOCS] 缓存未命中，已查询数据库并写入缓存")

        # 转换为响应模型
        if isinstance(result, dict):
            return HotDocumentsResponse(**result)
        else:
            return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [HOT_DOCS] 获取热门文档失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [HOT_DOCS] 尝试使用原有服务作为降级方案...")
        try:
            service = TechSquareService(db)
            fallback_result = service.get_hot_documents(limit)

            print(f"✅ [HOT_DOCS] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_result._fallback_info = {
                    "used_fallback": True,
                    "fallback_reason": str(e),
                    "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            return fallback_result

        except Exception as fallback_error:
            print(f"❌ [HOT_DOCS] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取热门文档失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )
@router.get("/latest-documents", response_model=HotDocumentsResponse)
async def get_latest_documents(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db)
):
    """
    获取最新发布文档（Redis缓存优化版）

    按发布时间降序排序

    性能优化：
    - ✅ Redis缓存：5分钟TTL
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    - ✅ 详细性能监控和调试信息
    """
    print("📅 [LATEST_DOCS] 开始获取最新文档（缓存版）")
    print(f"📅 [LATEST_DOCS] 查询参数: limit={limit}")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取最新文档
        def query_function(**kwargs):
            """实际的数据库查询函数"""
            print(f"🗄️ [LATEST_DOCS] 执行数据库查询...")
            service = TechSquareService(db)
            return service.get_latest_documents(kwargs['limit'])

        result = await hot_data_cache_service.get_latest_documents(
            db=db,
            query_func=query_function,
            limit=limit
        )

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False) if result else False
        print(f"📅 [LATEST_DOCS] 最新文档获取完成，总耗时: {total_time:.2f}ms")
        print(f"📅 [LATEST_DOCS] 缓存状态: {'命中' if is_cached else '未命中'}")
        print(f"📅 [LATEST_DOCS] 返回结果: {len(result.get('documents', [])) if result else 0}条")

        # 添加路由层的性能信息
        if result:
            result["_route_debug_info"] = {
                "route_total_time_ms": round(total_time, 2),
                "cache_hit": is_cached,
                "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存",
                "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "query_params": {"limit": limit}
            }

        if is_cached:
            print(f"✅ [LATEST_DOCS] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [LATEST_DOCS] 缓存未命中，已查询数据库并写入缓存")

        # 转换为响应模型
        if isinstance(result, dict):
            return HotDocumentsResponse(**result)
        else:
            return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [LATEST_DOCS] 获取最新文档失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [LATEST_DOCS] 尝试使用原有服务作为降级方案...")
        try:
            service = TechSquareService(db)
            fallback_result = service.get_latest_documents(limit)

            print(f"✅ [LATEST_DOCS] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_result._fallback_info = {
                    "used_fallback": True,
                    "fallback_reason": str(e),
                    "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            return fallback_result

        except Exception as fallback_error:
            print(f"❌ [LATEST_DOCS] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取最新文档失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )

@router.get("/stats", response_model=TechSquareStatsResponse)
async def get_tech_square_stats(db: Session = Depends(get_db)):
    """
    获取技术广场统计信息（Redis缓存优化版）

    统计内容：
    - 总文档数、总浏览量
    - 今日发布数、精选文档数
    - 分类统计（MD/PDF）

    性能优化：
    - ✅ Redis缓存：15分钟TTL
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    - ✅ 详细性能监控和调试信息
    """
    print("🏛️ [TECH_SQUARE_STATS] 开始获取技术广场统计数据（缓存版）")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取统计数据
        result = await tech_square_stats_cache_service.get_tech_square_stats(db)

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False)
        print(f"🏛️ [TECH_SQUARE_STATS] 统计数据获取完成，总耗时: {total_time:.2f}ms")
        print(f"🏛️ [TECH_SQUARE_STATS] 缓存状态: {'命中' if is_cached else '未命中'}")

        # 添加路由层的性能信息
        result["_route_debug_info"] = {
            "route_total_time_ms": round(total_time, 2),
            "cache_hit": is_cached,
            "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存",
            "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if is_cached:
            print(f"✅ [TECH_SQUARE_STATS] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [TECH_SQUARE_STATS] 缓存未命中，已查询数据库并写入缓存")

        return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [TECH_SQUARE_STATS] 获取统计信息失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [TECH_SQUARE_STATS] 尝试使用原有服务作为降级方案...")
        try:
            service = TechSquareService(db)
            fallback_result = service.get_tech_square_stats()

            print(f"✅ [TECH_SQUARE_STATS] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_dict = fallback_result.__dict__
            else:
                fallback_dict = fallback_result

            fallback_dict["_fallback_info"] = {
                "used_fallback": True,
                "fallback_reason": str(e),
                "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return fallback_dict

        except Exception as fallback_error:
            print(f"❌ [TECH_SQUARE_STATS] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取统计信息失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )
@router.post("/view/{document_id}")
async def increment_view_count(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    增加文档浏览量

    用于前端访问文档时调用
    """
    try:
        service = TechSquareService(db)
        success = service.increment_view_count(document_id)

        if not success:
            raise HTTPException(status_code=404, detail="文档不存在或未发布")

        return {"status": "success", "message": "浏览量已增加"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新浏览量失败: {str(e)}")


# ==================== 🆕 文件访问接口（无需认证） ====================

@router.get("/documents/{document_id}/download", summary="下载文档文件")
async def download_document_file(
        document_id: int,
        preview: bool = Query(False, description="是否为预览模式（浏览器内打开）"),
        db: Session = Depends(get_db)
):
    """
    下载已发布文档的文件（无需认证）

    参数：
    - **document_id**: 文档ID
    - **preview**: 预览模式
      - true: 浏览器内预览（适用于PDF）
      - false: 强制下载文件

    功能特点：
    - ✅ 无需认证，公开访问
    - ✅ 只能访问已发布的文档
    - ✅ 支持PDF和Markdown文件
    - ✅ 自动处理中文文件名编码
    - ✅ 支持预览和下载两种模式

    前端调用示例：
    ```javascript
    // 下载文件
    const downloadUrl = `http://localhost:8100/api/v2/tech_square/documents/${docId}/download`

    // 预览PDF（浏览器内打开）
    const previewUrl = `http://localhost:8100/api/v2/tech_square/documents/${docId}/download?preview=true`
    ```
    """
    try:
        service = TechSquareService(db)
        return service.download_document_file(document_id, preview)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文档失败: {str(e)}")


@router.get("/documents/{document_id}/stream", summary="流式传输文档")
async def stream_document_file(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    流式传输已发布文档（无需认证）

    专门优化PDF预览体验：
    - ✅ 分块传输，支持大文件（8KB chunks）
    - ✅ 浏览器自动选择PDF阅读器
    - ✅ 支持断点续传（Accept-Ranges）
    - ✅ 无需认证，公开访问

    推荐用法：
    ```javascript
    // 推荐：直接在新窗口打开PDF
    const pdfUrl = `http://localhost:8100/api/v2/tech_square/documents/${docId}/stream`
    window.open(pdfUrl, '_blank')

    // 或者嵌入到iframe中
    const iframe = document.createElement('iframe')
    iframe.src = pdfUrl
    iframe.width = '100%'
    iframe.height = '600px'
    document.body.appendChild(iframe)
    ```

    浏览器兼容性：
    - ✅ Chrome/Edge: 完美支持PDF内嵌预览
    - ✅ Firefox: 支持PDF预览和下载
    - ✅ Safari: 支持PDF预览
    - ✅ 移动端: 自动调用系统PDF阅读器
    """
    try:
        service = TechSquareService(db)
        return service.stream_document_file(document_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档流失败: {str(e)}")


@router.get("/documents/{document_id}/info", response_model=DocumentFileInfoResponse, summary="获取文档文件信息")
async def get_document_file_info(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    获取已发布文档的文件信息（无需认证）

    功能特点：
    - ✅ 获取文件元信息，不下载内容
    - ✅ 检查文件完整性
    - ✅ 验证文件大小匹配
    - ✅ 提供MIME类型信息
    - ✅ 无需认证，公开访问

    返回信息：
    - 文件名和安全文件名
    - 文件大小（数据库记录 vs 实际文件）
    - 文件类型和MIME类型
    - 是否存在物理文件
    - 文件完整性验证

    使用场景：
    - 前端判断是否显示下载按钮
    - 检查文件是否可用
    - 获取文件基本信息用于展示
    """
    try:
        service = TechSquareService(db)
        return service.get_document_file_info(document_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")