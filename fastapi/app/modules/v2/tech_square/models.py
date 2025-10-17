# app/modules/v2/tech_square/models.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# 修复导入路径 - 使用相对路径
from ..document_manager.models import Document  # 修改这行
from ..document_publish.models import PublishRecord  # 修改这行

# 后面的代码保持不变...


class TechSquareQueries:
    """技术广场专用查询类 - 封装复杂查询逻辑"""

    @staticmethod
    def get_published_documents_query(
            db: Session,
            search: Optional[str] = None,
            file_type: Optional[str] = None,
            time_filter: Optional[str] = None,
            sort_by: str = "latest"
    ):
        """
        构建已发布文档查询

        Args:
            search: 搜索关键词
            file_type: 文件类型筛选 (md/pdf)
            time_filter: 时间筛选 (today/week/month)
            sort_by: 排序方式 (latest/popular/recommended)
        """
        # 基础查询：JOIN文档表和发布记录表
        query = db.query(
            Document.id,
            Document.title,
            Document.summary,
            Document.file_type,
            Document.user_id,
            PublishRecord.publish_time,
            PublishRecord.view_count,
            PublishRecord.is_featured
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).filter(
            PublishRecord.publish_status == 'published'
        )

        # 搜索筛选
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Document.title.like(search_pattern),
                    Document.summary.like(search_pattern)
                )
            )

        # 文件类型筛选
        if file_type and file_type in ['md', 'pdf']:
            query = query.filter(Document.file_type == file_type)

        # 时间筛选
        if time_filter:
            now = datetime.utcnow()
            if time_filter == 'today':
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_filter == 'week':
                start_time = now - timedelta(days=7)
            elif time_filter == 'month':
                start_time = now - timedelta(days=30)
            else:
                start_time = None

            if start_time:
                query = query.filter(PublishRecord.publish_time >= start_time)

        # 排序逻辑
        if sort_by == "popular":
            query = query.order_by(desc(PublishRecord.view_count))
        elif sort_by == "recommended":
            # 综合推荐算法：最近3天的文档 + 浏览量权重
            recent_boost = func.CASE(
                (PublishRecord.publish_time >= datetime.utcnow() - timedelta(days=3), 100),
                else_=0
            )
            query = query.order_by(desc(PublishRecord.view_count + recent_boost))
        else:  # latest
            query = query.order_by(desc(PublishRecord.publish_time))

        return query

    @staticmethod
    def get_category_stats(db: Session) -> Dict[str, int]:
        """获取分类统计"""
        stats = db.query(
            Document.file_type,
            func.count(Document.id).label('count')
        ).join(
            PublishRecord, Document.id == PublishRecord.document_id
        ).filter(
            PublishRecord.publish_status == 'published'
        ).group_by(Document.file_type).all()

        result = {'md': 0, 'pdf': 0}
        for stat in stats:
            result[stat.file_type] = stat.count

        return result

    @staticmethod
    def get_hot_documents(db: Session, limit: int = 10):
        """获取热门文档（按浏览量排序）"""
        return TechSquareQueries.get_published_documents_query(
            db, sort_by="popular"
        ).limit(limit)