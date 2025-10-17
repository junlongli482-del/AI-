from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import EditorSession, AIOptimization
from .schemas import CreateSessionRequest, UpdateSessionRequest, OptimizeContentRequest
from app.core.ai_client import default_ai_client
from app.modules.v2.document_manager.models import Document

class EditorService:
    """编辑器服务类"""
    
    @staticmethod
    def create_session(db: Session, user_id: int, request: CreateSessionRequest) -> EditorSession:
        """创建编辑器会话"""
        # 如果是编辑现有文档，获取文档内容
        content = request.content
        title = request.title
        
        if request.session_type == "edit_document" and request.document_id:
            document = db.query(Document).filter(
                Document.id == request.document_id,
                Document.user_id == user_id
            ).first()
            
            if not document:
                raise ValueError("文档不存在或无权限访问")
            
            content = document.content or ""
            title = title or document.title
        
        # 创建会话
        session = EditorSession(
            document_id=request.document_id,
            user_id=user_id,
            title=title,
            content=content,
            session_type=request.session_type,
            is_draft=True
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: int, user_id: int) -> Optional[EditorSession]:
        """获取编辑器会话"""
        return db.query(EditorSession).filter(
            EditorSession.id == session_id,
            EditorSession.user_id == user_id
        ).first()
    
    @staticmethod
    def update_session(db: Session, session_id: int, user_id: int, request: UpdateSessionRequest) -> Optional[EditorSession]:
        """更新编辑器会话"""
        session = EditorService.get_session(db, session_id, user_id)
        if not session:
            return None
        
        # 更新字段
        if request.title is not None:
            session.title = request.title
        if request.content is not None:
            session.content = request.content
        if request.is_draft is not None:
            session.is_draft = request.is_draft
        
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def delete_session(db: Session, session_id: int, user_id: int) -> bool:
        """删除编辑器会话"""
        session = EditorService.get_session(db, session_id, user_id)
        if not session:
            return False
        
        db.delete(session)
        db.commit()
        return True
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[EditorSession]:
        """获取用户的编辑器会话列表"""
        return db.query(EditorSession).filter(
            EditorSession.user_id == user_id
        ).order_by(desc(EditorSession.updated_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def optimize_content(db: Session, session_id: int, user_id: int, request: OptimizeContentRequest) -> Dict[str, Any]:
        """AI优化内容"""
        # 验证会话权限
        session = EditorService.get_session(db, session_id, user_id)
        if not session:
            raise ValueError("会话不存在或无权限访问")
        
        try:
            # 调用AI优化
            optimized_content = default_ai_client.optimize_markdown(
                content=request.content,
                optimization_type=request.optimization_type
            )
            
            if not optimized_content:
                raise Exception("AI优化失败，请稍后重试")
            
            # 构建优化提示词记录
            optimization_prompt = f"优化类型: {request.optimization_type}"
            
            # 保存优化记录
            optimization = AIOptimization(
                session_id=session_id,
                user_id=user_id,
                original_content=request.content,
                optimized_content=optimized_content,
                optimization_prompt=optimization_prompt,
                ai_provider="default",
                status="completed"
            )
            
            db.add(optimization)
            db.commit()
            db.refresh(optimization)
            
            return {
                "success": True,
                "message": "内容优化成功",
                "optimization_id": optimization.id,
                "original_content": request.content,
                "optimized_content": optimized_content,
                "can_apply": True
            }
            
        except Exception as e:
            # 保存失败记录
            optimization = AIOptimization(
                session_id=session_id,
                user_id=user_id,
                original_content=request.content,
                optimized_content="",
                optimization_prompt=f"优化失败: {str(e)}",
                ai_provider="default",
                status="failed"
            )
            
            db.add(optimization)
            db.commit()
            
            return {
                "success": False,
                "message": f"优化失败: {str(e)}",
                "optimization_id": optimization.id,
                "original_content": request.content,
                "optimized_content": "",
                "can_apply": False
            }
    
    @staticmethod
    def apply_optimization(db: Session, session_id: int, optimization_id: int, user_id: int) -> bool:
        """应用AI优化结果到会话"""
        # 验证权限
        session = EditorService.get_session(db, session_id, user_id)
        if not session:
            return False
        
        optimization = db.query(AIOptimization).filter(
            AIOptimization.id == optimization_id,
            AIOptimization.session_id == session_id,
            AIOptimization.user_id == user_id,
            AIOptimization.status == "completed"
        ).first()
        
        if not optimization:
            return False
        
        # 应用优化内容
        session.content = optimization.optimized_content
        db.commit()
        
        return True
    
    @staticmethod
    def save_as_document(db: Session, session_id: int, user_id: int, title: str, folder_id: Optional[int] = None, summary: Optional[str] = None) -> Optional[Document]:
        """将编辑器会话保存为正式文档"""
        session = EditorService.get_session(db, session_id, user_id)
        if not session:
            return None
        
        # 如果是编辑现有文档，更新现有文档
        if session.session_type == "edit_document" and session.document_id:
            document = db.query(Document).filter(
                Document.id == session.document_id,
                Document.user_id == user_id
            ).first()
            
            if document:
                document.title = title
                document.content = session.content
                document.summary = summary
                if folder_id is not None:
                    document.folder_id = folder_id
                
                db.commit()
                db.refresh(document)
                
                # 标记会话为非草稿
                session.is_draft = False
                db.commit()
                
                return document
        
        # 创建新文档
        document = Document(
            title=title,
            content=session.content,
            file_type='md',
            summary=summary,
            folder_id=folder_id,
            user_id=user_id,
            status='draft'
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 更新会话关联和状态
        session.document_id = document.id
        session.is_draft = False
        session.title = title
        db.commit()
        
        return document
    
    @staticmethod
    def get_editor_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """获取编辑器统计信息"""
        total_sessions = db.query(EditorSession).filter(EditorSession.user_id == user_id).count()
        draft_sessions = db.query(EditorSession).filter(
            EditorSession.user_id == user_id,
            EditorSession.is_draft == True
        ).count()
        total_optimizations = db.query(AIOptimization).filter(AIOptimization.user_id == user_id).count()
        
        # 最近的会话
        recent_sessions = db.query(EditorSession).filter(
            EditorSession.user_id == user_id
        ).order_by(desc(EditorSession.updated_at)).limit(5).all()
        
        return {
            "total_sessions": total_sessions,
            "draft_sessions": draft_sessions,
            "total_optimizations": total_optimizations,
            "recent_sessions": recent_sessions
        }