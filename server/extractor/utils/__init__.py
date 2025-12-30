"""
Utility modules for MetaExtract.
"""

from .cache import (
    get_file_hash_quick,
    get_from_cache,
    set_cache,
    clear_cache_pattern,
    get_cache_stats,
    REDIS_AVAILABLE
)

__all__ = [
    'get_file_hash_quick',
    'get_from_cache', 
    'set_cache',
    'clear_cache_pattern',
    'get_cache_stats',
    'REDIS_AVAILABLE'
]