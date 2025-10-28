from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from .services import DocumentPublishService
from .schemas import (
    PublishRequest, UnpublishRequest, PublishRecordResponse,
    PublishedDocumentsQuery, PublishStatsResponse, DocumentPublishDetail,
    PublishedDocumentsResponse, DocumentUpdateRequest, DocumentUpdateResponse
)
from .dependencies import get_publish_dependencies, verify_document_owner
from app.core.database import get_db
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v1.user_auth.models import User

router = APIRouter()


@router.get("/test")
async def test_publish_module():
    """测试发布模块连通性"""
    return {
        "message": "✅ 文档发布模块运行正常",
        "module": "document_publish",
        "version": "v2",
        "features": [
            "文档发布申请",
            "AI自动审核",
            "发布状态管理",
            "发布历史记录",
            "统计分析"
        ]
    }


@router.post("/submit", response_model=PublishRecordResponse)
async def submit_document_for_publish(
        request: PublishRequest,
        deps=Depends(get_publish_dependencies)
):
    """
    提交文档发布申请

    - 检查文档权限
    - 创建发布记录
    - 触发AI审核
    - 记录操作历史
    """
    try:
        result = DocumentPublishService.submit_for_publish(
            db=deps["db"],
            user_id=deps["user_id"],
            request=request
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布申请失败: {str(e)}")


@router.get("/published", response_model=PublishedDocumentsResponse)
async def get_published_documents(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        status: Optional[str] = Query(None, description="发布状态筛选"),
        is_featured: Optional[bool] = Query(None, description="是否精选"),
        db: Session = Depends(get_db)
):
    """
    获取已发布文档列表（公开接口）

    - 支持分页查询
    - 支持状态筛选
    - 支持精选筛选
    - 按发布时间倒序
    """
    try:
        query = PublishedDocumentsQuery(
            page=page,
            size=size,
            status=status,
            is_featured=is_featured
        )
        result = DocumentPublishService.get_published_documents(db=db, query=query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发布文档失败: {str(e)}")


@router.get("/document/{document_id}", response_model=DocumentPublishDetail)
async def get_document_publish_detail(
        document_id: int,
        deps=Depends(get_publish_dependencies)
):
    """
    获取文档发布详情（需要权限）

    - 文档基本信息
    - 发布记录
    - 发布历史
    """
    try:
        result = DocumentPublishService.get_document_publish_detail(
            db=deps["db"],
            user_id=deps["user_id"],
            document_id=document_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发布详情失败: {str(e)}")


@router.post("/unpublish/{document_id}", response_model=PublishRecordResponse)
async def unpublish_document(
        document_id: int,
        request: UnpublishRequest,
        deps=Depends(get_publish_dependencies)
):
    """
    撤回已发布文档

    - 验证文档权限
    - 更新发布状态
    - 记录操作历史
    """
    try:
        result = DocumentPublishService.unpublish_document(
            db=deps["db"],
            user_id=deps["user_id"],
            document_id=document_id,
            request=request
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤回发布失败: {str(e)}")


@router.get("/my-records")
async def get_my_publish_records(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        deps=Depends(get_publish_dependencies)
):
    """
    获取我的发布记录

    - 包含发布记录和文档信息
    - 支持分页
    - 按创建时间倒序
    """
    try:
        result = DocumentPublishService.get_my_publish_records(
            db=deps["db"],
            user_id=deps["user_id"],
            page=page,
            size=size
        )
        return {
            "success": True,
            "data": result,
            "message": "获取发布记录成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发布记录失败: {str(e)}")


@router.get("/stats", response_model=PublishStatsResponse)
async def get_publish_stats(
        global_stats: bool = Query(False, description="是否获取全局统计"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取发布统计

    - 默认获取个人统计
    - global_stats=true 获取全局统计
    """
    try:
        user_id = None if global_stats else current_user.id
        result = DocumentPublishService.get_publish_stats(db=db, user_id=user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.post("/view/{document_id}")
async def increment_document_view(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    增加文档浏览量（公开接口）

    - 无需登录
    - 仅对已发布文档有效
    """
    try:
        DocumentPublishService.increment_view_count(db=db, document_id=document_id)
        return {
            "success": True,
            "message": "浏览量已更新"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新浏览量失败: {str(e)}")


@router.get("/status/{document_id}")
async def get_publish_status(
        document_id: int,
        deps=Depends(get_publish_dependencies)
):
    """
    快速获取文档发布状态

    - 返回当前发布状态
    - 包含基本统计信息
    """
    try:
        from .models import PublishRecord
        from sqlalchemy import and_

        # 查询发布记录
        publish_record = deps["db"].query(PublishRecord).filter(
            and_(
                PublishRecord.document_id == document_id,
                PublishRecord.user_id == deps["user_id"]
            )
        ).first()

        if not publish_record:
            return {
                "success": True,
                "data": {
                    "document_id": document_id,
                    "publish_status": "not_submitted",
                    "message": "文档尚未提交发布"
                }
            }

        return {
            "success": True,
            "data": {
                "document_id": document_id,
                "publish_status": publish_record.publish_status,
                "publish_time": publish_record.publish_time,
                "view_count": publish_record.view_count,
                "is_featured": publish_record.is_featured,
                "publish_reason": publish_record.publish_reason,
                "unpublish_reason": publish_record.unpublish_reason
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发布状态失败: {str(e)}")


@router.get("/config")
async def get_publish_config():
    """
    获取发布配置信息

    - 发布状态枚举
    - 业务规则说明
    """
    return {
        "success": True,
        "data": {
            "publish_statuses": {
                "draft": "草稿",
                "pending_review": "待审核",
                "review_passed": "审核通过",
                "review_failed": "审核失败",
                "published": "已发布",
                "unpublished": "已撤回"
            },
            "action_types": {
                "submit": "提交发布",
                "approve": "审核通过",
                "reject": "审核拒绝",
                "publish": "发布",
                "unpublish": "撤回",
                "edit": "编辑"
            },
            "rules": {
                "auto_review": "支持AI自动审核",
                "publish_flow": "提交 → AI审核 → 自动发布",
                "unpublish_anytime": "已发布文档可随时撤回",
                "view_tracking": "自动跟踪文档浏览量"
            }
        }
    }


@router.put("/update/{document_id}", response_model=DocumentUpdateResponse)
async def update_published_document(
        document_id: int,
        request: DocumentUpdateRequest,
        deps=Depends(get_publish_dependencies)
):
    """
    更新已发布文档（保留所有互动数据）

    功能特点：
    - ✅ 保留所有互动数据（评论、点赞、收藏、浏览量）
    - ✅ 重新提交AI审核
    - ✅ 审核期间技术广场显示旧版本
    - ✅ 审核通过后显示新版本
    - ✅ 分享链接保持有效
    - ✅ 版本控制和操作历史

    业务流程：
    1. 验证文档权限和发布状态
    2. 保存待审核内容到临时字段
    3. 触发AI审核
    4. 审核通过：应用新内容
    5. 审核失败：回滚到原内容
    """
    try:
        result = DocumentPublishService.update_published_document(
            db=deps["db"],
            user_id=deps["user_id"],
            document_id=document_id,
            request=request
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文档失败: {str(e)}")