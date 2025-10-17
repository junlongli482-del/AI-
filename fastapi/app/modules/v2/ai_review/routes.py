from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v2.ai_review.dependencies import get_document_by_id, validate_review_permission
from app.modules.v2.ai_review.models import AIReviewLog  # 直接导入模型
from app.modules.v2.ai_review.schemas import (
    ReviewSubmitRequest, ReviewLogResponse, ReviewStatusResponse,
    ReviewHistoryRequest, ReviewStatsResponse, ReviewResult
)
from app.modules.v2.ai_review.services import ai_review_service

# 注意：不要设置prefix和tags，因为main.py会自动处理
router = APIRouter()


@router.get("/test")
async def test_ai_review():
    """测试AI审核模块"""
    return {
        "success": True,
        "message": "AI审核模块运行正常",
        "module": "ai_review",
        "version": "1.0.0",
        "features": [
            "文档大小检查（PDF≤10页，MD≤1000行）",
            "AI内容安全审核",
            "审核历史记录",
            "审核统计分析"
        ]
    }


@router.post("/submit-review", response_model=ReviewLogResponse)
async def submit_document_review(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
        document=Depends(validate_review_permission)
):
    """
    提交文档审核

    审核流程：
    1. 检查文档大小限制（PDF≤10页，MD≤1000行）
    2. 通过大小检查后，进行AI内容安全审核
    3. 根据审核结果更新文档状态
    """
    try:
        # 检查是否已有待处理的审核
        existing_review = db.query(AIReviewLog).filter(
            AIReviewLog.document_id == document_id,
            AIReviewLog.user_id == current_user.id,
            AIReviewLog.review_result == 'pending'
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该文档已有待处理的审核，请等待审核完成"
            )

        # 提交审核
        review_log = ai_review_service.submit_document_review(
            document=document,
            user_id=current_user.id,
            db=db
        )

        return ReviewLogResponse.from_orm(review_log)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交审核失败: {str(e)}"
        )


@router.get("/review-status/{document_id}", response_model=ReviewStatusResponse)
async def get_review_status(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    查询文档审核状态

    返回文档的最新审核状态和详细信息
    """
    try:
        # 验证文档权限
        document = get_document_by_id(document_id, db, current_user)

        review_status = ai_review_service.get_review_status(
            document_id=document_id,
            user_id=current_user.id,
            db=db
        )

        return review_status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询审核状态失败: {str(e)}"
        )


@router.get("/review-history")
async def get_review_history(
        page: int = Query(default=1, ge=1, description="页码"),
        size: int = Query(default=20, ge=1, le=100, description="每页数量"),
        review_result: Optional[ReviewResult] = Query(default=None, description="筛选审核结果"),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    获取用户的审核历史记录

    支持分页和结果筛选
    """
    try:
        history = ai_review_service.get_review_history(
            user_id=current_user.id,
            page=page,
            size=size,
            review_result=review_result,
            db=db
        )

        return {
            "success": True,
            "message": "获取审核历史成功",
            "data": history
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核历史失败: {str(e)}"
        )


@router.get("/review-detail/{review_id}", response_model=ReviewLogResponse)
async def get_review_detail(
        review_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    获取审核记录详情
    """
    try:
        from app.modules.v2.ai_review.dependencies import get_review_log_by_id

        review_log = get_review_log_by_id(review_id, db, current_user)
        return ReviewLogResponse.from_orm(review_log)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核详情失败: {str(e)}"
        )


@router.post("/retry-review/{document_id}", response_model=ReviewLogResponse)
async def retry_document_review(
        document_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    重新审核文档

    适用于审核失败或出错的文档
    """
    try:
        # 验证文档权限和状态
        document = get_document_by_id(document_id, db, current_user)

        if document.status not in ['review_failed', 'draft']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文档状态为 {document.status}，无法重新审核"
            )

        # 重新提交审核
        review_log = ai_review_service.submit_document_review(
            document=document,
            user_id=current_user.id,
            db=db
        )

        return ReviewLogResponse.from_orm(review_log)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新审核失败: {str(e)}"
        )


@router.get("/stats", response_model=ReviewStatsResponse)
async def get_review_stats(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    获取用户的审核统计信息

    包括总审核数、通过率、平均耗时等
    """
    try:
        stats = ai_review_service.get_review_stats(
            user_id=current_user.id,
            db=db
        )

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核统计失败: {str(e)}"
        )


@router.get("/config")
async def get_review_config(
    current_user = Depends(get_current_user)
):
    """
    获取审核配置信息
    """
    return {
        "success": True,
        "message": "获取审核配置成功",
        "config": {
            "review_types": ["content_safety"],
            "size_limits": {
                "pdf_max_pages": 10,
                "md_max_lines": 1000
            },
            "ai_provider": "default",
            "ai_service_info": "AI服务端已预设内容安全审核提示词",
            "review_prompt_info": ai_review_service.review_prompt_info,
            "supported_file_types": ["pdf", "md"],
            "review_flow": [
                "1. 文档大小检查（PDF≤10页，MD≤1000行）",
                "2. AI内容安全审核（使用服务端预设提示词）",
                "3. 解析AI响应（true/false格式）",
                "4. 更新文档状态"
            ]
        }
    }


@router.delete("/review-log/{review_id}")
async def delete_review_log(
        review_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    删除审核记录

    注意：只能删除自己的审核记录，且不会影响文档状态
    """
    try:
        from app.modules.v2.ai_review.dependencies import get_review_log_by_id

        review_log = get_review_log_by_id(review_id, db, current_user)

        # 删除审核记录
        db.delete(review_log)
        db.commit()

        return {
            "success": True,
            "message": "审核记录删除成功",
            "deleted_review_id": review_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除审核记录失败: {str(e)}"
        )


@router.get("/recent-reviews")
async def get_recent_reviews(
        limit: int = Query(default=10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    获取最近的审核记录
    """
    try:
        recent_reviews = db.query(AIReviewLog).filter(
            AIReviewLog.user_id == current_user.id
        ).order_by(AIReviewLog.created_at.desc()).limit(limit).all()

        return {
            "success": True,
            "message": "获取最近审核记录成功",
            "data": {
                "total": len(recent_reviews),
                "reviews": [ReviewLogResponse.from_orm(review) for review in recent_reviews]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最近审核记录失败: {str(e)}"
        )