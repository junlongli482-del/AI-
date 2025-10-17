# app/modules/v2/tech_square/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

# 修复导入路径 - 使用相对路径
from ....core.database import get_db  # 修改这行
from .services import TechSquareService
from .schemas import (
    DocumentListRequest, DocumentListResponse, DocumentDetailResponse,
    CategoryStatsResponse, HotDocumentsResponse, TechSquareStatsResponse,
    SearchRequest, SortOption, TimeFilter, FileTypeFilter
)

router = APIRouter()

# 后面的代码保持不变...


@router.get("/test")
async def test_tech_square():
    """测试技术广场模块连通性"""
    return {
        "status": "success",
        "message": "Tech Square模块运行正常",
        "module": "tech_square",
        "version": "v2"
    }


@router.get("/documents", response_model=DocumentListResponse)
async def get_document_list(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
        file_type: Optional[FileTypeFilter] = Query(None, description="文件类型筛选"),
        time_filter: Optional[TimeFilter] = Query(None, description="时间筛选"),
        sort_by: SortOption = Query(SortOption.LATEST, description="排序方式"),
        db: Session = Depends(get_db)
):
    """
    获取文档列表

    支持功能：
    - 分页查询
    - 关键词搜索（标题、摘要）
    - 文件类型筛选（md/pdf）
    - 时间筛选（今日/本周/本月）
    - 多种排序（最新/最热/推荐）
    """
    try:
        request = DocumentListRequest(
            page=page,
            size=size,
            search=search,
            file_type=file_type,
            time_filter=time_filter,
            sort_by=sort_by
        )

        service = TechSquareService(db)
        return service.get_document_list(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document_detail(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    获取文档详情

    返回已发布文档的完整信息，包括内容
    """
    try:
        service = TechSquareService(db)
        document = service.get_document_detail(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在或未发布")

        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档详情失败: {str(e)}")


@router.get("/search", response_model=DocumentListResponse)
async def search_documents(
        keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=50, description="每页数量"),
        file_type: Optional[FileTypeFilter] = Query(None, description="文件类型筛选"),
        db: Session = Depends(get_db)
):
    """
    搜索文档

    智能搜索功能：
    - 标题匹配
    - 摘要内容匹配
    - 支持文件类型筛选
    """
    try:
        request = SearchRequest(
            keyword=keyword,
            page=page,
            size=size,
            file_type=file_type
        )

        service = TechSquareService(db)
        return service.search_documents(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索文档失败: {str(e)}")


@router.get("/category-stats", response_model=CategoryStatsResponse)
async def get_category_stats(db: Session = Depends(get_db)):
    """
    获取分类统计信息

    返回各文件类型的文档数量
    """
    try:
        service = TechSquareService(db)
        return service.get_category_stats()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类统计失败: {str(e)}")


@router.get("/hot-documents", response_model=HotDocumentsResponse)
async def get_hot_documents(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db)
):
    """
    获取热门文档

    按浏览量降序排序
    """
    try:
        service = TechSquareService(db)
        return service.get_hot_documents(limit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门文档失败: {str(e)}")


@router.get("/latest-documents", response_model=HotDocumentsResponse)
async def get_latest_documents(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db)
):
    """
    获取最新发布文档

    按发布时间降序排序
    """
    try:
        service = TechSquareService(db)
        return service.get_latest_documents(limit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最新文档失败: {str(e)}")


@router.get("/stats", response_model=TechSquareStatsResponse)
async def get_tech_square_stats(db: Session = Depends(get_db)):
    """
    获取技术广场统计信息

    包括：
    - 总文档数、总浏览量
    - 今日发布数、精选文档数
    - 分类统计
    """
    try:
        service = TechSquareService(db)
        return service.get_tech_square_stats()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/view/{document_id}")
async def increment_view_count(
        document_id: int,
        db: Session = Depends(get_db)
):
    """
    增加文档浏览量

    用于前端访问文档时调用
    """
    try:
        service = TechSquareService(db)
        success = service.increment_view_count(document_id)

        if not success:
            raise HTTPException(status_code=404, detail="文档不存在或未发布")

        return {"status": "success", "message": "浏览量已增加"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新浏览量失败: {str(e)}")