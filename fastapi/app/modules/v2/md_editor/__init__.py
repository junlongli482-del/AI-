# app/modules/v2/md_editor/__init__.py
"""
MD编辑器模块

功能：
- MD文档编辑
- AI内容优化
- 实时草稿保存
- 编辑历史管理
"""

from .routes import router
from .models import EditorSession, AIOptimization
from .services import EditorService

__all__ = ["router", "EditorSession", "AIOptimization", "EditorService"]