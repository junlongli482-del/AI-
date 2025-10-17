from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, select
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import secrets
import string
from fastapi import HTTPException, status

# 🔧 修复：移除枚举导入，只导入模型类
from .models import DocumentShare, ShareAccessLog
from .schemas import (
    CreateShareRequest, UpdateShareRequest, AccessShareRequest,
    ShareResponse, ShareDetailResponse, ShareStatsResponse,
    PublicDocumentResponse, AccessLogResponse
)
from ..document_manager.models import Document
from ...v1.user_register.models import User
import os

class ShareSystemService:

    def __init__(self):
        pass

    def generate_share_code(self) -> str:
        """生成唯一的分享码"""
        while True:
            # 生成8位随机字符串
            code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            # 这里应该检查数据库中是否已存在，简化处理
            return code

    def create_share(self, request: CreateShareRequest, current_user, db: Session) -> ShareResponse:
        """创建文档分享"""
        # 获取用户ID
        user_id = current_user.id

        # 🔧 修复：验证文档存在且属于当前用户
        document = db.query(Document).filter(
            and_(Document.id == request.document_id, Document.user_id == user_id)
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在或无权限访问"
            )

        # 🔧 修复：检查是否已存在活跃的分享
        existing_share = db.query(DocumentShare).filter(
            and_(
                DocumentShare.document_id == request.document_id,
                DocumentShare.user_id == user_id,
                DocumentShare.status == "active"
            )
        ).first()

        if existing_share:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该文档已存在活跃的分享链接"
            )

        # 计算过期时间
        expire_time = None
        if request.expire_hours:
            expire_time = datetime.utcnow() + timedelta(hours=request.expire_hours)

        # 创建分享记录
        share = DocumentShare(
            document_id=request.document_id,
            user_id=user_id,
            share_code=self.generate_share_code(),
            share_type=request.share_type,
            share_password=request.share_password,
            allow_download=request.allow_download,
            allow_comment=request.allow_comment,
            expire_time=expire_time
        )

        db.add(share)
        db.commit()
        db.refresh(share)

        return self._build_share_response(share, db)

    def get_my_shares(self, current_user, page: int, size: int, db: Session) -> Tuple[List[ShareResponse], int]:
        """获取我的分享列表"""
        user_id = current_user.id

        query = db.query(DocumentShare).filter(DocumentShare.user_id == user_id)

        total = query.count()
        shares = query.order_by(desc(DocumentShare.created_at)).offset((page - 1) * size).limit(size).all()

        share_responses = [self._build_share_response(share, db) for share in shares]
        return share_responses, total

    def get_share_detail(self, share_id: int, current_user, db: Session) -> ShareDetailResponse:
        """获取分享详情"""
        user_id = current_user.id

        # 🔧 修复：检查分享是否存在
        share = db.query(DocumentShare).filter(
            and_(DocumentShare.id == share_id, DocumentShare.user_id == user_id)
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享不存在或无权限访问"
            )

        # 获取访问统计
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        today_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id == share_id,
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= today_start
            )
        ).count()

        week_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id == share_id,
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= week_start
            )
        ).count()

        month_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id == share_id,
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= month_start
            )
        ).count()

        # 获取最近访问记录
        recent_logs = db.query(ShareAccessLog).filter(
            ShareAccessLog.share_id == share_id
        ).order_by(desc(ShareAccessLog.accessed_at)).limit(10).all()

        recent_access_logs = [self._build_access_log_response(log, db) for log in recent_logs]

        base_response = self._build_share_response(share, db)

        return ShareDetailResponse(
            **base_response.dict(),
            today_views=today_views,
            week_views=week_views,
            month_views=month_views,
            recent_access_logs=recent_access_logs
        )

    def update_share(self, share_id: int, request: UpdateShareRequest, current_user, db: Session) -> ShareResponse:
        """更新分享配置"""
        user_id = current_user.id

        share = db.query(DocumentShare).filter(
            and_(DocumentShare.id == share_id, DocumentShare.user_id == user_id)
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享不存在或无权限访问"
            )

        # 更新字段
        if request.share_type is not None:
            share.share_type = request.share_type
        if request.share_password is not None:
            share.share_password = request.share_password
        if request.allow_download is not None:
            share.allow_download = request.allow_download
        if request.allow_comment is not None:
            share.allow_comment = request.allow_comment
        if request.status is not None:
            share.status = request.status
        if request.expire_hours is not None:
            if request.expire_hours > 0:
                share.expire_time = datetime.utcnow() + timedelta(hours=request.expire_hours)
            else:
                share.expire_time = None

        share.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(share)

        return self._build_share_response(share, db)

    def delete_share(self, share_id: int, current_user, db: Session) -> bool:
        """删除分享"""
        user_id = current_user.id

        share = db.query(DocumentShare).filter(
            and_(DocumentShare.id == share_id, DocumentShare.user_id == user_id)
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享不存在或无权限访问"
            )

        db.delete(share)
        db.commit()
        return True

    def access_shared_document(self, share_code: str, request: AccessShareRequest,
                               visitor_ip: str, visitor_user_agent: str,
                               visitor_user_id: Optional[int], db: Session) -> PublicDocumentResponse:
        """访问分享的文档"""
        # 查找分享记录
        share = db.query(DocumentShare).filter(DocumentShare.share_code == share_code).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享链接不存在"
            )

        # 检查分享状态
        if share.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分享链接已失效"
            )

        # 检查是否过期
        if share.expire_time and share.expire_time < datetime.utcnow():
            share.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分享链接已过期"
            )

        # 权限验证
        if share.share_type == "private" and not visitor_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能访问此分享"
            )

        if share.share_type == "password":
            if not request.password or request.password != share.share_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分享密码错误"
                )

        # 记录访问日志
        self._log_access(share.id, "VIEW", visitor_ip, visitor_user_agent, visitor_user_id, db)

        # 更新访问计数
        share.view_count += 1
        db.commit()

        # 获取文档信息
        document = db.query(Document).filter(Document.id == share.document_id).first()

        # 🔧 修复：检查文档是否存在
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

        author = db.query(User).filter(User.id == document.user_id).first()

        # 🔧 修复：检查作者是否存在
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="作者信息不存在"
            )

        return PublicDocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            summary=document.summary,
            file_type=document.file_type,
            file_size=document.file_size,
            author_username=author.username,
            publish_time=document.publish_time,
            view_count=share.view_count,
            allow_download=share.allow_download,
            allow_comment=share.allow_comment
        )

    def download_shared_document(self, share_code: str, visitor_ip: str,
                                 visitor_user_agent: str, visitor_user_id: Optional[int],
                                 db: Session) -> Tuple[str, str]:
        """下载分享的文档"""
        share = db.query(DocumentShare).filter(DocumentShare.share_code == share_code).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享链接不存在"
            )

        if not share.allow_download:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="该分享不允许下载"
            )

        # 记录下载日志
        self._log_access(share.id, "DOWNLOAD", visitor_ip, visitor_user_agent, visitor_user_id, db)

        # 更新下载计数
        share.download_count += 1
        db.commit()

        # 获取文档信息
        document = db.query(Document).filter(Document.id == share.document_id).first()

        return document.file_path, document.title

    def get_share_stats(self, current_user, db: Session) -> ShareStatsResponse:
        """获取分享统计"""
        user_id = current_user.id

        # 🔧 修复：直接使用字符串
        total_shares = db.query(DocumentShare).filter(DocumentShare.user_id == user_id).count()
        active_shares = db.query(DocumentShare).filter(
            and_(DocumentShare.user_id == user_id, DocumentShare.status == "active")
        ).count()
        expired_shares = db.query(DocumentShare).filter(
            and_(DocumentShare.user_id == user_id, DocumentShare.status == "expired")
        ).count()
        disabled_shares = db.query(DocumentShare).filter(
            and_(DocumentShare.user_id == user_id, DocumentShare.status == "disabled")
        ).count()

        # 访问统计
        user_shares_query = select(DocumentShare.id).where(DocumentShare.user_id == user_id)

        total_views = db.query(func.sum(DocumentShare.view_count)).filter(
            DocumentShare.user_id == user_id
        ).scalar() or 0

        total_downloads = db.query(func.sum(DocumentShare.download_count)).filter(
            DocumentShare.user_id == user_id
        ).scalar() or 0

        # 时间范围统计
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        today_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id.in_(user_shares_query),
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= today_start
            )
        ).count()

        week_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id.in_(user_shares_query),
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= week_start
            )
        ).count()

        month_views = db.query(ShareAccessLog).filter(
            and_(
                ShareAccessLog.share_id.in_(user_shares_query),
                ShareAccessLog.access_type == "VIEW",
                ShareAccessLog.accessed_at >= month_start
            )
        ).count()

        # 热门分享
        popular_shares = db.query(DocumentShare).filter(
            DocumentShare.user_id == user_id
        ).order_by(desc(DocumentShare.view_count)).limit(5).all()

        popular_share_responses = [self._build_share_response(share, db) for share in popular_shares]

        return ShareStatsResponse(
            total_shares=total_shares,
            active_shares=active_shares,
            expired_shares=expired_shares,
            disabled_shares=disabled_shares,
            total_views=total_views,
            total_downloads=total_downloads,
            today_views=today_views,
            week_views=week_views,
            month_views=month_views,
            popular_shares=popular_share_responses
        )

    def _build_share_response(self, share: DocumentShare, db: Session) -> ShareResponse:
        """构建分享响应"""
        document = db.query(Document).filter(Document.id == share.document_id).first()

        # 🔑 关键修改：从环境变量读取基础URL，默认本地地址
        base_url = os.getenv("BASE_URL", "http://localhost:8100")
        share_url = f"{base_url}/api/v2/share_system/public/{share.share_code}"

        return ShareResponse(
            id=share.id,
            document_id=share.document_id,
            share_code=share.share_code,
            share_type=share.share_type,
            share_url=share_url,  # 这里会根据环境变量自动变化
            allow_download=share.allow_download,
            allow_comment=share.allow_comment,
            status=share.status,
            expire_time=share.expire_time,
            view_count=share.view_count,
            download_count=share.download_count,
            created_at=share.created_at,
            updated_at=share.updated_at,
            document_title=document.title,
            document_summary=document.summary
        )

    def _build_access_log_response(self, log: ShareAccessLog, db: Session) -> AccessLogResponse:
        """构建访问日志响应"""
        visitor_username = None
        if log.visitor_user_id:
            visitor = db.query(User).filter(User.id == log.visitor_user_id).first()
            if visitor:
                visitor_username = visitor.username

        return AccessLogResponse(
            id=log.id,
            access_type=log.access_type,
            access_result=log.access_result,
            visitor_ip=log.visitor_ip,
            visitor_user_id=log.visitor_user_id,
            visitor_username=visitor_username,
            accessed_at=log.accessed_at
        )

    def _log_access(self, share_id: int, access_type: str, visitor_ip: str,
                    visitor_user_agent: str, visitor_user_id: Optional[int], db: Session):
        """记录访问日志"""
        log = ShareAccessLog(
            share_id=share_id,
            visitor_ip=visitor_ip,
            visitor_user_agent=visitor_user_agent,
            visitor_user_id=visitor_user_id,
            access_type=access_type,
            access_result="success"
        )
        db.add(log)
        db.commit()


# 创建服务实例
share_system_service = ShareSystemService()