from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .dependencies import get_db
from .services import EditorService
from .schemas import (
    CreateSessionRequest, UpdateSessionRequest, OptimizeContentRequest, SaveDocumentRequest,
    EditorSessionResponse, EditorSessionDetailResponse, OptimizeResponse, EditorStatsResponse,
    AIOptimizationResponse
)
from app.modules.v1.user_auth.dependencies import get_current_user
from app.modules.v1.user_register.models import User

# 注意：不设置 prefix 和 tags，由 main.py 自动处理
router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """测试接口"""
    return {"message": "MD Editor 模块运行正常", "version": "1.0.0"}

@router.post("/sessions", response_model=EditorSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建编辑器会话"""
    try:
        session = EditorService.create_session(db, current_user.id, request)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@router.get("/sessions", response_model=List[EditorSessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的编辑器会话列表"""
    sessions = EditorService.get_user_sessions(db, current_user.id, skip, limit)
    return sessions

@router.get("/sessions/{session_id}", response_model=EditorSessionDetailResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取编辑器会话详情"""
    session = EditorService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session

@router.put("/sessions/{session_id}", response_model=EditorSessionResponse)
async def update_session(
    session_id: int,
    request: UpdateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新编辑器会话"""
    session = EditorService.update_session(db, session_id, current_user.id, request)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除编辑器会话"""
    success = EditorService.delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"success": True, "message": "会话删除成功"}

@router.post("/sessions/{session_id}/optimize", response_model=OptimizeResponse)
async def optimize_content(
    session_id: int,
    request: OptimizeContentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI优化内容"""
    try:
        result = EditorService.optimize_content(db, session_id, current_user.id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")

@router.post("/sessions/{session_id}/apply-optimization/{optimization_id}")
async def apply_optimization(
    session_id: int,
    optimization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """应用AI优化结果"""
    success = EditorService.apply_optimization(db, session_id, optimization_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="应用优化失败，请检查会话和优化记录是否存在")
    return {"success": True, "message": "优化结果已应用"}

@router.post("/sessions/{session_id}/save-document")
async def save_as_document(
    session_id: int,
    request: SaveDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将编辑器会话保存为正式文档"""
    try:
        document = EditorService.save_as_document(
            db, session_id, current_user.id, 
            request.title, request.folder_id, request.summary
        )
        if not document:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "success": True,
            "message": "文档保存成功",
            "document_id": document.id,
            "document_title": document.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文档失败: {str(e)}")

@router.get("/sessions/{session_id}/optimizations", response_model=List[AIOptimizationResponse])
async def get_session_optimizations(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话的AI优化历史"""
    # 验证会话权限
    session = EditorService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return session.ai_optimizations

@router.get("/stats", response_model=EditorStatsResponse)
async def get_editor_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取编辑器统计信息"""
    stats = EditorService.get_editor_stats(db, current_user.id)
    return stats

@router.get("/config")
async def get_editor_config(
    current_user: User = Depends(get_current_user)
):
    """获取编辑器配置"""
    return {
        "optimization_types": [
            {"value": "general", "label": "通用优化", "description": "提升表达质量和可读性"},
            {"value": "grammar", "label": "语法检查", "description": "修正语法和拼写错误"},
            {"value": "structure", "label": "结构优化", "description": "优化文档结构和层次"},
            {"value": "expand", "label": "内容扩展", "description": "适当扩展和完善内容"}
        ],
        "editor_features": {
            "auto_save": True,
            "syntax_highlight": True,
            "live_preview": True,
            "ai_optimization": True
        },
        "limits": {
            "max_content_length": 50000,  # 最大内容长度
            "max_title_length": 200,      # 最大标题长度
            "max_sessions_per_user": 100  # 每用户最大会话数
        }
    }