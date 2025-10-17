from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from fastapi import HTTPException
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from .models import PublishRecord, PublishHistory
from .schemas import (
    PublishRequest, UnpublishRequest, PublishRecordResponse,
    PublishHistoryResponse, PublishedDocumentsQuery, PublishStatsResponse,
    DocumentPublishDetail, PublishedDocumentItem, PublishedDocumentsResponse
)

# 导入其他模块的模型
from app.modules.v2.document_manager.models import Document
from app.modules.v2.ai_review.models import AIReviewLog


class DocumentPublishService:

    @staticmethod
    def submit_for_publish(
            db: Session,
            user_id: int,
            request: PublishRequest
    ) -> PublishRecordResponse:
        """提交文档发布申请"""

        # 1. 检查文档是否存在且属于当前用户
        document = db.query(Document).filter(
            and_(
                Document.id == request.document_id,
                Document.user_id == user_id
            )
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在或无权限")

        # 2. 检查文档是否已有发布记录
        existing_record = db.query(PublishRecord).filter(
            PublishRecord.document_id == request.document_id
        ).first()

        if existing_record:
            # 如果已发布，不能重复提交
            if existing_record.publish_status == "published":
                raise HTTPException(status_code=400, detail="文档已发布，无法重复提交")

            # 如果在审核中，不能重复提交
            if existing_record.publish_status in ["pending_review", "review_passed"]:
                raise HTTPException(status_code=400, detail="文档正在审核中，请勿重复提交")

            # 更新现有记录
            existing_record.publish_status = "pending_review"
            existing_record.publish_reason = request.publish_reason
            existing_record.publish_config = request.publish_config
            existing_record.updated_at = datetime.utcnow()

            publish_record = existing_record
        else:
            # 3. 创建新的发布记录
            publish_record = PublishRecord(
                document_id=request.document_id,
                user_id=user_id,
                publish_version=1,
                publish_status="pending_review",
                publish_reason=request.publish_reason,
                publish_config=request.publish_config
            )
            db.add(publish_record)
            db.flush()  # 获取ID

        # 4. 记录操作历史
        history = PublishHistory(
            publish_record_id=publish_record.id,
            document_id=request.document_id,
            user_id=user_id,
            action_type="submit",
            action_reason=request.publish_reason,
            old_status="draft",
            new_status="pending_review",
            operator_id=user_id
        )
        db.add(history)

        # 5. 触发AI审核
        try:
            DocumentPublishService._trigger_ai_review(db, publish_record)
        except Exception as e:
            print(f"AI审核触发失败: {str(e)}")
            # AI审核失败不影响提交流程

        db.commit()
        db.refresh(publish_record)

        return PublishRecordResponse.model_validate(publish_record)

    @staticmethod
    def _trigger_ai_review(db: Session, publish_record: PublishRecord):
        """触发AI审核（集成ai_review模块）"""
        try:
            # 导入ai_review模块的服务
            from app.modules.v2.ai_review.services import ai_review_service  # 使用全局实例

            # 获取Document对象
            document = db.query(Document).filter(Document.id == publish_record.document_id).first()
            if not document:
                raise Exception("文档不存在")

            # 修复：使用正确的调用方式
            review_result = ai_review_service.submit_document_review(
                document,  # Document对象
                publish_record.user_id,  # user_id
                db  # Session对象
            )

            # 更新发布记录的审核ID
            publish_record.review_id = review_result.id

            # 根据审核结果更新发布状态
            if review_result.review_result == "passed":
                DocumentPublishService._approve_publish(db, publish_record, "AI审核通过")
            elif review_result.review_result == "failed":
                DocumentPublishService._reject_publish(db, publish_record,
                                                       review_result.failure_reason or "AI审核未通过")

        except Exception as e:
            print(f"AI审核服务调用失败: {str(e)}")
            # 如果AI审核失败，标记为需要人工审核
            publish_record.publish_status = "review_failed"
            publish_record.unpublish_reason = f"AI审核服务异常: {str(e)}"

    @staticmethod
    def _approve_publish(db: Session, publish_record: PublishRecord, reason: str):
        """审核通过，自动发布"""
        old_status = publish_record.publish_status
        publish_record.publish_status = "published"
        publish_record.publish_time = datetime.utcnow()

        # 记录历史
        history = PublishHistory(
            publish_record_id=publish_record.id,
            document_id=publish_record.document_id,
            user_id=publish_record.user_id,
            action_type="approve",
            action_reason=reason,
            old_status=old_status,
            new_status="published",
            operator_id=None  # AI系统操作
        )
        db.add(history)

        # 更新文档状态
        document = db.query(Document).filter(Document.id == publish_record.document_id).first()
        if document:
            document.status = "published"
            document.publish_time = datetime.utcnow()

    @staticmethod
    def _reject_publish(db: Session, publish_record: PublishRecord, reason: str):
        """审核拒绝"""
        old_status = publish_record.publish_status
        publish_record.publish_status = "review_failed"
        publish_record.unpublish_reason = reason

        # 记录历史
        history = PublishHistory(
            publish_record_id=publish_record.id,
            document_id=publish_record.document_id,
            user_id=publish_record.user_id,
            action_type="reject",
            action_reason=reason,
            old_status=old_status,
            new_status="review_failed",
            operator_id=None  # AI系统操作
        )
        db.add(history)

    @staticmethod
    def get_published_documents(
            db: Session,
            query: PublishedDocumentsQuery
    ) -> PublishedDocumentsResponse:
        """获取已发布文档列表（分页）"""

        # 构建查询
        base_query = db.query(Document, PublishRecord).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).filter(PublishRecord.publish_status == "published")

        # 状态筛选
        if query.status:
            base_query = base_query.filter(PublishRecord.publish_status == query.status)

        # 精选筛选
        if query.is_featured is not None:
            base_query = base_query.filter(PublishRecord.is_featured == query.is_featured)

        # 按发布时间倒序
        base_query = base_query.order_by(desc(PublishRecord.publish_time))

        # 计算总数
        total = base_query.count()

        # 分页
        offset = (query.page - 1) * query.size
        results = base_query.offset(offset).limit(query.size).all()

        # 构建响应
        items = []
        for document, publish_record in results:
            items.append(PublishedDocumentItem(
                id=document.id,
                title=document.title,
                summary=document.summary,
                file_type=document.file_type,
                user_id=document.user_id,
                publish_time=publish_record.publish_time,
                view_count=publish_record.view_count,
                is_featured=publish_record.is_featured
            ))

        pages = (total + query.size - 1) // query.size

        return PublishedDocumentsResponse(
            items=items,
            total=total,
            page=query.page,
            size=query.size,
            pages=pages
        )

    @staticmethod
    def get_document_publish_detail(
            db: Session,
            user_id: int,
            document_id: int
    ) -> DocumentPublishDetail:
        """获取文档发布详情"""

        # 获取文档信息
        document = db.query(Document).filter(
            and_(
                Document.id == document_id,
                Document.user_id == user_id
            )
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在或无权限")

        # 获取发布记录
        publish_record = db.query(PublishRecord).filter(
            PublishRecord.document_id == document_id
        ).first()

        # 获取发布历史
        history_records = db.query(PublishHistory).filter(
            PublishHistory.document_id == document_id
        ).order_by(desc(PublishHistory.action_time)).all()

        # 构建响应
        publish_history = [
            PublishHistoryResponse.model_validate(record)
            for record in history_records
        ]

        return DocumentPublishDetail(
            document_id=document.id,
            title=document.title,
            summary=document.summary,
            file_type=document.file_type,
            created_at=document.created_at,
            publish_record=PublishRecordResponse.model_validate(publish_record) if publish_record else None,
            publish_history=publish_history
        )

    @staticmethod
    def unpublish_document(
            db: Session,
            user_id: int,
            document_id: int,
            request: UnpublishRequest
    ) -> PublishRecordResponse:
        """撤回已发布文档"""

        # 检查发布记录
        publish_record = db.query(PublishRecord).filter(
            and_(
                PublishRecord.document_id == document_id,
                PublishRecord.user_id == user_id,
                PublishRecord.publish_status == "published"
            )
        ).first()

        if not publish_record:
            raise HTTPException(status_code=404, detail="文档未发布或无权限")

        # 更新状态
        old_status = publish_record.publish_status
        publish_record.publish_status = "unpublished"
        publish_record.unpublish_time = datetime.utcnow()
        publish_record.unpublish_reason = request.unpublish_reason
        publish_record.updated_at = datetime.utcnow()

        # 记录历史
        history = PublishHistory(
            publish_record_id=publish_record.id,
            document_id=document_id,
            user_id=user_id,
            action_type="unpublish",
            action_reason=request.unpublish_reason,
            old_status=old_status,
            new_status="unpublished",
            operator_id=user_id
        )
        db.add(history)

        # 更新文档状态
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "draft"
            document.publish_time = None

        db.commit()
        db.refresh(publish_record)

        return PublishRecordResponse.model_validate(publish_record)

    @staticmethod
    def get_my_publish_records(
            db: Session,
            user_id: int,
            page: int = 1,
            size: int = 20
    ) -> Dict[str, Any]:
        """获取我的发布记录"""

        # 查询用户的发布记录
        query = db.query(PublishRecord, Document).join(
            Document, PublishRecord.document_id == Document.id
        ).filter(PublishRecord.user_id == user_id)

        # 按创建时间倒序
        query = query.order_by(desc(PublishRecord.created_at))

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * size
        results = query.offset(offset).limit(size).all()

        # 构建响应
        items = []
        for publish_record, document in results:
            item = {
                "publish_record": PublishRecordResponse.model_validate(publish_record),
                "document": {
                    "id": document.id,
                    "title": document.title,
                    "summary": document.summary,
                    "file_type": document.file_type
                }
            }
            items.append(item)

        pages = (total + size - 1) // size

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    @staticmethod
    def get_publish_stats(db: Session, user_id: int = None) -> PublishStatsResponse:
        """获取发布统计"""

        # 基础查询
        base_query = db.query(PublishRecord)
        if user_id:
            base_query = base_query.filter(PublishRecord.user_id == user_id)

        # 统计各种状态的数量
        total_published = base_query.filter(PublishRecord.publish_status == "published").count()
        total_drafts = base_query.filter(PublishRecord.publish_status == "draft").count()
        pending_review = base_query.filter(PublishRecord.publish_status == "pending_review").count()
        featured_count = base_query.filter(
            and_(
                PublishRecord.publish_status == "published",
                PublishRecord.is_featured == True
            )
        ).count()

        # 今日发布数量
        today = datetime.utcnow().date()
        today_published = base_query.filter(
            and_(
                PublishRecord.publish_status == "published",
                func.date(PublishRecord.publish_time) == today
            )
        ).count()

        # 总浏览量
        total_views = db.query(func.sum(PublishRecord.view_count)).filter(
            PublishRecord.publish_status == "published"
        ).scalar() or 0

        if user_id:
            total_views = base_query.filter(
                PublishRecord.publish_status == "published"
            ).with_entities(func.sum(PublishRecord.view_count)).scalar() or 0

        return PublishStatsResponse(
            total_published=total_published,
            total_drafts=total_drafts,
            pending_review=pending_review,
            today_published=today_published,
            featured_count=featured_count,
            total_views=total_views
        )

    @staticmethod
    def increment_view_count(db: Session, document_id: int):
        """增加文档浏览量"""
        publish_record = db.query(PublishRecord).filter(
            and_(
                PublishRecord.document_id == document_id,
                PublishRecord.publish_status == "published"
            )
        ).first()

        if publish_record:
            publish_record.view_count += 1
            db.commit()