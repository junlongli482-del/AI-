"""
Redis缓存服务模块
"""
from .stats_cache import stats_cache_service
from .tech_square_cache import tech_square_stats_cache_service
from .document_list_cache import document_list_cache_service
from .hot_data_cache import hot_data_cache_service
from .search_cache import search_cache_service  # 🆕 新增

__all__ = [
    "stats_cache_service",
    "tech_square_stats_cache_service",
    "document_list_cache_service",
    "hot_data_cache_service",
    "search_cache_service",  # 🆕 新增
]