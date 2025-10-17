"""
文档管理模块 - 路由定义
功能：定义文档和文件夹管理的API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .dependencies import get_db, get_current_active_user, get_db_and_user
from .services import FolderService, DocumentService
from .schemas import (
    FolderCreateRequest, FolderResponse, FolderTreeResponse,
    DocumentCreateRequest, DocumentUpdateRequest, DocumentResponse,
    DocumentListWithPaginationResponse, SuccessResponse
)
from app.modules.v1.user_register.models import User

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
    获取文档列表（分页）

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
    """
    return DocumentService.get_documents_list(db, current_user.id, folder_id, page, page_size)


# ==================== 快捷操作接口 ====================

@router.get("/stats", summary="获取统计信息")
async def get_user_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    获取用户的文档统计信息

    包含：
    - 总文档数
    - 各状态文档数量
    - 文件夹数量
    """
    from .models import Document, Folder, DocumentStatus
    from sqlalchemy import func

    # 统计文档数量
    total_docs = db.query(Document).filter(Document.user_id == current_user.id).count()

    # 按状态统计
    status_stats = db.query(
        Document.status,
        func.count(Document.id)
    ).filter(
        Document.user_id == current_user.id
    ).group_by(Document.status).all()

    # 统计文件夹数量
    total_folders = db.query(Folder).filter(Folder.user_id == current_user.id).count()

    # 格式化状态统计
    status_dict = {status.value: 0 for status in DocumentStatus}
    for status, count in status_stats:
        status_dict[status] = count

    return {
        "total_documents": total_docs,
        "total_folders": total_folders,
        "documents_by_status": status_dict,
        "user_id": current_user.id
    }