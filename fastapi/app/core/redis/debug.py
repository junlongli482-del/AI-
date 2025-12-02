"""
Redis缓存调试工具
功能：提供完善的调试信息和性能监控
"""
import time
import json
from typing import Any, Dict, Optional, Callable
from functools import wraps
from datetime import datetime


class CacheDebugger:
    """缓存调试器"""

    def __init__(self, module_name: str = "Unknown"):
        self.module_name = module_name
        self.debug_enabled = True  # 开发阶段始终开启

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """统一日志输出"""
        icons = {
            'TRACE': '🔍',
            'INFO': 'ℹ️',
            'WARN': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅',
            'CACHE': '💾',
            'DB': '🗄️',
            'PERF': '⚡'
        }

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        icon = icons.get(level, '📝')

        print(f"{icon} [{timestamp}] [{self.module_name}] {message}")

        if data and self.debug_enabled:
            print(f"   📋 数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    def trace(self, message: str, data: Optional[Dict] = None):
        """详细执行路径"""
        self.log('TRACE', message, data)

    def info(self, message: str, data: Optional[Dict] = None):
        """关键信息"""
        self.log('INFO', message, data)

    def success(self, message: str, data: Optional[Dict] = None):
        """成功信息"""
        self.log('SUCCESS', message, data)

    def warn(self, message: str, data: Optional[Dict] = None):
        """警告信息"""
        self.log('WARN', message, data)

    def error(self, message: str, data: Optional[Dict] = None):
        """错误信息"""
        self.log('ERROR', message, data)

    def cache_hit(self, key: str, data_size: int = 0):
        """缓存命中"""
        self.log('CACHE', f"缓存命中: {key}", {
            "key": key,
            "data_size": data_size,
            "hit": True
        })

    def cache_miss(self, key: str):
        """缓存未命中"""
        self.log('CACHE', f"缓存未命中: {key}", {
            "key": key,
            "hit": False
        })

    def cache_set(self, key: str, ttl: int, data_size: int = 0):
        """缓存写入"""
        self.log('CACHE', f"缓存写入: {key} (TTL: {ttl}s)", {
            "key": key,
            "ttl": ttl,
            "data_size": data_size
        })

    def db_query(self, query_type: str, duration_ms: float, result_count: int = 0):
        """数据库查询"""
        self.log('DB', f"数据库查询: {query_type} ({duration_ms:.2f}ms)", {
            "query_type": query_type,
            "duration_ms": duration_ms,
            "result_count": result_count
        })

    def performance(self, operation: str, duration_ms: float, improvement: Optional[str] = None):
        """性能信息"""
        msg = f"性能: {operation} ({duration_ms:.2f}ms)"
        if improvement:
            msg += f" - {improvement}"

        self.log('PERF', msg, {
            "operation": operation,
            "duration_ms": duration_ms,
            "improvement": improvement
        })


def cache_performance_monitor(operation_name: str):
    """性能监控装饰器"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            debugger = CacheDebugger("PerformanceMonitor")
            start_time = time.time()

            try:
                debugger.trace(f"开始执行: {operation_name}")
                result = await func(*args, **kwargs)

                duration_ms = (time.time() - start_time) * 1000
                debugger.performance(operation_name, duration_ms, "执行成功")

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                debugger.error(f"执行失败: {operation_name} ({duration_ms:.2f}ms)", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise

        return wrapper

    return decorator


# 全局调试器实例
stats_debugger = CacheDebugger("StatsCache")