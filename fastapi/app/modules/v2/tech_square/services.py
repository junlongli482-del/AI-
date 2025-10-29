# app/modules/v2/tech_square/services.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from .models import TechSquareQueries
from .schemas import (
    DocumentListRequest, DocumentListResponse, DocumentItemResponse,
    DocumentDetailResponse, CategoryStatsResponse, HotDocumentsResponse,
    TechSquareStatsResponse, SearchRequest, DocumentFileInfoResponse  # 新增
)
# 修复导入路径 - 使用相对路径
from ..document_manager.models import Document  # 修改这行
from ..document_publish.models import PublishRecord  # 修改这行
from ...v1.user_register.models import User  # 修改这行

import urllib.parse
import re
import mimetypes
from pathlib import Path
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import HTTPException, status


# 后面的代码保持不变...


class TechSquareService:
    """技术广场业务逻辑服务类"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 🆕 优化查询方法 ====================

    def _get_documents_with_user_info(self, query_builder_func, *args, **kwargs):
        """
        通用方法：获取文档列表并包含用户信息

        Args:
            query_builder_func: 查询构建函数
            *args, **kwargs: 传递给查询构建函数的参数

        Returns:
            包含用户信息的文档查询结果
        """
        # 使用原有的查询构建逻辑
        base_query = query_builder_func(*args, **kwargs)

        # JOIN用户表获取用户信息
        enhanced_query = self.db.query(
            Document.id,
            Document.title,
            Document.summary,
            Document.file_type,
            Document.user_id,
            User.username,
            User.nickname,
            PublishRecord.publish_time,
            PublishRecord.view_count,
            PublishRecord.is_featured
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).join(
            User, Document.user_id == User.id
        ).filter(
            PublishRecord.publish_status == 'published'
        )

        # 应用原有查询的筛选和排序条件
        # 这里需要根据TechSquareQueries的实现来适配筛选条件
        return enhanced_query

    def _build_document_query_with_filters(self, search=None, file_type=None, time_filter=None, sort_by="latest"):
        """
        构建带筛选条件的文档查询（包含用户信息）
        """
        # 基础查询：JOIN Document + PublishRecord + User
        query = self.db.query(
            Document.id,
            Document.title,
            Document.summary,
            Document.file_type,
            Document.user_id,
            User.username,
            User.nickname,
            PublishRecord.publish_time,
            PublishRecord.view_count,
            PublishRecord.is_featured
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).join(
            User, Document.user_id == User.id
        ).filter(
            PublishRecord.publish_status == 'published'
        )

        # 🔍 搜索筛选
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Document.title.like(search_pattern)) |
                (Document.summary.like(search_pattern))
            )

        # 📁 文件类型筛选
        if file_type:
            query = query.filter(Document.file_type == file_type)

        # 📅 时间筛选
        if time_filter:
            now = datetime.utcnow()
            if time_filter == "today":
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(PublishRecord.publish_time >= start_time)
            elif time_filter == "week":
                start_time = now - timedelta(days=7)
                query = query.filter(PublishRecord.publish_time >= start_time)
            elif time_filter == "month":
                start_time = now - timedelta(days=30)
                query = query.filter(PublishRecord.publish_time >= start_time)

        # 📊 排序
        if sort_by == "popular":
            query = query.order_by(desc(PublishRecord.view_count))
        elif sort_by == "recommended":
            # 推荐算法：最近3天的文档获得加成
            recent_threshold = datetime.utcnow() - timedelta(days=3)
            query = query.order_by(
                desc(
                    func.case(
                        (PublishRecord.publish_time >= recent_threshold, PublishRecord.view_count + 100),
                        else_=PublishRecord.view_count
                    )
                )
            )
        else:  # latest
            query = query.order_by(desc(PublishRecord.publish_time))

        return query

    # ==================== 🆕 文件访问功能 ====================

    @staticmethod
    def _safe_filename(filename: str) -> str:
        """
        生成安全的文件名，处理中文字符和特殊字符
        """
        # 移除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制文件名长度
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        return safe_name

    @staticmethod
    def _encode_filename_for_header(filename: str) -> str:
        """
        为HTTP头部编码文件名，支持中文字符
        """
        # 使用RFC 5987标准编码中文文件名
        encoded_filename = urllib.parse.quote(filename, safe='')
        return f"filename*=UTF-8''{encoded_filename}"

    def _get_published_document_with_file(self, document_id: int):
        """
        获取已发布的文档及其文件信息

        核心安全验证：只能访问已发布的文档
        """
        # JOIN查询获取文档和发布信息
        result = self.db.query(
            Document.id,
            Document.title,
            Document.content,
            Document.file_path,
            Document.file_type,
            Document.file_size,
            PublishRecord.publish_status
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).filter(
            Document.id == document_id,
            PublishRecord.publish_status == 'published'  # 🔑 关键：只能访问已发布文档
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在或未发布"
            )

        return result

    def download_document_file(self, document_id: int, preview: bool = False):
        """
        下载已发布文档的文件（无需认证）

        业务逻辑：
        1. 验证文档是否已发布
        2. 检查文件是否存在
        3. 返回文件响应
        """
        document = self._get_published_document_with_file(document_id)

        # 检查是否有文件路径
        if not document.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档没有关联的文件"
            )

        # 检查文件是否存在
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )

        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            if document.file_type == 'pdf':
                mime_type = 'application/pdf'
            elif document.file_type == 'md':
                mime_type = 'text/markdown'
            else:
                mime_type = 'application/octet-stream'

        # 生成安全的文件名
        safe_title = self._safe_filename(document.title)
        filename = f"{safe_title}.{document.file_type}"

        # 编码文件名用于HTTP头部
        encoded_filename = self._encode_filename_for_header(filename)

        # 根据预览模式设置Content-Disposition
        if preview and document.file_type == 'pdf':
            # 预览模式：浏览器内打开
            disposition = f'inline; {encoded_filename}'
        else:
            # 下载模式：强制下载
            disposition = f'attachment; {encoded_filename}'

        headers = {
            "Content-Disposition": disposition
        }

        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            headers=headers
        )

    def stream_document_file(self, document_id: int):
        """
        流式传输已发布文档文件（无需认证）

        专门优化PDF预览体验
        """
        document = self._get_published_document_with_file(document_id)

        if not document.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档没有关联的文件"
            )

        file_path = Path(document.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )

        # 获取文件大小
        file_size = file_path.stat().st_size

        # 设置MIME类型
        if document.file_type == 'pdf':
            media_type = 'application/pdf'
        elif document.file_type == 'md':
            media_type = 'text/markdown'
        else:
            media_type = 'application/octet-stream'

        # 生成安全的文件名并编码
        safe_title = self._safe_filename(document.title)
        filename = f"{safe_title}.{document.file_type}"
        encoded_filename = self._encode_filename_for_header(filename)

        # 创建文件流生成器
        def file_generator():
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    yield chunk

        # 设置响应头
        headers = {
            'Content-Length': str(file_size),
            'Content-Disposition': f'inline; {encoded_filename}',
            'Accept-Ranges': 'bytes'
        }

        return StreamingResponse(
            file_generator(),
            media_type=media_type,
            headers=headers
        )

    def get_document_file_info(self, document_id: int) -> DocumentFileInfoResponse:
        """
        获取已发布文档的文件信息（无需认证）

        返回文件元数据，不下载内容
        """
        document = self._get_published_document_with_file(document_id)

        # 生成安全的文件名
        safe_title = self._safe_filename(document.title)
        safe_filename = f"{safe_title}.{document.file_type}"

        # 基础信息
        file_info = DocumentFileInfoResponse(
            document_id=document.id,
            title=document.title,
            file_type=document.file_type,
            file_size=document.file_size,
            has_file=bool(document.file_path),
            file_path=document.file_path,
            safe_filename=safe_filename,
            file_exists=False,
            original_filename=None,
            actual_file_size=0,
            mime_type=None,
            size_match=False
        )

        # 如果有文件路径，检查物理文件
        if document.file_path:
            file_path = Path(document.file_path)
            file_exists = file_path.exists()

            file_info.file_exists = file_exists
            file_info.original_filename = f"{document.title}.{document.file_type}"

            if file_exists:
                # 获取实际文件大小和MIME类型
                actual_size = file_path.stat().st_size
                mime_type, _ = mimetypes.guess_type(str(file_path))

                file_info.actual_file_size = actual_size
                file_info.mime_type = mime_type or f"application/{document.file_type}"
                file_info.size_match = actual_size == document.file_size

        return file_info

    def get_document_list(self, request: DocumentListRequest) -> DocumentListResponse:
        """
        获取文档列表（分页 + 筛选 + 搜索）🆕 包含用户信息

        核心逻辑：
        1. 构建查询条件（包含用户信息）
        2. 执行分页查询
        3. 组装响应数据
        """
        # 🆕 使用新的查询方法，包含用户信息
        query = self._build_document_query_with_filters(
            search=request.search,
            file_type=request.file_type.value if request.file_type else None,
            time_filter=request.time_filter.value if request.time_filter else None,
            sort_by=request.sort_by.value
        )

        # 计算总数
        total = query.count()

        # 分页查询
        offset = (request.page - 1) * request.size
        documents = query.offset(offset).limit(request.size).all()

        # 🆕 转换为响应模型（包含用户信息）
        document_items = []
        for doc in documents:
            document_items.append(DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                username=doc.username,  # 🆕 用户名
                nickname=doc.nickname,  # 🆕 昵称
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
        获取文档详情 🆕 包含用户信息

        业务逻辑：
        1. 验证文档是否已发布
        2. 返回完整文档信息（包含用户信息）
        3. 不在此处增加浏览量（由专门接口处理）
        """
        # 🆕 JOIN查询获取文档、发布信息和用户信息
        result = self.db.query(
            Document.id,
            Document.title,
            Document.content,
            Document.summary,
            Document.file_type,
            Document.file_path,
            Document.user_id,
            User.username,  # 🆕 用户名
            User.nickname,  # 🆕 昵称
            PublishRecord.publish_time,
            PublishRecord.view_count,
            PublishRecord.is_featured
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).join(
            User, Document.user_id == User.id  # 🆕 JOIN用户表
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
            username=result.username,  # 🆕 用户名
            nickname=result.nickname,  # 🆕 昵称
            publish_time=result.publish_time,
            view_count=result.view_count,
            is_featured=result.is_featured
        )

    def search_documents(self, request: SearchRequest) -> DocumentListResponse:
        """
        搜索文档 🆕 包含用户信息

        搜索策略：
        1. 标题匹配优先级最高
        2. 摘要内容匹配次之
        3. 按相关度排序
        """
        # 🆕 使用新的查询方法，包含用户信息
        query = self._build_document_query_with_filters(
            search=request.keyword,
            file_type=request.file_type.value if request.file_type else None,
            sort_by="latest"  # 搜索结果按最新排序
        )

        # 分页处理
        total = query.count()
        offset = (request.page - 1) * request.size
        documents = query.offset(offset).limit(request.size).all()

        # 🆕 组装响应（包含用户信息）
        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                username=doc.username,  # 🆕 用户名
                nickname=doc.nickname,  # 🆕 昵称
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
        """获取热门文档 🆕 包含用户信息"""
        # 🆕 使用新的查询方法，包含用户信息
        query = self._build_document_query_with_filters(sort_by="popular")
        documents = query.limit(limit).all()

        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                username=doc.username,  # 🆕 用户名
                nickname=doc.nickname,  # 🆕 昵称
                publish_time=doc.publish_time,
                view_count=doc.view_count,
                is_featured=doc.is_featured
            )
            for doc in documents
        ]

        return HotDocumentsResponse(documents=document_items)

    def get_latest_documents(self, limit: int = 10) -> HotDocumentsResponse:
        """获取最新发布文档 🆕 包含用户信息"""
        # 🆕 使用新的查询方法，包含用户信息
        query = self._build_document_query_with_filters(sort_by="latest")
        documents = query.limit(limit).all()

        document_items = [
            DocumentItemResponse(
                id=doc.id,
                title=doc.title,
                summary=doc.summary or "暂无摘要",
                file_type=doc.file_type,
                user_id=doc.user_id,
                username=doc.username,  # 🆕 用户名
                nickname=doc.nickname,  # 🆕 昵称
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