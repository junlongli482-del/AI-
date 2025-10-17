from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from ...v1.user_auth.dependencies import get_current_user
from ...v1.user_register.models import User


def get_current_user_optional(db: Session = Depends(get_db)) -> Optional[User]:
    """
    获取当前用户（可选）
    用于不需要强制登录的接口，如查看点赞状态
    """
    try:
        from ...v1.user_auth.dependencies import get_current_user
        return get_current_user(db)
    except:
        return None


def validate_document_access(document_id: int, db: Session = Depends(get_db)):
    """验证文档访问权限"""
    from ..document_manager.models import Document

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 只允许访问已发布的文档
    if document.status != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或未发布"
        )

    return document


def validate_comment_permission(comment_id: int, current_user: User, db: Session = Depends(get_db)):
    """验证评论操作权限"""
    from .models import DocumentComment

    comment = db.query(DocumentComment).filter(
        DocumentComment.id == comment_id,
        DocumentComment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此评论"
        )

    return comment