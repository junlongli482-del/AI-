# app/modules/v2/tech_square/services.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from .models import TechSquareQueries
from .schemas import (
    DocumentListRequest, DocumentListResponse, DocumentItemResponse,
    DocumentDetailResponse, CategoryStatsResponse, HotDocumentsResponse,
    TechSquareStatsResponse, SearchRequest
)
# 修复导入路径 - 使用相对路径
from ..document_manager.models import Document  # 修改这行
from ..document_publish.models import PublishRecord  # 修改这行
from ...v1.user_register.models import User  # 修改这行

# 后面的代码保持不变...


class TechSquareService:
    """技术广场业务逻辑服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_document_list(self, request: DocumentListRequest) -> DocumentListResponse:
        """
        获取文档列表（分页 + 筛选 + 搜索）

        核心逻辑：
        1. 构建查询条件
        2. 执行分页查询
        3. 组装响应数据
        """
        # 构建查询
        query = TechSquareQueries.get_published_documents_query(
            db=self.db,
            search=request.search,
            file_type=request.file_type.value if request.file_type else None,
            time_filter=request.time_filter.value if request.time_filter else None,
            sort_by=request.sort_by.value
        )

        # 计算总数（性能优化：只查询必要字段）
        total = query.count()

        # 分页查询
        offset = (request.page - 1) * request.size
        documents = query.offset(offset).limit(request.size).all()

        # 转换为响应模型
        document_items = []
        for doc in documents:
            document_items.append(DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                publish_time=doc.publish_time,
                view_count=doc.view_count,
                is_featured=doc.is_featured
            ))

        # 计算分页信息
        total_pages = (total + request.size - 1) // request.size

        return DocumentListResponse(
            documents=document_items,
            total=total,
            page=request.page,
            size=request.size,
            total_pages=total_pages,
            has_next=request.page < total_pages,
            has_prev=request.page > 1
        )

    def get_document_detail(self, document_id: int) -> Optional[DocumentDetailResponse]:
        """
        获取文档详情

        业务逻辑：
        1. 验证文档是否已发布
        2. 返回完整文档信息
        3. 不在此处增加浏览量（由专门接口处理）
        """
        # JOIN查询获取文档和发布信息
        result = self.db.query(
            Document.id,
            Document.title,
            Document.content,
            Document.summary,
            Document.file_type,
            Document.file_path,
            Document.user_id,
            PublishRecord.publish_time,
            PublishRecord.view_count,
            PublishRecord.is_featured
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).filter(
            Document.id == document_id,
            PublishRecord.publish_status == 'published'
        ).first()

        if not result:
            return None

        return DocumentDetailResponse(
            id=result.id,
            title=result.title,
            content=result.content,
            summary=result.summary,
            file_type=result.file_type,
            file_path=result.file_path,
            user_id=result.user_id,
            publish_time=result.publish_time,
            view_count=result.view_count,
            is_featured=result.is_featured
        )

    def search_documents(self, request: SearchRequest) -> DocumentListResponse:
        """
        搜索文档

        搜索策略：
        1. 标题匹配优先级最高
        2. 摘要内容匹配次之
        3. 按相关度排序
        """
        # 构建搜索查询
        query = TechSquareQueries.get_published_documents_query(
            db=self.db,
            search=request.keyword,
            file_type=request.file_type.value if request.file_type else None,
            sort_by="latest"  # 搜索结果按最新排序
        )

        # 分页处理
        total = query.count()
        offset = (request.page - 1) * request.size
        documents = query.offset(offset).limit(request.size).all()

        # 组装响应
        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                publish_time=doc.publish_time,
                view_count=doc.view_count,
                is_featured=doc.is_featured
            )
            for doc in documents
        ]

        total_pages = (total + request.size - 1) // request.size

        return DocumentListResponse(
            documents=document_items,
            total=total,
            page=request.page,
            size=request.size,
            total_pages=total_pages,
            has_next=request.page < total_pages,
            has_prev=request.page > 1
        )

    def get_category_stats(self) -> CategoryStatsResponse:
        """获取分类统计信息"""
        stats = TechSquareQueries.get_category_stats(self.db)

        return CategoryStatsResponse(
            md_count=stats.get('md', 0),
            pdf_count=stats.get('pdf', 0),
            total_count=stats.get('md', 0) + stats.get('pdf', 0)
        )

    def get_hot_documents(self, limit: int = 10) -> HotDocumentsResponse:
        """获取热门文档"""
        documents = TechSquareQueries.get_hot_documents(self.db, limit).all()

        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                publish_time=doc.publish_time,
                view_count=doc.view_count,
                is_featured=doc.is_featured
            )
            for doc in documents
        ]

        return HotDocumentsResponse(documents=document_items)

    def get_latest_documents(self, limit: int = 10) -> HotDocumentsResponse:
        """获取最新发布文档"""
        query = TechSquareQueries.get_published_documents_query(
            db=self.db,
            sort_by="latest"
        )

        documents = query.limit(limit).all()

        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                publish_time=doc.publish_time,
                view_count=doc.view_count,
                is_featured=doc.is_featured
            )
            for doc in documents
        ]

        return HotDocumentsResponse(documents=document_items)

    def get_tech_square_stats(self) -> TechSquareStatsResponse:
        """获取技术广场统计信息"""
        # 总发布文档数
        total_documents = self.db.query(PublishRecord).filter(
            PublishRecord.publish_status == 'published'
        ).count()

        # 总浏览量
        total_views = self.db.query(
            func.sum(PublishRecord.view_count)
        ).filter(
            PublishRecord.publish_status == 'published'
        ).scalar() or 0

        # 今日发布数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_published = self.db.query(PublishRecord).filter(
            PublishRecord.publish_status == 'published',
            PublishRecord.publish_time >= today_start
        ).count()

        # 精选文档数
        featured_count = self.db.query(PublishRecord).filter(
            PublishRecord.publish_status == 'published',
            PublishRecord.is_featured == True
        ).count()

        # 分类统计
        category_stats = self.get_category_stats()

        return TechSquareStatsResponse(
            total_documents=total_documents,
            total_views=int(total_views),
            today_published=today_published,
            featured_count=featured_count,
            category_stats=category_stats
        )

    def increment_view_count(self, document_id: int) -> bool:
        """
        增加文档浏览量

        业务逻辑：
        1. 验证文档是否已发布
        2. 原子性更新浏览量
        3. 返回操作结果
        """
        # 查找发布记录
        publish_record = self.db.query(PublishRecord).filter(
            PublishRecord.document_id == document_id,
            PublishRecord.publish_status == 'published'
        ).first()

        if not publish_record:
            return False

        # 增加浏览量
        publish_record.view_count += 1
        self.db.commit()

        return True