"""
Base Cache Implementation for MetaExtract

Provides common functionality for all cache implementations.
"""

import hashlib
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Union
from pathlib import Path
from datetime import timedelta

from .redis_client import get_redis_client

logger = logging.getLogger("metaextract.cache.base")


class BaseCache(ABC):
    """Abstract base class for all cache implementations."""
    
    def __init__(self, cache_prefix: str, default_ttl: int = 3600):
        """
        Initialize base cache.
        
        Args:
            cache_prefix: Prefix for all cache keys
            default_ttl: Default TTL in seconds
        """
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.redis_client = get_redis_client()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def _generate_cache_key(self, *components) -> str:
        """Generate cache key from components."""
        # Create a deterministic hash from components
        key_parts = []
        for component in components:
            if isinstance(component, (dict, list)):
                # Serialize complex objects consistently
                import json
                key_parts.append(json.dumps(component, sort_keys=True, separators=(',', ':')))
            else:
                key_parts.append(str(component))
        
        # Create hash of combined components
        combined = "|".join(key_parts)
        key_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        return f"{self.cache_prefix}:{key_hash}"
    
    def _calculate_file_hash(self, file_path: str, quick: bool = True) -> str:
        """
        Calculate hash of file content for cache invalidation.
        
        Args:
            file_path: Path to the file
            quick: Use quick hashing for large files
            
        Returns:
            File hash string
        """
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            
            if quick and file_size > 10 * 1024 * 1024:  # 10MB
                # Quick hash for large files
                hasher = hashlib.sha256()
                hasher.update(str(file_size).encode())
                hasher.update(str(stat_info.st_mtime).encode())
                
                # Read first and last 4KB
                with open(file_path, "rb") as f:
                    # First 4KB
                    first_chunk = f.read(4096)
                    hasher.update(first_chunk)
                    
                    # Last 4KB
                    if file_size > 8192:
                        f.seek(-4096, 2)
                        last_chunk = f.read(4096)
                        hasher.update(last_chunk)
                
                return hasher.hexdigest()
            else:
                # Full hash for small files
                hasher = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        hasher.update(chunk)
                return hasher.hexdigest()
                
        except Exception as e:
            logger.error(f"Failed to calculate file hash for {file_path}: {e}")
            # Fallback to path + size + mtime
            try:
                stat_info = os.stat(file_path)
                fallback_data = f"{file_path}_{stat_info.st_size}_{stat_info.st_mtime}"
                return hashlib.sha256(fallback_data.encode()).hexdigest()
            except Exception:
                # Final fallback
                return hashlib.sha256(file_path.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.redis_client.is_connected:
                return None
            
            value = self.redis_client.get_json(key)
            if value is not None:
                self._stats['hits'] += 1
                logger.debug(f"Cache hit for key: {key}")
            else:
                self._stats['misses'] += 1
                logger.debug(f"Cache miss for key: {key}")
            
            return value
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self._stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            if not self.redis_client.is_connected:
                return False
            
            ttl = ttl or self.default_ttl
            success = self.redis_client.set_json(key, value, ex=ttl)
            
            if success:
                self._stats['sets'] += 1
                logger.debug(f"Cache set for key: {key} (TTL: {ttl}s)")
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self._stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.redis_client.is_connected:
                return False
            
            success = self.redis_client.delete(key)
            if success:
                self._stats['deletes'] += 1
                logger.debug(f"Cache delete for key: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self._stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self.redis_client.is_connected:
                return False
            
            return self.redis_client.exists(key)
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            self._stats['errors'] += 1
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for key in seconds."""
        try:
            if not self.redis_client.is_connected:
                return -2
            
            return self.redis_client.get_ttl(key)
            
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            self._stats['errors'] += 1
            return -2
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            if not self.redis_client.is_connected:
                return 0
            
            keys = self.redis_client.keys(f"{self.cache_prefix}:{pattern}")
            count = 0
            
            for key in keys:
                if self.delete(key):
                    count += 1
            
            logger.info(f"Invalidated {count} keys matching pattern: {pattern}")
            return count
            
        except Exception as e:
            logger.error(f"Pattern invalidation error for pattern {pattern}: {e}")
            self._stats['errors'] += 1
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_prefix': self.cache_prefix,
            'default_ttl': self.default_ttl,
            'redis_connected': self.redis_client.is_connected,
            'stats': self._stats.copy(),
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def clear_all(self) -> bool:
        """Clear all cache entries for this prefix."""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                # Use pipeline for efficient deletion
                pipeline = self.redis_client.pipeline()
                if pipeline:
                    for key in keys:
                        pipeline.delete(key)
                    pipeline.execute()
                    
                    count = len(keys)
                    self._stats['deletes'] += count
                    logger.info(f"Cleared {count} cache entries for prefix: {self.cache_prefix}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Clear all error for prefix {self.cache_prefix}: {e}")
            self._stats['errors'] += 1
            return False
    
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key for specific use case."""
        pass
    
    @abstractmethod
    def get_cached_result(self, *args, **kwargs) -> Optional[Any]:
        """Get cached result if available."""
        pass
    
    @abstractmethod
    def cache_result(self, result: Any, *args, **kwargs) -> bool:
        """Cache result for future use."""
        pass