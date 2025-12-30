#!/usr/bin/env python3
"""
Caching utilities for MetaExtract performance optimization.
"""

import os
import json
import hashlib
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("metaextract.cache")

# Redis connection (optional)
try:
    import redis
    REDIS_AVAILABLE = True
    
    # Initialize Redis connection
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )
    
    # Test connection
    try:
        redis_client.ping()
        logger.info("Redis cache connected successfully")
    except:
        REDIS_AVAILABLE = False
        logger.warning("Redis connection failed, caching disabled")
        
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available, caching disabled")

def get_file_hash_quick(filepath: str) -> str:
    """
    Generate a quick hash for file identification.
    Uses file size + first/last 1KB for speed on large files.
    """
    try:
        stat_info = os.stat(filepath)
        file_size = stat_info.st_size
        
        # For small files, hash the entire content
        if file_size < 1024 * 1024:  # 1MB
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        
        # For large files, hash size + first/last 1KB
        hasher = hashlib.md5()
        hasher.update(str(file_size).encode())
        hasher.update(str(stat_info.st_mtime).encode())
        
        with open(filepath, 'rb') as f:
            # First 1KB
            first_chunk = f.read(1024)
            hasher.update(first_chunk)
            
            # Last 1KB
            if file_size > 1024:
                f.seek(-1024, 2)
                last_chunk = f.read(1024)
                hasher.update(last_chunk)
        
        return hasher.hexdigest()
        
    except Exception as e:
        logger.warning(f"Error generating file hash: {e}")
        return hashlib.md5(filepath.encode()).hexdigest()

def get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get metadata from cache if available."""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            result = json.loads(cached_data)
            logger.debug(f"Cache hit: {cache_key}")
            return result
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
    
    return None

def set_cache(cache_key: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
    """Store metadata in cache."""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        # Add cache metadata
        data["cache_info"] = {
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours
        }
        
        json_data = json.dumps(data, default=str)
        ttl_seconds = ttl_hours * 3600
        
        redis_client.setex(cache_key, ttl_seconds, json_data)
        logger.debug(f"Cache set: {cache_key} (TTL: {ttl_hours}h)")
        return True
        
    except Exception as e:
        logger.warning(f"Cache write error: {e}")
        return False

def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern."""
    if not REDIS_AVAILABLE:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Cleared {deleted} cache entries matching: {pattern}")
            return deleted
    except Exception as e:
        logger.warning(f"Cache clear error: {e}")
    
    return 0

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    if not REDIS_AVAILABLE:
        return {"available": False}
    
    try:
        info = redis_client.info()
        return {
            "available": True,
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
        }
    except Exception as e:
        logger.warning(f"Cache stats error: {e}")
        return {"available": False, "error": str(e)}