"""
文档管理模块 - 业务逻辑服务
功能：处理文档和文件夹的核心业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status
from typing import List, Optional, Tuple
import os
from datetime import datetime

from .models import Folder, Document, FolderLevel, DocumentStatus, FileType
from .schemas import (
    FolderCreateRequest, FolderResponse, FolderTreeResponse,
    DocumentCreateRequest, DocumentUpdateRequest, DocumentResponse,
    DocumentListResponse, DocumentListWithPaginationResponse
)

class FolderService:
    """文件夹服务类"""

    @staticmethod
    def create_folder(db: Session, folder_data: FolderCreateRequest, user_id: int) -> FolderResponse:
        """创建文件夹"""
        # 检查文件夹名称是否重复（同一用户同一父目录下）
        existing_folder = db.query(Folder).filter(
            and_(
                Folder.name == folder_data.name,
                Folder.parent_id == folder_data.parent_id,
                Folder.user_id == user_id
            )
        ).first()

        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该位置已存在同名文件夹"
            )

        # 如果有父文件夹，检查父文件夹是否存在且属于当前用户
        level = 1  # 默认根目录
        if folder_data.parent_id:
            parent_folder = db.query(Folder).filter(
                and_(
                    Folder.id == folder_data.parent_id,
                    Folder.user_id == user_id
                )
            ).first()

            if not parent_folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父文件夹不存在"
                )

            # 检查层级限制（最多3层）
            if parent_folder.level >= 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文件夹层级不能超过3层"
                )

            level = parent_folder.level + 1

        # 创建文件夹
        new_folder = Folder(
            name=folder_data.name,
            parent_id=folder_data.parent_id,
            user_id=user_id,
            level=level
        )

        db.add(new_folder)
        db.commit()
        db.refresh(new_folder)

        return FolderResponse.model_validate(new_folder)

    @staticmethod
    def get_folder_tree(db: Session, user_id: int) -> List[FolderTreeResponse]:
        """获取用户的文件夹树形结构"""
        # 获取用户所有文件夹
        folders = db.query(Folder).filter(Folder.user_id == user_id).all()

        # 构建树形结构
        def build_tree(parent_id: Optional[int] = None) -> List[FolderTreeResponse]:
            tree = []
            for folder in folders:
                if folder.parent_id == parent_id:
                    # 计算该文件夹下的文档数量
                    doc_count = db.query(Document).filter(
                        and_(
                            Document.folder_id == folder.id,
                            Document.user_id == user_id
                        )
                    ).count()

                    folder_node = FolderTreeResponse(
                        id=folder.id,
                        name=folder.name,
                        level=folder.level,
                        children=build_tree(folder.id),
                        document_count=doc_count
                    )
                    tree.append(folder_node)
            return tree

        return build_tree()

    @staticmethod
    def delete_folder(db: Session, folder_id: int, user_id: int) -> bool:
        """删除文件夹"""
        folder = db.query(Folder).filter(
            and_(Folder.id == folder_id, Folder.user_id == user_id)
        ).first()

        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件夹不存在"
            )

        # 检查是否有子文件夹或文档
        has_children = db.query(Folder).filter(Folder.parent_id == folder_id).first()
        has_documents = db.query(Document).filter(Document.folder_id == folder_id).first()

        if has_children or has_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件夹不为空，无法删除。请先删除子文件夹和文档"
            )

        db.delete(folder)
        db.commit()
        return True

class DocumentService:
    """文档服务类"""

    @staticmethod
    def create_document(db: Session, doc_data: DocumentCreateRequest, user_id: int) -> DocumentResponse:
        """创建文档"""
        # 如果指定了文件夹，检查文件夹是否存在且属于当前用户
        if doc_data.folder_id:
            folder = db.query(Folder).filter(
                and_(
                    Folder.id == doc_data.folder_id,
                    Folder.user_id == user_id
                )
            ).first()

            if not folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的文件夹不存在"
                )

        # 检查同一文件夹下是否有同名文档
        existing_doc = db.query(Document).filter(
            and_(
                Document.title == doc_data.title,
                Document.folder_id == doc_data.folder_id,
                Document.user_id == user_id
            )
        ).first()

        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该文件夹下已存在同名文档"
            )

        # 计算内容大小（字符数）
        content_size = len(doc_data.content or "") if doc_data.content else 0

        # 🔧 关键修改：直接使用字符串值，不使用枚举类
        new_document = Document(
            title=doc_data.title,
            content=doc_data.content,
            summary=doc_data.summary,
            folder_id=doc_data.folder_id,
            user_id=user_id,
            file_type=doc_data.file_type.value,  # 使用.value获取字符串值
            file_size=content_size,
            status='draft'  # 直接使用字符串
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return DocumentService._build_document_response(db, new_document)

    @staticmethod
    def get_document(db: Session, doc_id: int, user_id: int) -> DocumentResponse:
        """获取单个文档详情"""
        document = db.query(Document).filter(
            and_(Document.id == doc_id, Document.user_id == user_id)
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

        return DocumentService._build_document_response(db, document)

    @staticmethod
    def update_document(db: Session, doc_id: int, doc_data: DocumentUpdateRequest, user_id: int) -> DocumentResponse:
        """更新文档"""
        document = db.query(Document).filter(
            and_(Document.id == doc_id, Document.user_id == user_id)
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

        # 更新字段
        if doc_data.title is not None:
            # 检查新标题是否重复
            existing_doc = db.query(Document).filter(
                and_(
                    Document.title == doc_data.title,
                    Document.folder_id == (doc_data.folder_id if doc_data.folder_id is not None else document.folder_id),
                    Document.user_id == user_id,
                    Document.id != doc_id
                )
            ).first()

            if existing_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该文件夹下已存在同名文档"
                )

            document.title = doc_data.title

        if doc_data.content is not None:
            document.content = doc_data.content
            document.file_size = len(doc_data.content)

        if doc_data.summary is not None:
            document.summary = doc_data.summary

        if doc_data.folder_id is not None:
            # 检查新文件夹是否存在
            if doc_data.folder_id != 0:  # 0表示移到根目录
                folder = db.query(Folder).filter(
                    and_(
                        Folder.id == doc_data.folder_id,
                        Folder.user_id == user_id
                    )
                ).first()

                if not folder:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="指定的文件夹不存在"
                    )

                document.folder_id = doc_data.folder_id
            else:
                document.folder_id = None

        db.commit()
        db.refresh(document)

        return DocumentService._build_document_response(db, document)

    @staticmethod
    def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
        """删除文档"""
        document = db.query(Document).filter(
            and_(Document.id == doc_id, Document.user_id == user_id)
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

        # 如果有文件路径，删除物理文件
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"删除文件失败: {e}")

        db.delete(document)
        db.commit()
        return True

    @staticmethod
    def get_documents_list(
        db: Session,
        user_id: int,
        folder_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> DocumentListWithPaginationResponse:
        """获取文档列表（分页）"""
        # 构建查询条件
        query = db.query(Document).filter(Document.user_id == user_id)

        if folder_id is not None:
            if folder_id == 0:  # 0表示根目录（无文件夹）
                query = query.filter(Document.folder_id.is_(None))
            else:
                query = query.filter(Document.folder_id == folder_id)

        # 获取总数
        total = query.count()

        # 分页查询
        documents = query.order_by(desc(Document.updated_at)).offset((page - 1) * page_size).limit(page_size).all()

        # 构建响应
        doc_list = []
        for doc in documents:
            folder_name = None
            if doc.folder_id:
                folder = db.query(Folder).filter(Folder.id == doc.folder_id).first()
                folder_name = folder.name if folder else None

            doc_list.append(DocumentListResponse(
                id=doc.id,
                title=doc.title,
                file_type=doc.file_type,  # 直接使用字符串值
                file_size=doc.file_size,
                status=doc.status,  # 直接使用字符串值
                folder_id=doc.folder_id,
                folder_name=folder_name,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))

        total_pages = (total + page_size - 1) // page_size

        return DocumentListWithPaginationResponse(
            documents=doc_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def _build_document_response(db: Session, document: Document) -> DocumentResponse:
        """构建文档响应对象"""
        folder_name = None
        if document.folder_id:
            folder = db.query(Folder).filter(Folder.id == document.folder_id).first()
            folder_name = folder.name if folder else None

        return DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            file_path=document.file_path,
            file_type=document.file_type,  # 直接使用字符串值
            file_size=document.file_size,
            summary=document.summary,
            status=document.status,  # 直接使用字符串值
            publish_time=document.publish_time,
            review_message=document.review_message,
            folder_id=document.folder_id,
            folder_name=folder_name,
            created_at=document.created_at,
            updated_at=document.updated_at
        )