# app/modules/v2/tech_square/__init__.py
"""
技术广场模块 (Tech Square)

提供文档展示、搜索、分类和统计功能的核心模块。

主要功能：
- 已发布文档列表展示（分页、筛选、排序）
- 智能搜索功能
- 文档详情查看
- 分类统计
- 热门推荐
- 浏览量统计

API版本：v2
模块状态：开发中
"""

from .routes import router

__version__ = "1.0.0"
__author__ = "FastAPI Team"
__description__ = "技术广场 - 文档展示与搜索模块"