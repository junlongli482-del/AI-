"""
文件上传模块 - 依赖注入
功能：提供模块所需的依赖项
"""

from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v1.user_register.models import User
import os
from pathlib import Path


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


def validate_upload_file(file: UploadFile):
    """验证上传文件的基本要求"""
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未选择文件"
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )

    # 检查文件扩展名
    allowed_extensions = ['.md', '.pdf']
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。支持的格式：{', '.join(allowed_extensions)}"
        )

    return file


def ensure_upload_directory(user_id: int) -> str:
    """确保用户上传目录存在"""
    upload_dir = f"uploads/user_{user_id}/documents"
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir