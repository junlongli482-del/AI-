"""
文件上传模块 - API路由
功能：提供文件上传相关的HTTP接口
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from .dependencies import (
    get_db,
    get_current_active_user,
    validate_upload_file,
    ensure_upload_directory
)
from .services import FileUploadService, FileValidationService
from .schemas import (
    FileUploadResponse,
    FileValidationResponse,
    UploadRecordResponse,
    FileListResponse,
    FileUploadConfig,
    CreateDocumentFromUploadRequest
)
# 🔧 删除 FileStatus 导入，因为我们不再使用枚举类
from .models import UploadRecord
from app.modules.v1.user_register.models import User

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """测试接口"""
    return {"message": "文件上传模块运行正常", "module": "file_upload"}


@router.get("/config")
async def get_upload_config():
    """获取文件上传配置信息"""
    return FileUploadConfig(
        max_file_size_mb=50,
        allowed_extensions=[".md", ".pdf"],
        upload_path="uploads"
    )


@router.post("/validate", response_model=FileValidationResponse)
async def validate_file_only(
    file: UploadFile = File(..., description="要验证的文件"),
    current_user: User = Depends(get_current_active_user)
):
    """仅验证文件，不保存"""
    try:
        # 验证文件基本要求
        validate_upload_file(file)

        # 读取文件内容进行验证
        file_content = await file.read()

        # 重置文件指针
        await file.seek(0)

        # 执行文件验证
        validation_result = FileValidationService.validate_file(file, file_content)

        return validation_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件验证失败: {str(e)}"
        )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文件"""
    try:
        # 1. 基础验证
        validate_upload_file(file)

        # 2. 确保上传目录存在
        upload_dir = ensure_upload_directory(current_user.id)

        # 3. 执行文件上传
        result = await FileUploadService.upload_file(
            db=db,
            file=file,
            user_id=current_user.id,
            upload_dir=upload_dir
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/uploads", response_model=FileListResponse)
async def get_upload_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的文件上传历史"""
    try:
        # 🔧 状态筛选验证 - 直接使用字符串列表
        status_enum = None
        if status_filter:
            valid_statuses = ['uploading', 'uploaded', 'validated', 'failed', 'deleted']
            if status_filter not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的状态值: {status_filter}，有效值: {valid_statuses}"
                )
            status_enum = status_filter

        # 获取上传记录
        records, total = FileUploadService.get_upload_records(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status_filter=status_enum
        )

        # 转换为响应模型
        upload_records = [UploadRecordResponse.from_orm(record) for record in records]

        return FileListResponse(
            files=upload_records,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取上传历史失败: {str(e)}"
        )


@router.get("/uploads/{upload_id}", response_model=UploadRecordResponse)
async def get_upload_detail(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定上传记录的详细信息"""
    try:
        from sqlalchemy import and_

        # 查询上传记录（确保是当前用户的）
        upload_record = db.query(UploadRecord).filter(
            and_(
                UploadRecord.id == upload_id,
                UploadRecord.user_id == current_user.id
            )
        ).first()

        if not upload_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到指定的上传记录"
            )

        return UploadRecordResponse.from_orm(upload_record)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取上传记录详情失败: {str(e)}"
        )


@router.post("/create-document", response_model=dict)
async def create_document_from_upload(
    request: CreateDocumentFromUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从上传的文件创建文档"""
    try:
        result = FileUploadService.create_document_from_upload(
            db=db,
            upload_id=request.upload_id,
            user_id=current_user.id,
            title=request.title,
            summary=request.summary,
            folder_id=request.folder_id
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文档失败: {str(e)}"
        )


@router.delete("/uploads/{upload_id}")
async def delete_upload_record(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除上传记录"""
    try:
        from sqlalchemy import and_

        # 查询上传记录
        upload_record = db.query(UploadRecord).filter(
            and_(
                UploadRecord.id == upload_id,
                UploadRecord.user_id == current_user.id
            )
        ).first()

        if not upload_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到指定的上传记录"
            )

        # 检查是否已关联文档
        if upload_record.document_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该上传记录已关联文档，无法删除"
            )

        # 🔧 标记为已删除 - 直接使用字符串
        upload_record.status = 'deleted'
        db.commit()

        return {
            "success": True,
            "message": "上传记录已删除",
            "upload_id": upload_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除上传记录失败: {str(e)}"
        )


@router.get("/stats")
async def get_upload_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的上传统计信息"""
    try:
        from sqlalchemy import func

        # 基础统计查询
        base_query = db.query(UploadRecord).filter(UploadRecord.user_id == current_user.id)

        # 总上传数
        total_uploads = base_query.count()

        # 按状态统计
        status_stats = db.query(
            UploadRecord.status,
            func.count(UploadRecord.id).label('count')
        ).filter(
            UploadRecord.user_id == current_user.id
        ).group_by(UploadRecord.status).all()

        # 按文件类型统计
        type_stats = db.query(
            UploadRecord.file_type,
            func.count(UploadRecord.id).label('count'),
            func.sum(UploadRecord.file_size).label('total_size')
        ).filter(
            UploadRecord.user_id == current_user.id
        ).group_by(UploadRecord.file_type).all()

        # 总文件大小
        total_size = db.query(
            func.sum(UploadRecord.file_size)
        ).filter(
            UploadRecord.user_id == current_user.id
        ).scalar() or 0

        return {
            "total_uploads": total_uploads,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "status_distribution": {
                status: count for status, count in status_stats
            },
            "type_distribution": [
                {
                    "file_type": file_type,
                    "count": count,
                    "total_size_bytes": total_size or 0,
                    "total_size_mb": round((total_size or 0) / (1024 * 1024), 2)
                }
                for file_type, count, total_size in type_stats
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )