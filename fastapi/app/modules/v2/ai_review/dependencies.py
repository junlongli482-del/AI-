from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v2.ai_review.models import AIReviewLog, ReviewRule
from app.modules.v2.document_manager.models import Document
from typing import Optional


def get_document_by_id(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取文档并验证权限"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权限访问"
        )

    return document


def get_review_log_by_id(review_log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取审核日志并验证权限"""
    review_log = db.query(AIReviewLog).filter(
        AIReviewLog.id == review_log_id,
        AIReviewLog.user_id == current_user.id
    ).first()

    if not review_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="审核记录不存在或无权限访问"
        )

    return review_log


def get_active_review_rules(db: Session = Depends(get_db)):
    """获取所有激活的审核规则"""
    return db.query(ReviewRule).filter(
        ReviewRule.is_active == True
    ).order_by(ReviewRule.priority.desc()).all()


def validate_review_permission(document: Document = Depends(get_document_by_id)):
    """验证审核权限"""
    # 检查文档状态是否允许审核
    if document.status not in ['draft', 'review_failed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档状态为 {document.status}，无法提交审核"
        )

    return document