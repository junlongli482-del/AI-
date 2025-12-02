"""
文档管理模块 - 路由定义
功能：定义文档和文件夹管理的API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import time
from datetime import datetime
import mimetypes
import os
from pathlib import Path

from .dependencies import get_db, get_current_active_user, get_db_and_user
from .services import FolderService, DocumentService
from .models import Document, Folder, DocumentStatus
from .schemas import (
    FolderCreateRequest, FolderResponse, FolderTreeResponse,
    DocumentCreateRequest, DocumentUpdateRequest, DocumentResponse,
    DocumentListWithPaginationResponse, SuccessResponse
)
from ....core.redis.services import stats_cache_service, document_list_cache_service
from ....modules.v1.user_register.models import User
# 创建路由器
router = APIRouter()


# ==================== 测试接口 ====================

@router.get("/test")
async def test_module():
    """模块健康检查"""
    return {
        "message": "Document Manager模块运行正常",
        "version": "v2.0",
        "features": ["文档管理", "文件夹管理", "分页查询"]
    }


# ==================== 文件夹管理接口 ====================

@router.post("/folders", response_model=FolderResponse, summary="创建文件夹")
async def create_folder(
        folder_data: FolderCreateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    创建新文件夹

    - **name**: 文件夹名称（1-100字符，不能包含特殊字符）
    - **parent_id**: 父文件夹ID（可选，不填表示根目录）

    限制：
    - 同一位置不能有同名文件夹
    - 最多支持3层文件夹结构
    """
    return FolderService.create_folder(db, folder_data, current_user.id)


@router.get("/folders/tree", response_model=List[FolderTreeResponse], summary="获取文件夹树")
async def get_folder_tree(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的文件夹树形结构

    返回完整的文件夹层级关系，包含每个文件夹下的文档数量
    """
    return FolderService.get_folder_tree(db, current_user.id)


@router.delete("/folders/{folder_id}", response_model=SuccessResponse, summary="删除文件夹")
async def delete_folder(
        folder_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    删除文件夹

    注意：
    - 只能删除空文件夹（无子文件夹和文档）
    - 删除操作不可恢复
    """
    success = FolderService.delete_folder(db, folder_id, current_user.id)
    return SuccessResponse(message="文件夹删除成功")


# ==================== 文档管理接口 ====================

@router.post("/documents", response_model=DocumentResponse, summary="创建文档")
async def create_document(
        doc_data: DocumentCreateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    创建新文档

    - **title**: 文档标题（1-200字符）
    - **content**: 文档内容（Markdown格式，可选）
    - **summary**: 简短摘要（最多500字符，可选）
    - **folder_id**: 所属文件夹ID（可选，不填表示根目录）
    - **file_type**: 文件类型（md或pdf，默认md）

    限制：
    - 同一文件夹下不能有同名文档
    - 新创建的文档默认为草稿状态
    """
    return DocumentService.create_document(db, doc_data, current_user.id)


@router.get("/documents/{doc_id}", response_model=DocumentResponse, summary="获取文档详情")
async def get_document(
        doc_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    获取指定文档的详细信息

    包含完整的文档内容、状态、所属文件夹等信息
    """
    return DocumentService.get_document(db, doc_id, current_user.id)


@router.put("/documents/{doc_id}", response_model=DocumentResponse, summary="更新文档")
async def update_document(
        doc_id: int,
        doc_data: DocumentUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    更新文档信息

    可以更新：
    - 标题
    - 内容
    - 摘要
    - 所属文件夹

    注意：
    - 只能更新自己的文档
    - 更新后文档状态可能需要重新审核
    """
    return DocumentService.update_document(db, doc_id, doc_data, current_user.id)


@router.delete("/documents/{doc_id}", response_model=SuccessResponse, summary="删除文档")
async def delete_document(
        doc_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    删除文档

    注意：
    - 删除操作不可恢复
    - 会同时删除相关的物理文件
    - 如果文档已发布，会从技术广场移除
    """
    success = DocumentService.delete_document(db, doc_id, current_user.id)
    return SuccessResponse(message="文档删除成功")


@router.get("/documents", response_model=DocumentListWithPaginationResponse, summary="获取文档列表")
async def get_documents_list(
        folder_id: Optional[int] = Query(None, description="文件夹ID，不填获取所有文档，0表示根目录"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    获取文档列表（分页）（Redis缓存优化版）

    参数：
    - **folder_id**: 文件夹ID筛选（可选）
      - 不填：获取所有文档
      - 0：获取根目录下的文档
      - 其他数字：获取指定文件夹下的文档
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）

    返回：
    - 文档列表（按更新时间倒序）
    - 分页信息

    性能优化：
    - ✅ Redis缓存：20分钟TTL
    - ✅ 用户隔离缓存：每个用户独立缓存
    - ✅ 文件夹筛选支持：不同文件夹独立缓存
    - ✅ 缓存未命中时自动查询数据库
    - ✅ 优雅降级：Redis不可用时直接查询数据库
    """
    print("📄 [USER_DOCS] 开始获取用户文档列表（缓存版）")
    print(f"📄 [USER_DOCS] 用户ID: {current_user.id}, 查询参数: folder_id={folder_id}, page={page}, size={page_size}")

    try:
        start_time = time.time()

        # 🚀 使用缓存服务获取文档列表
        def query_function(**kwargs):
            """实际的数据库查询函数"""
            print(f"🗄️ [USER_DOCS] 执行数据库查询...")

            # 调用原有服务
            return DocumentService.get_documents_list(
                db=kwargs['db'],
                user_id=kwargs['user_id'],
                folder_id=kwargs['folder_id'],
                page=kwargs['page'],
                page_size=kwargs['page_size']
            )

        result = await document_list_cache_service.get_user_document_list(
            db=db,
            query_func=query_function,
            user_id=current_user.id,
            page=page,
            size=page_size,
            folder_id=folder_id
        )

        total_time = (time.time() - start_time) * 1000

        # 添加路由层的调试信息
        is_cached = result.get("cache_info", {}).get("cached", False)
        print(f"📄 [USER_DOCS] 用户文档列表获取完成，总耗时: {total_time:.2f}ms")
        print(f"📄 [USER_DOCS] 缓存状态: {'命中' if is_cached else '未命中'}")
        print(f"📄 [USER_DOCS] 返回结果: 总数{result.get('total', 0)}, 当前页{len(result.get('documents', []))}条")

        # 添加路由层的性能信息
        result["_route_debug_info"] = {
            "route_total_time_ms": round(total_time, 2),
            "cache_hit": is_cached,
            "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存",
            "route_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query_params": {
                "user_id": current_user.id,
                "folder_id": folder_id,
                "page": page,
                "page_size": page_size
            }
        }

        if is_cached:
            print(f"✅ [USER_DOCS] 缓存命中! 总耗时: {total_time:.2f}ms")
        else:
            print(f"🔄 [USER_DOCS] 缓存未命中，已查询数据库并写入缓存")

        # 转换为响应模型
        if isinstance(result, dict):
            # 如果是字典，需要转换为Pydantic模型
            return DocumentListWithPaginationResponse(**result)
        else:
            # 如果已经是模型，直接返回
            return result

    except Exception as e:
        error_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [USER_DOCS] 获取用户文档列表失败 ({error_time:.2f}ms): {str(e)}")

        # 🛡️ 优雅降级：缓存服务异常时使用原有服务
        print(f"🔄 [USER_DOCS] 尝试使用原有服务作为降级方案...")
        try:
            fallback_result = DocumentService.get_documents_list(db, current_user.id, folder_id, page, page_size)

            print(f"✅ [USER_DOCS] 降级方案成功")

            # 添加降级信息
            if hasattr(fallback_result, '__dict__'):
                fallback_result._fallback_info = {
                    "used_fallback": True,
                    "fallback_reason": str(e),
                    "fallback_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            return fallback_result

        except Exception as fallback_error:
            print(f"❌ [USER_DOCS] 降级方案也失败: {str(fallback_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取文档列表失败: {str(e)}，降级方案也失败: {str(fallback_error)}"
            )

# ==================== 快捷操作接口 ====================

@router.get("/stats", summary="获取统计信息")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户的文档统计信息（Redis缓存优化版）

    包含：
    - 总文档数
    - 各状态文档数量
    - 文件夹数量
    - Redis缓存优化
    - 详细的性能监控信息
    """
    print("🔍 [STATS] =========================")
    print(f"🔍 [STATS] 开始获取用户统计数据（缓存版）")
    print(f"🔍 [STATS] 用户ID: {current_user.id}")
    print(f"🔍 [STATS] 用户名: {current_user.username}")
    print(f"🔍 [STATS] 请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    overall_start = time.time()

    try:
        print("💾 [STATS] 尝试使用Redis缓存...")

        # 🚀 使用缓存服务获取统计数据
        cache_start = time.time()
        result = await stats_cache_service.get_user_document_stats(db, current_user.id)
        cache_time = (time.time() - cache_start) * 1000

        # 添加路由层的调试信息
        total_time = (time.time() - overall_start) * 1000
        is_cached = result.get("cache_info", {}).get("cached", False)

        if is_cached:
            print(f"✅ [STATS] 缓存命中! 总耗时: {total_time:.2f}ms")
            print(f"⚡ [STATS] 缓存服务耗时: {cache_time:.2f}ms")
            print(f"🚀 [STATS] 性能提升: 跳过了数据库查询!")
        else:
            print(f"✅ [STATS] 缓存未命中，已查询数据库并缓存")
            print(f"⚡ [STATS] 总耗时: {total_time:.2f}ms")
            print(f"💾 [STATS] 下次请求将从缓存获取")

        # 添加路由层的性能信息
        result["_route_debug_info"] = {
            "route_total_time_ms": round(total_time, 2),
            "cache_service_time_ms": round(cache_time, 2),
            "cache_hit": is_cached,
            "performance_improvement": "缓存命中，跳过数据库查询" if is_cached else "首次查询，已写入缓存"
        }

        print(f"📊 [STATS] 返回结果: 文档{result['total_documents']}个, 文件夹{result['total_folders']}个")
        print(f"📊 [STATS] 状态分布: {result['documents_by_status']}")
        print(f"💾 [STATS] 缓存状态: {'命中' if is_cached else '未命中'}")
        print("🔍 [STATS] =========================")

        return result

    except Exception as e:
        error_time = (time.time() - overall_start) * 1000
        print(f"❌ [STATS] 统计失败! 耗时: {error_time:.2f}ms")
        print(f"❌ [STATS] 错误类型: {type(e).__name__}")
        print(f"❌ [STATS] 错误详情: {str(e)}")
        print("🔍 [STATS] =========================")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


# ==================== 文件下载接口 ====================

@router.get("/documents/{doc_id}/download", summary="下载文档文件")
async def download_document(
        doc_id: int,
        preview: bool = Query(False, description="是否为预览模式（浏览器内打开）"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    下载文档文件（支持PDF预览和文件下载）

    参数：
    - **doc_id**: 文档ID
    - **preview**: 预览模式
      - true: 浏览器内预览（适用于PDF）
      - false: 强制下载文件

    支持的文件类型：
    - PDF文件：支持浏览器内预览
    - Markdown文件：下载.md文件

    响应：
    - Content-Type: 根据文件类型自动设置
    - Content-Disposition: 根据预览模式设置
    """
    return DocumentService.download_document(db, doc_id, current_user.id, preview)


@router.get("/documents/{doc_id}/stream", summary="获取文档文件流")
async def stream_document(
        doc_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    获取文档文件流（推荐用于PDF预览）

    专门用于PDF文件的流式传输，优化浏览器预览体验：
    - 设置正确的Content-Type
    - 支持分块传输
    - 浏览器自动选择PDF阅读器

    前端调用示例：
    ```javascript
    const pdfUrl = `http://localhost:8100/api/v2/document_manager/documents/${doc.id}/stream`
    window.open(pdfUrl, '_blank')
    ```
    """
    return DocumentService.stream_document(db, doc_id, current_user.id)


@router.get("/documents/{doc_id}/info", summary="获取文档文件信息")
async def get_document_file_info(
        doc_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    获取文档文件信息（不下载文件内容）

    返回：
    - 文件名
    - 文件大小
    - 文件类型
    - MIME类型
    - 是否存在物理文件
    """
    return DocumentService.get_document_file_info(db, doc_id, current_user.id)