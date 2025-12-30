"""
Caching utilities for metadata extraction
"""
import json
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class CacheManager:
    """
    File-based cache manager for metadata operations.
    Useful for expensive operations like geocoding.
    """
    
    def __init__(self, cache_dir: str = "/tmp/metaextract_cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = timedelta(hours=24)  # Default cache TTL: 24 hours
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str, ttl: Optional[timedelta] = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            ttl: Time-to-live (uses default if None)
        
        Returns:
            Cached value if exists and not expired, else None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            cached_at = datetime.fromisoformat(data['cached_at'])
            effective_ttl = ttl if ttl else self.default_ttl
            
            if datetime.now() - cached_at > effective_ttl:
                # Cache expired
                cache_path.unlink()
                return None
            
            return data['value']
        except Exception as e:
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        
        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'key': key,
                'value': value
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            return True
        except Exception as e:
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
        
        Returns:
            True if entry existed and was deleted
        """
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False
    
    def clear_all(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1
        return count
