from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import jwt

from ....core.database import get_db
from ....core.config import settings  # 🔧 修复：导入你的配置
from ...v1.user_auth.dependencies import get_current_user
from .models import DocumentShare
from ..document_manager.models import Document


def get_user_share(
        share_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
) -> DocumentShare:
    """获取用户的分享记录"""
    share = db.query(DocumentShare).filter(
        DocumentShare.id == share_id,
        DocumentShare.user_id == current_user.id
    ).first()

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在或无权限访问"
        )

    return share


def get_user_document(
        document_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Document:
    """获取用户的文档"""
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


def get_public_share(
        share_code: str,
        db: Session = Depends(get_db)
) -> DocumentShare:
    """获取公开分享记录（无需认证）"""
    share = db.query(DocumentShare).filter(
        DocumentShare.share_code == share_code
    ).first()

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享链接不存在"
        )

    return share


# 🔧 修复：重新实现可选认证依赖
def get_optional_current_user(request: Request, db: Session = Depends(get_db)):
    """
    可选的用户认证依赖
    - 如果有有效token，返回用户对象
    - 如果没有token或token无效，返回None
    - 不会抛出认证异常
    """
    try:
        # 检查是否有Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            print("🔍 没有Authorization header")
            return None

        # 检查是否是Bearer token格式
        if not authorization.startswith("Bearer "):
            print("🔍 不是Bearer token格式")
            return None

        # 提取token
        token = authorization.split(" ")[1]
        print(f"🔍 提取到token: {token[:20]}...")

        # 🔧 修复：直接使用JWT验证
        from ...v1.user_register.models import User

        try:
            # 验证JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))
            print(f"🔍 解析到user_id: {user_id}")

            if user_id is None:
                print("🔍 token中没有user_id")
                return None

            # 查询用户
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                print(f"✅ 找到活跃用户: {user.username}")
                return user
            else:
                print(f"❌ 用户不存在或不活跃")
                return None

        except jwt.ExpiredSignatureError:
            print("❌ Token已过期")
            return None
        except jwt.JWTError as e:
            print(f"❌ JWT验证失败: {str(e)}")
            return None

    except Exception as e:
        # 任何认证错误都返回None，不抛出异常
        print(f"❌ 认证异常: {str(e)}")
        return None


def validate_share_permissions(
        share: DocumentShare = Depends(get_public_share),
        current_user: Optional = Depends(get_optional_current_user)
):
    """验证分享访问权限"""
    from datetime import datetime

    # 检查分享状态
    if share.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分享链接已失效"
        )

    # 检查是否过期
    if share.expire_time and share.expire_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分享链接已过期"
        )

    # 检查私有分享权限
    if share.share_type == "private" and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录才能访问此分享"
        )

    return share