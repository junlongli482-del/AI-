from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v1.user_auth.models import User


def get_publish_dependencies(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """发布模块通用依赖"""
    return {
        "current_user": current_user,
        "db": db,
        "user_id": current_user.id
    }


def verify_document_owner(
        document_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """验证文档所有权"""
    from app.modules.v2.document_manager.models import Document
    from sqlalchemy import and_

    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权限"
        )

    return document