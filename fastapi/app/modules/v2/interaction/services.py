from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc
from typing import Optional, List, Tuple
from fastapi import HTTPException
import math

from .models import DocumentLike, DocumentFavorite, DocumentComment, DocumentInteractionStats
from .schemas import (
    CommentCreate, CommentUpdate, CommentItem, CommentReply, CommentUser,
    FavoriteItem, InteractionStats, UserInteractionStats
)
from ..document_manager.models import Document
from ...v1.user_register.models import User


class InteractionService:
    """互动服务类"""

    # ============= 点赞功能 =============
    def toggle_like(self, db: Session, document_id: int, user_id: int) -> Tuple[bool, bool, int]:
        """
        切换点赞状态
        返回: (操作成功, 是否已点赞, 点赞总数)
        """
        # 检查文档是否存在
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 检查是否已点赞
        existing_like = db.query(DocumentLike).filter(
            and_(DocumentLike.document_id == document_id, DocumentLike.user_id == user_id)
        ).first()

        if existing_like:
            # 取消点赞
            db.delete(existing_like)
            is_liked = False
            message = "取消点赞成功"
        else:
            # 添加点赞
            new_like = DocumentLike(document_id=document_id, user_id=user_id)
            db.add(new_like)
            is_liked = True
            message = "点赞成功"

        # 更新统计
        self._update_like_stats(db, document_id)

        db.commit()

        # 获取最新点赞数
        like_count = self._get_like_count(db, document_id)

        return True, is_liked, like_count

    def get_like_status(self, db: Session, document_id: int, user_id: Optional[int] = None) -> Tuple[bool, int]:
        """
        获取点赞状态
        返回: (是否已点赞, 点赞总数)
        """
        # 检查是否已点赞
        is_liked = False
        if user_id:
            existing_like = db.query(DocumentLike).filter(
                and_(DocumentLike.document_id == document_id, DocumentLike.user_id == user_id)
            ).first()
            is_liked = existing_like is not None

        # 获取点赞总数
        like_count = self._get_like_count(db, document_id)

        return is_liked, like_count

    def _get_like_count(self, db: Session, document_id: int) -> int:
        """获取文档点赞数"""
        return db.query(DocumentLike).filter(DocumentLike.document_id == document_id).count()

    def _update_like_stats(self, db: Session, document_id: int):
        """更新点赞统计"""
        like_count = self._get_like_count(db, document_id)

        stats = db.query(DocumentInteractionStats).filter(
            DocumentInteractionStats.document_id == document_id
        ).first()

        if stats:
            stats.like_count = like_count
        else:
            stats = DocumentInteractionStats(
                document_id=document_id,
                like_count=like_count
            )
            db.add(stats)

    # ============= 收藏功能 =============
    def toggle_favorite(self, db: Session, document_id: int, user_id: int) -> Tuple[bool, bool, int]:
        """
        切换收藏状态
        返回: (操作成功, 是否已收藏, 收藏总数)
        """
        # 检查文档是否存在
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 检查是否已收藏
        existing_favorite = db.query(DocumentFavorite).filter(
            and_(DocumentFavorite.document_id == document_id, DocumentFavorite.user_id == user_id)
        ).first()

        if existing_favorite:
            # 取消收藏
            db.delete(existing_favorite)
            is_favorited = False
            message = "取消收藏成功"
        else:
            # 添加收藏
            new_favorite = DocumentFavorite(document_id=document_id, user_id=user_id)
            db.add(new_favorite)
            is_favorited = True
            message = "收藏成功"

        # 更新统计
        self._update_favorite_stats(db, document_id)

        db.commit()

        # 获取最新收藏数
        favorite_count = self._get_favorite_count(db, document_id)

        return True, is_favorited, favorite_count

    def get_favorite_status(self, db: Session, document_id: int, user_id: Optional[int] = None) -> Tuple[bool, int]:
        """
        获取收藏状态
        返回: (是否已收藏, 收藏总数)
        """
        # 检查是否已收藏
        is_favorited = False
        if user_id:
            existing_favorite = db.query(DocumentFavorite).filter(
                and_(DocumentFavorite.document_id == document_id, DocumentFavorite.user_id == user_id)
            ).first()
            is_favorited = existing_favorite is not None

        # 获取收藏总数
        favorite_count = self._get_favorite_count(db, document_id)

        return is_favorited, favorite_count

    def get_user_favorites(self, db: Session, user_id: int, page: int = 1, size: int = 20) -> Tuple[
        List[FavoriteItem], int]:
        """获取用户收藏列表"""
        offset = (page - 1) * size

        # 查询收藏列表
        query = db.query(DocumentFavorite).options(
            joinedload(DocumentFavorite.document)
        ).filter(DocumentFavorite.user_id == user_id).order_by(desc(DocumentFavorite.created_at))

        total = query.count()
        favorites = query.offset(offset).limit(size).all()

        # 转换为响应模型
        items = []
        for favorite in favorites:
            if favorite.document:  # 确保文档存在
                item = FavoriteItem(
                    id=favorite.id,
                    document_id=favorite.document.id,
                    document_title=favorite.document.title,
                    document_summary=favorite.document.summary,
                    file_type=favorite.document.file_type,
                    created_at=favorite.created_at
                )
                items.append(item)

        return items, total

    def _get_favorite_count(self, db: Session, document_id: int) -> int:
        """获取文档收藏数"""
        return db.query(DocumentFavorite).filter(DocumentFavorite.document_id == document_id).count()

    def _update_favorite_stats(self, db: Session, document_id: int):
        """更新收藏统计"""
        favorite_count = self._get_favorite_count(db, document_id)

        stats = db.query(DocumentInteractionStats).filter(
            DocumentInteractionStats.document_id == document_id
        ).first()

        if stats:
            stats.favorite_count = favorite_count
        else:
            stats = DocumentInteractionStats(
                document_id=document_id,
                favorite_count=favorite_count
            )
            db.add(stats)

    # ============= 评论功能 =============
    def create_comment(self, db: Session, document_id: int, user_id: int, comment_data: CommentCreate) -> CommentItem:
        """创建评论"""
        # 检查文档是否存在
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 如果是回复，检查父评论是否存在
        if comment_data.parent_id:
            parent_comment = db.query(DocumentComment).filter(
                and_(
                    DocumentComment.id == comment_data.parent_id,
                    DocumentComment.document_id == document_id,
                    DocumentComment.is_deleted == False
                )
            ).first()
            if not parent_comment:
                raise HTTPException(status_code=404, detail="父评论不存在")

            # 检查是否为二层回复（不允许三层及以上）
            if parent_comment.parent_id is not None:
                raise HTTPException(status_code=400, detail="不支持三层及以上回复")

        # 创建评论
        new_comment = DocumentComment(
            document_id=document_id,
            user_id=user_id,
            parent_id=comment_data.parent_id,
            content=comment_data.content
        )

        db.add(new_comment)
        db.flush()  # 获取ID

        # 更新统计
        self._update_comment_stats(db, document_id)

        db.commit()

        # 返回完整的评论信息
        return self._get_comment_detail(db, new_comment.id)

    def get_comments(self, db: Session, document_id: int, page: int = 1, size: int = 20) -> Tuple[
        List[CommentItem], int]:
        """获取文档评论列表（只返回顶级评论，回复作为子项）"""
        offset = (page - 1) * size

        # 查询顶级评论
        query = db.query(DocumentComment).options(
            joinedload(DocumentComment.user),
            joinedload(DocumentComment.replies).joinedload(DocumentComment.user)
        ).filter(
            and_(
                DocumentComment.document_id == document_id,
                DocumentComment.parent_id.is_(None),
                DocumentComment.is_deleted == False
            )
        ).order_by(desc(DocumentComment.created_at))

        total = query.count()
        comments = query.offset(offset).limit(size).all()

        # 转换为响应模型
        items = []
        for comment in comments:
            # 获取回复列表（只显示未删除的回复）
            replies = []
            for reply in comment.replies:
                if not reply.is_deleted:
                    reply_item = CommentReply(
                        id=reply.id,
                        content=reply.content,
                        user=CommentUser(
                            id=reply.user.id,
                            username=reply.user.username,
                            nickname=reply.user.nickname
                        ),
                        created_at=reply.created_at,
                        updated_at=reply.updated_at
                    )
                    replies.append(reply_item)

            comment_item = CommentItem(
                id=comment.id,
                content=comment.content,
                user=CommentUser(
                    id=comment.user.id,
                    username=comment.user.username,
                    nickname=comment.user.nickname
                ),
                replies=replies,
                reply_count=len(replies),
                created_at=comment.created_at,
                updated_at=comment.updated_at
            )
            items.append(comment_item)

        return items, total

    def update_comment(self, db: Session, comment_id: int, user_id: int, comment_data: CommentUpdate) -> CommentItem:
        """更新评论"""
        comment = db.query(DocumentComment).filter(
            and_(
                DocumentComment.id == comment_id,
                DocumentComment.user_id == user_id,
                DocumentComment.is_deleted == False
            )
        ).first()

        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在或无权限修改")

        comment.content = comment_data.content
        db.commit()

        return self._get_comment_detail(db, comment_id)

    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> bool:
        """删除评论（软删除）"""
        comment = db.query(DocumentComment).filter(
            and_(
                DocumentComment.id == comment_id,
                DocumentComment.user_id == user_id,
                DocumentComment.is_deleted == False
            )
        ).first()

        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在或无权限删除")

        # 软删除
        comment.is_deleted = True

        # 如果是顶级评论，同时软删除所有回复
        if comment.parent_id is None:
            db.query(DocumentComment).filter(
                DocumentComment.parent_id == comment_id
            ).update({"is_deleted": True})

        # 更新统计
        self._update_comment_stats(db, comment.document_id)

        db.commit()
        return True

    def _get_comment_detail(self, db: Session, comment_id: int) -> CommentItem:
        """获取评论详情"""
        comment = db.query(DocumentComment).options(
            joinedload(DocumentComment.user),
            joinedload(DocumentComment.replies).joinedload(DocumentComment.user)
        ).filter(
            and_(DocumentComment.id == comment_id, DocumentComment.is_deleted == False)
        ).first()

        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")

        # 获取回复列表
        replies = []
        for reply in comment.replies:
            if not reply.is_deleted:
                reply_item = CommentReply(
                    id=reply.id,
                    content=reply.content,
                    user=CommentUser(
                        id=reply.user.id,
                        username=reply.user.username,
                        nickname=reply.user.nickname
                    ),
                    created_at=reply.created_at,
                    updated_at=reply.updated_at
                )
                replies.append(reply_item)

        return CommentItem(
            id=comment.id,
            content=comment.content,
            user=CommentUser(
                id=comment.user.id,
                username=comment.user.username,
                nickname=comment.user.nickname
            ),
            replies=replies,
            reply_count=len(replies),
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )

    def _get_comment_count(self, db: Session, document_id: int) -> int:
        """获取文档评论数（包括回复）"""
        return db.query(DocumentComment).filter(
            and_(DocumentComment.document_id == document_id, DocumentComment.is_deleted == False)
        ).count()

    def _update_comment_stats(self, db: Session, document_id: int):
        """更新评论统计"""
        comment_count = self._get_comment_count(db, document_id)

        stats = db.query(DocumentInteractionStats).filter(
            DocumentInteractionStats.document_id == document_id
        ).first()

        if stats:
            stats.comment_count = comment_count
        else:
            stats = DocumentInteractionStats(
                document_id=document_id,
                comment_count=comment_count
            )
            db.add(stats)

    # ============= 统计功能 =============
    def get_document_stats(self, db: Session, document_id: int) -> InteractionStats:
        """获取文档互动统计"""
        stats = db.query(DocumentInteractionStats).filter(
            DocumentInteractionStats.document_id == document_id
        ).first()

        if not stats:
            # 如果统计不存在，创建一个
            stats = DocumentInteractionStats(document_id=document_id)
            db.add(stats)
            db.commit()

        return InteractionStats(
            document_id=stats.document_id,
            like_count=stats.like_count,
            favorite_count=stats.favorite_count,
            comment_count=stats.comment_count,
            updated_at=stats.updated_at
        )

    def get_user_interaction_stats(self, db: Session, user_id: int) -> UserInteractionStats:
        """获取用户互动统计"""
        # 用户给出的互动
        total_likes_given = db.query(DocumentLike).filter(DocumentLike.user_id == user_id).count()
        total_favorites = db.query(DocumentFavorite).filter(DocumentFavorite.user_id == user_id).count()
        total_comments = db.query(DocumentComment).filter(
            and_(DocumentComment.user_id == user_id, DocumentComment.is_deleted == False)
        ).count()

        # 🔧 修复SQLAlchemy警告：使用select()而不是subquery()
        from sqlalchemy import select
        user_documents_query = select(Document.id).where(Document.user_id == user_id)

        total_likes_received = db.query(DocumentLike).filter(
            DocumentLike.document_id.in_(user_documents_query)
        ).count()

        total_favorites_received = db.query(DocumentFavorite).filter(
            DocumentFavorite.document_id.in_(user_documents_query)
        ).count()

        total_comments_received = db.query(DocumentComment).filter(
            and_(
                DocumentComment.document_id.in_(user_documents_query),
                DocumentComment.is_deleted == False
            )
        ).count()

        return UserInteractionStats(
            total_likes_given=total_likes_given,
            total_favorites=total_favorites,
            total_comments=total_comments,
            total_likes_received=total_likes_received,
            total_favorites_received=total_favorites_received,
            total_comments_received=total_comments_received
        )


# 创建服务实例
interaction_service = InteractionService()