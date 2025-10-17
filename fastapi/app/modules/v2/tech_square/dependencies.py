# app/modules/v2/tech_square/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

# 修复导入路径 - 使用相对路径
from ....core.database import get_db  # 修改这行
from ..document_publish.models import PublishRecord  # 修改这行
from ..document_manager.models import Document  # 修改这行

# 后面的代码保持不变...


def verify_document_published(document_id: int, db: Session = Depends(get_db)) -> PublishRecord:
    """
    验证文档是否已发布

    通用依赖函数，用于需要验证文档发布状态的接口
    """
    publish_record = db.query(PublishRecord).filter(
        PublishRecord.document_id == document_id,
        PublishRecord.publish_status == 'published'
    ).first()

    if not publish_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或未发布"
        )

    return publish_record


def get_document_with_publish_info(document_id: int, db: Session = Depends(get_db)) -> tuple:
    """
    获取文档及其发布信息

    返回 (Document, PublishRecord) 元组
    """
    result = db.query(Document, PublishRecord).join(
        PublishRecord, Document.id == PublishRecord.document_id
    ).filter(
        Document.id == document_id,
        PublishRecord.publish_status == 'published'
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或未发布"
        )

    return result


class TechSquareConfig:
    """技术广场配置类"""

    # 分页配置
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 20

    # 搜索配置
    MAX_SEARCH_LENGTH = 100
    MIN_SEARCH_LENGTH = 1

    # 热门文档配置
    HOT_DOCUMENTS_LIMIT = 50
    LATEST_DOCUMENTS_LIMIT = 50

    # 推荐算法权重
    RECENT_BOOST_DAYS = 3
    RECENT_BOOST_SCORE = 100