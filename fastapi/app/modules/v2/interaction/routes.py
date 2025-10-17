from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.core.database import get_db
from ...v1.user_auth.dependencies import get_current_user
from ...v1.user_register.models import User
from .dependencies import get_current_user_optional, validate_document_access
from .services import interaction_service
from .schemas import (
    LikeResponse, LikeStatusResponse, FavoriteResponse, FavoriteStatusResponse,
    FavoriteListResponse, CommentCreate, CommentUpdate, CommentListResponse,
    CommentResponse, InteractionStats, UserInteractionStats
)

router = APIRouter()


# ============= 测试接口 =============
@router.get("/test")
async def test_interaction():
    """测试互动模块连通性"""
    return {
        "success": True,
        "message": "互动模块连接正常",
        "module": "interaction",
        "version": "v2"
    }


# ============= 点赞功能 =============
@router.post("/documents/{document_id}/like", response_model=LikeResponse)
async def toggle_like(
        document_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """切换文档点赞状态"""
    try:
        success, is_liked, like_count = interaction_service.toggle_like(
            db, document_id, current_user.id
        )

        message = "点赞成功" if is_liked else "取消点赞成功"

        return LikeResponse(
            success=success,
            message=message,
            is_liked=is_liked,
            like_count=like_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.get("/documents/{document_id}/like-status", response_model=LikeStatusResponse)
async def get_like_status(
        document_id: int,
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    """获取文档点赞状态"""
    try:
        user_id = current_user.id if current_user else None
        is_liked, like_count = interaction_service.get_like_status(
            db, document_id, user_id
        )

        return LikeStatusResponse(
            is_liked=is_liked,
            like_count=like_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取点赞状态失败: {str(e)}")


# ============= 收藏功能 =============
@router.post("/documents/{document_id}/favorite", response_model=FavoriteResponse)
async def toggle_favorite(
        document_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """切换文档收藏状态"""
    try:
        success, is_favorited, favorite_count = interaction_service.toggle_favorite(
            db, document_id, current_user.id
        )

        message = "收藏成功" if is_favorited else "取消收藏成功"

        return FavoriteResponse(
            success=success,
            message=message,
            is_favorited=is_favorited,
            favorite_count=favorite_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.get("/documents/{document_id}/favorite-status", response_model=FavoriteStatusResponse)
async def get_favorite_status(
        document_id: int,
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    """获取文档收藏状态"""
    try:
        user_id = current_user.id if current_user else None
        is_favorited, favorite_count = interaction_service.get_favorite_status(
            db, document_id, user_id
        )

        return FavoriteStatusResponse(
            is_favorited=is_favorited,
            favorite_count=favorite_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏状态失败: {str(e)}")


@router.get("/my-favorites", response_model=FavoriteListResponse)
async def get_my_favorites(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取我的收藏列表"""
    try:
        items, total = interaction_service.get_user_favorites(
            db, current_user.id, page, size
        )

        pages = math.ceil(total / size) if total > 0 else 1

        return FavoriteListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")


# ============= 评论功能 =============
@router.post("/documents/{document_id}/comments", response_model=CommentResponse)
async def create_comment(
        document_id: int,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """创建评论或回复"""
    try:
        comment = interaction_service.create_comment(
            db, document_id, current_user.id, comment_data
        )

        message = "回复成功" if comment_data.parent_id else "评论成功"

        return CommentResponse(
            success=True,
            message=message,
            comment=comment
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评论失败: {str(e)}")


@router.get("/documents/{document_id}/comments", response_model=CommentListResponse)
async def get_comments(
        document_id: int,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db)
):
    """获取文档评论列表"""
    try:
        items, total = interaction_service.get_comments(
            db, document_id, page, size
        )

        pages = math.ceil(total / size) if total > 0 else 1

        return CommentListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评论列表失败: {str(e)}")


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新评论"""
    try:
        comment = interaction_service.update_comment(
            db, comment_id, current_user.id, comment_data
        )

        return CommentResponse(
            success=True,
            message="评论更新成功",
            comment=comment
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新评论失败: {str(e)}")


@router.delete("/comments/{comment_id}")
async def delete_comment(
        comment_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除评论"""
    try:
        success = interaction_service.delete_comment(
            db, comment_id, current_user.id
        )

        return {
            "success": success,
            "message": "评论删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评论失败: {str(e)}")


# ============= 统计功能 =============
@router.get("/documents/{document_id}/stats", response_model=InteractionStats)
async def get_document_stats(
        document_id: int,
        db: Session = Depends(get_db)
):
    """获取文档互动统计"""
    try:
        stats = interaction_service.get_document_stats(db, document_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/my-stats", response_model=UserInteractionStats)
async def get_my_interaction_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取我的互动统计"""
    try:
        stats = interaction_service.get_user_interaction_stats(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")