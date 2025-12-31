"""
MetaExtract Enhanced Caching System

This module provides an advanced caching system for metadata extraction results
to improve performance and reduce redundant processing.
"""

import hashlib
import json
import time
import threading
from typing import Any, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import os
import pickle
import tempfile
from dataclasses import dataclass
from enum import Enum


@dataclass
class CacheEntry:
    """Represents a cached metadata extraction result."""
    key: str
    data: Any
    timestamp: float
    access_count: int
    file_path: str
    file_size: int
    file_mtime: float
    tier: str
    ttl: float  # Time-to-live in seconds


class CacheEvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"   # Time To Live


class EnhancedCache:
    """Enhanced caching system with multiple eviction policies and performance optimizations."""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600, 
                 eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}  # For LRU
        self.access_counts: Dict[str, int] = {}   # For LFU
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0
        }
    
    def _generate_key(self, filepath: str, tier: str, options: Optional[Dict] = None) -> str:
        """Generate a unique cache key based on file path, tier, and options."""
        key_data = {
            'filepath': filepath,
            'tier': tier,
            'options': options or {}
        }
        # Include file modification time to detect changes
        try:
            mtime = os.path.getmtime(filepath)
            key_data['mtime'] = mtime
        except OSError:
            pass
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is expired."""
        if entry.ttl <= 0:
            return False  # No TTL means never expires
        return time.time() - entry.timestamp > entry.ttl
    
    def _check_file_integrity(self, entry: CacheEntry) -> bool:
        """Check if the cached file still matches the original."""
        try:
            if not os.path.exists(entry.file_path):
                return False
            
            current_size = os.path.getsize(entry.file_path)
            current_mtime = os.path.getmtime(entry.file_path)
            
            return (current_size == entry.file_size and 
                    abs(current_mtime - entry.file_mtime) < 0.1)  # Allow small time differences
        except OSError:
            return False
    
    def get(self, filepath: str, tier: str = "super", 
            options: Optional[Dict] = None) -> Optional[Any]:
        """Get a cached result if available and valid."""
        with self.lock:
            key = self._generate_key(filepath, tier, options)
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if entry is expired
            if self._is_expired(entry):
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                if key in self.access_counts:
                    del self.access_counts[key]
                self.stats['misses'] += 1
                return None
            
            # Check file integrity
            if not self._check_file_integrity(entry):
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                if key in self.access_counts:
                    del self.access_counts[key]
                self.stats['misses'] += 1
                return None
            
            # Update access statistics
            self.access_times[key] = time.time()
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
            entry.access_count += 1
            
            self.stats['hits'] += 1
            return entry.data
    
    def put(self, filepath: str, data: Any, tier: str = "super", 
            ttl: Optional[float] = None, options: Optional[Dict] = None) -> bool:
        """Put a result in the cache."""
        with self.lock:
            # Get file info
            try:
                file_size = os.path.getsize(filepath)
                file_mtime = os.path.getmtime(filepath)
            except OSError:
                return False  # Can't cache if we can't get file info
            
            key = self._generate_key(filepath, tier, options)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                timestamp=time.time(),
                access_count=1,
                file_path=filepath,
                file_size=file_size,
                file_mtime=file_mtime,
                tier=tier,
                ttl=ttl if ttl is not None else self.default_ttl
            )
            
            # Check if we need to evict items
            if len(self.cache) >= self.max_size:
                self._evict_items()
            
            # Add to cache
            self.cache[key] = entry
            self.access_times[key] = time.time()
            self.access_counts[key] = 1
            
            return True
    
    def _evict_items(self):
        """Evict items based on the current eviction policy."""
        if not self.cache:
            return
        
        if self.eviction_policy == CacheEvictionPolicy.LRU:
            self._evict_lru()
        elif self.eviction_policy == CacheEvictionPolicy.LFU:
            self._evict_lfu()
        else:  # TTL or default
            self._evict_expired()
    
    def _evict_lru(self):
        """Evict the least recently used item."""
        if not self.access_times:
            return
        
        # Find the key with the oldest access time
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove the entry
        if oldest_key in self.cache:
            del self.cache[oldest_key]
        if oldest_key in self.access_times:
            del self.access_times[oldest_key]
        if oldest_key in self.access_counts:
            del self.access_counts[oldest_key]
        
        self.stats['evictions'] += 1
    
    def _evict_lfu(self):
        """Evict the least frequently used item."""
        if not self.access_counts:
            return
        
        # Find the key with the lowest access count
        least_used_key = min(self.access_counts.keys(), key=lambda k: self.access_counts[k])
        
        # Remove the entry
        if least_used_key in self.cache:
            del self.cache[least_used_key]
        if least_used_key in self.access_times:
            del self.access_times[least_used_key]
        if least_used_key in self.access_counts:
            del self.access_counts[least_used_key]
        
        self.stats['evictions'] += 1
    
    def _evict_expired(self):
        """Evict expired items."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            if key in self.access_counts:
                del self.access_counts[key]
        
        self.stats['evictions'] += len(expired_keys)
        
        # If still at max size after expiring, evict one more based on policy
        if len(self.cache) >= self.max_size and self.cache:
            if self.eviction_policy == CacheEvictionPolicy.LRU:
                self._evict_lru()
            else:  # Default to LFU
                self._evict_lfu()
    
    def invalidate(self, filepath: str, tier: str = "super", 
                   options: Optional[Dict] = None) -> bool:
        """Invalidate a specific cache entry."""
        with self.lock:
            key = self._generate_key(filepath, tier, options)
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                if key in self.access_counts:
                    del self.access_counts[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.access_counts.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'hit_rate': hit_rate,
                'hit_rate_percent': hit_rate * 100
            }
    
    def cleanup_expired(self):
        """Manually cleanup expired entries."""
        with self.lock:
            self._evict_expired()


# Global cache instance
_cache = None
_cache_lock = threading.Lock()


def get_cache() -> EnhancedCache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        with _cache_lock:
            if _cache is None:
                _cache = EnhancedCache()
    return _cache


def cache_result(filepath: str, result: Any, tier: str = "super", 
                ttl: Optional[float] = None, options: Optional[Dict] = None) -> bool:
    """Convenience function to cache a result."""
    cache = get_cache()
    return cache.put(filepath, result, tier, ttl, options)


def get_cached_result(filepath: str, tier: str = "super", 
                     options: Optional[Dict] = None) -> Optional[Any]:
    """Convenience function to get a cached result."""
    cache = get_cache()
    return cache.get(filepath, tier, options)


def invalidate_cache(filepath: str, tier: str = "super", 
                    options: Optional[Dict] = None) -> bool:
    """Convenience function to invalidate a cache entry."""
    cache = get_cache()
    return cache.invalidate(filepath, tier, options)


def get_cache_stats() -> Dict[str, Any]:
    """Convenience function to get cache statistics."""
    cache = get_cache()
    return cache.get_stats()


def cleanup_cache():
    """Convenience function to cleanup expired entries."""
    cache = get_cache()
    cache.cleanup_expired()


# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the caching system
    cache = get_cache()
    
    # Simulate caching some metadata
    sample_metadata = {
        "file": {"name": "test.jpg", "size": 1024000},
        "exif": {"DateTime": "2023:01:01 12:00:00", "Make": "Canon"},
        "summary": {"width": 1920, "height": 1080}
    }
    
    # Cache the result
    filepath = "/tmp/test_image.jpg"
    success = cache.put(filepath, sample_metadata, "premium", ttl=1800)  # 30 minutes TTL
    print(f"Caching result: {success}")
    
    # Retrieve from cache
    cached_result = cache.get(filepath, "premium")
    print(f"Retrieved from cache: {cached_result is not None}")
    
    # Check stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Test with different options
    options = {"include_thumbnails": True, "max_resolution": 800}
    success2 = cache.put(filepath, sample_metadata, "premium", options=options)
    print(f"Caching with options: {success2}")
    
    cached_with_options = cache.get(filepath, "premium", options=options)
    print(f"Retrieved with options: {cached_with_options is not None}")
    
    # Test invalidation
    invalidated = cache.invalidate(filepath, "premium")
    print(f"Invalidated: {invalidated}")
    
    # Check stats again
    stats_after = cache.get_stats()
    print(f"Cache stats after invalidation: {stats_after}")