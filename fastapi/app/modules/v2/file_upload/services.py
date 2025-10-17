"""
文件上传模块 - 业务逻辑
功能：处理文件上传、验证、存储等核心业务
"""

import os
import uuid
import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import UploadRecord
from .schemas import FileValidationResponse, FileUploadResponse, UploadRecordResponse
from app.modules.v2.document_manager.models import Document
from app.modules.v2.document_manager.services import DocumentService


class FileValidationService:
    """文件验证服务"""

    # 文件大小限制（字节）
    MAX_FILE_SIZES = {
        'md': 20 * 1024 * 1024,    # 10MB
        'pdf': 100 * 1024 * 1024,   # 50MB
    }

    @classmethod
    def validate_file(cls, file: UploadFile, file_content: bytes) -> FileValidationResponse:
        """
        综合验证文件

        Args:
            file: 上传的文件对象
            file_content: 文件内容字节

        Returns:
            FileValidationResponse: 验证结果
        """
        try:
            # 1. 基础信息检查
            file_ext = Path(file.filename).suffix.lower().lstrip('.')
            file_size = len(file_content)

            # 2. 文件类型检查
            if file_ext not in ['md', 'pdf']:
                return FileValidationResponse(
                    is_valid=False,
                    file_type=file_ext,
                    file_size=file_size,
                    validation_details={},
                    error_message="不支持的文件类型"
                )

            # 3. 文件大小检查
            max_size = cls.MAX_FILE_SIZES.get(file_ext, 0)
            if file_size > max_size:
                return FileValidationResponse(
                    is_valid=False,
                    file_type=file_ext,
                    file_size=file_size,
                    validation_details={"max_size": max_size},
                    error_message=f"文件大小超出限制，最大允许 {max_size // (1024*1024)}MB"
                )

            # 4. 文件头验证
            validation_result = cls._validate_file_signature(file_ext, file_content)
            if not validation_result['is_valid']:
                return FileValidationResponse(
                    is_valid=False,
                    file_type=file_ext,
                    file_size=file_size,
                    validation_details=validation_result,
                    error_message=validation_result.get('error', '文件格式验证失败')
                )

            # 5. 内容完整性检查
            content_validation = cls._validate_file_content(file_ext, file_content)

            return FileValidationResponse(
                is_valid=content_validation['is_valid'],
                file_type=file_ext,
                file_size=file_size,
                validation_details={
                    'signature_check': validation_result,
                    'content_check': content_validation
                },
                error_message=content_validation.get('error') if not content_validation['is_valid'] else None
            )

        except Exception as e:
            return FileValidationResponse(
                is_valid=False,
                file_type=file_ext if 'file_ext' in locals() else 'unknown',
                file_size=len(file_content) if file_content else 0,
                validation_details={},
                error_message=f"文件验证过程中发生错误: {str(e)}"
            )

    @classmethod
    def _validate_file_signature(cls, file_type: str, content: bytes) -> Dict[str, Any]:
        """验证文件头签名"""
        if file_type == 'pdf':
            # PDF文件必须以%PDF-开头
            if not content.startswith(b'%PDF-'):
                return {
                    'is_valid': False,
                    'error': '不是有效的PDF文件格式'
                }
            return {'is_valid': True}

        elif file_type == 'md':
            # Markdown文件验证UTF-8编码
            try:
                content.decode('utf-8')
                return {'is_valid': True}
            except UnicodeDecodeError:
                return {
                    'is_valid': False,
                    'error': 'Markdown文件必须是UTF-8编码'
                }

        return {'is_valid': True}

    @classmethod
    def _validate_file_content(cls, file_type: str, content: bytes) -> Dict[str, Any]:
        """验证文件内容完整性"""
        if file_type == 'pdf':
            return cls._validate_pdf_content(content)
        elif file_type == 'md':
            return cls._validate_md_content(content)

        return {'is_valid': True}

    @classmethod
    def _validate_pdf_content(cls, content: bytes) -> Dict[str, Any]:
        """验证PDF文件内容"""
        try:
            # 简单的PDF页数估算（基于/Page关键字出现次数）
            page_count = content.count(b'/Type/Page')

            # 如果没有找到标准的页面标记，尝试其他方法
            if page_count == 0:
                page_count = content.count(b'/Type /Page')

            # 页数限制检查
            if page_count > 20:
                return {
                    'is_valid': False,
                    'error': f'PDF文件页数超出限制，当前{page_count}页，最多允许10页',
                    'page_count': page_count
                }

            # 检查PDF文件是否完整（必须有EOF标记）
            if not content.endswith(b'%%EOF') and b'%%EOF' not in content[-100:]:
                return {
                    'is_valid': False,
                    'error': 'PDF文件可能不完整或已损坏'
                }

            return {
                'is_valid': True,
                'page_count': page_count,
                'file_complete': True
            }

        except Exception as e:
            return {
                'is_valid': False,
                'error': f'PDF文件内容验证失败: {str(e)}'
            }

    @classmethod
    def _validate_md_content(cls, content: bytes) -> Dict[str, Any]:
        """验证Markdown文件内容"""
        try:
            # 解码为文本
            text_content = content.decode('utf-8')

            # 基础检查
            char_count = len(text_content)
            line_count = text_content.count('\n') + 1

            # 估算页数（按A4纸标准：约2000字/页）
            estimated_pages = char_count / 2000

            if estimated_pages > 20:
                return {
                    'is_valid': False,
                    'error': f'Markdown文件内容过长，估算约{estimated_pages:.1f}页，最多允许相当于20页A4纸的内容',
                    'char_count': char_count,
                    'estimated_pages': estimated_pages
                }

            return {
                'is_valid': True,
                'char_count': char_count,
                'line_count': line_count,
                'estimated_pages': estimated_pages
            }

        except UnicodeDecodeError as e:
            return {
                'is_valid': False,
                'error': f'Markdown文件编码错误: {str(e)}'
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': f'Markdown文件内容验证失败: {str(e)}'
            }


class FileUploadService:
    """文件上传服务"""

    @staticmethod
    def generate_unique_filename(original_filename: str, user_id: int) -> str:
        """生成唯一的文件名"""
        file_ext = Path(original_filename).suffix
        timestamp = str(int(time.time() * 1000))
        unique_id = str(uuid.uuid4())[:8]
        return f"user_{user_id}_{timestamp}_{unique_id}{file_ext}"

    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """计算文件MD5哈希值"""
        return hashlib.md5(content).hexdigest()

    @staticmethod
    async def upload_file(
        db: Session,
        file: UploadFile,
        user_id: int,
        upload_dir: str
    ) -> FileUploadResponse:
        """
        处理文件上传的完整流程
        """
        try:
            # 1. 读取文件内容
            file_content = await file.read()

            # 2. 验证文件
            validation_result = FileValidationService.validate_file(file, file_content)

            if not validation_result.is_valid:
                return FileUploadResponse(
                    success=False,
                    message=f"文件验证失败: {validation_result.error_message}",
                    upload_id=None,
                    file_info=validation_result.validation_details
                )

            # 3. 生成存储文件名和路径
            stored_filename = FileUploadService.generate_unique_filename(file.filename, user_id)
            file_path = os.path.join(upload_dir, stored_filename)

            # 4. 保存文件到磁盘
            with open(file_path, "wb") as f:
                f.write(file_content)

            # 5. 创建上传记录 - 🔧 直接使用字符串值
            upload_record = UploadRecord(
                original_filename=file.filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=validation_result.file_size,
                file_type=validation_result.file_type,  # 直接使用字符串
                mime_type=file.content_type or f"application/{validation_result.file_type}",
                status='validated',  # 直接使用字符串
                validation_message="文件验证通过",
                user_id=user_id
            )

            db.add(upload_record)
            db.commit()
            db.refresh(upload_record)

            return FileUploadResponse(
                success=True,
                message="文件上传成功",
                upload_id=upload_record.id,
                file_info={
                    "original_filename": file.filename,
                    "file_size": validation_result.file_size,
                    "file_type": validation_result.file_type,
                    "validation_details": validation_result.validation_details
                }
            )

        except Exception as e:
            # 如果出错，尝试清理已创建的文件
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

            return FileUploadResponse(
                success=False,
                message=f"文件上传失败: {str(e)}",
                upload_id=None,
                file_info=None
            )

    @staticmethod
    def get_upload_records(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None  # 🔧 改为字符串类型
    ) -> Tuple[list, int]:
        """获取用户的上传记录"""
        query = db.query(UploadRecord).filter(UploadRecord.user_id == user_id)

        if status_filter:
            query = query.filter(UploadRecord.status == status_filter)

        total = query.count()

        records = query.order_by(UploadRecord.created_at.desc())\
                      .offset((page - 1) * page_size)\
                      .limit(page_size)\
                      .all()

        return records, total

    @staticmethod
    def create_document_from_upload(
            db: Session,
            upload_id: int,
            user_id: int,
            title: str,
            summary: Optional[str] = None,
            folder_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """从上传文件创建文档"""
        try:
            # 1. 获取上传记录
            upload_record = db.query(UploadRecord).filter(
                and_(
                    UploadRecord.id == upload_id,
                    UploadRecord.user_id == user_id,
                    UploadRecord.status == 'validated'
                )
            ).first()

            if not upload_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="未找到有效的上传记录"
                )

            # 2. 读取文件内容
            if upload_record.file_type == 'md':
                with open(upload_record.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # PDF文件不读取内容，只记录路径
                content = None

            # 3. 🔧 直接创建 Document 对象
            from app.modules.v2.document_manager.models import Document

            document = Document(
                title=title,
                content=content,
                file_path=upload_record.file_path,
                file_type=upload_record.file_type,
                file_size=upload_record.file_size,
                summary=summary,
                folder_id=folder_id,
                user_id=user_id,
                status='draft'  # 默认状态
            )

            db.add(document)
            db.flush()  # 获取 document.id

            # 4. 更新上传记录，关联文档
            upload_record.document_id = document.id
            db.commit()

            return {
                "success": True,
                "message": "文档创建成功",
                "document_id": document.id,
                "upload_id": upload_id
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建文档失败: {str(e)}"
            )