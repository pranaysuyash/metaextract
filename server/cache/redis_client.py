"""
Redis Client Configuration for MetaExtract Caching

Provides centralized Redis connection management and utilities.
"""

import os
import json
import logging
from typing import Any, Optional, Dict, Union
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger("metaextract.cache.redis")


class RedisClient:
    """Centralized Redis client with connection pooling and error handling."""
    
    def __init__(self):
        self._client = None
        self._connected = False
        self._connect()
    
    def _connect(self):
        """Initialize Redis connection with fallback options."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not available")
            return
        
        try:
            # Get Redis configuration from environment
            host = os.getenv('REDIS_HOST', 'localhost')
            port = int(os.getenv('REDIS_PORT', 6379))
            db = int(os.getenv('REDIS_DB', 0))
            password = os.getenv('REDIS_PASSWORD', None)
            
            # Create Redis client with connection pooling
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,  # Return strings instead of bytes
                socket_timeout=5,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={},
                max_connections=50,
                retry_on_timeout=True,
                retry_on_error=[redis.ConnectionError, redis.TimeoutError],
                health_check_interval=30
            )
            
            # Test connection
            self._client.ping()
            self._connected = True
            logger.info(f"Redis connected successfully to {host}:{port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            self._client = None
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self._client is not None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.is_connected:
            return None
        
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Union[str, dict, list], 
            ex: Optional[Union[int, timedelta]] = None) -> bool:
        """Set value in Redis with optional expiration."""
        if not self.is_connected:
            return False
        
        try:
            # Serialize complex types to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, separators=(',', ':'))
            
            return self._client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.is_connected:
            return False
        
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.is_connected:
            return False
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def keys(self, pattern: str) -> list:
        """Get keys matching pattern."""
        if not self.is_connected:
            return []
        
        try:
            return list(self._client.keys(pattern))
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for key in seconds."""
        if not self.is_connected:
            return -2  # Key doesn't exist
        
        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2
    
    def set_ttl(self, key: str, seconds: int) -> bool:
        """Set TTL for key in seconds."""
        if not self.is_connected:
            return False
        
        try:
            return bool(self._client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from Redis and deserialize."""
        value = self.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for key {key}: {e}")
            return None
    
    def set_json(self, key: str, value: Dict[str, Any], 
                 ex: Optional[Union[int, timedelta]] = None) -> bool:
        """Set JSON value in Redis with serialization."""
        return self.set(key, value, ex=ex)
    
    def pipeline(self):
        """Get Redis pipeline for batch operations."""
        if not self.is_connected:
            return None
        
        return self._client.pipeline()
    
    def info(self) -> Optional[Dict[str, Any]]:
        """Get Redis server information."""
        if not self.is_connected:
            return None
        
        try:
            return self._client.info()
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return None
    
    def flushdb(self) -> bool:
        """Flush current Redis database."""
        if not self.is_connected:
            return False
        
        try:
            return self._client.flushdb()
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    def close(self):
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None
                self._connected = False


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient()
    
    return _redis_client


def close_redis_client():
    """Close global Redis client."""
    global _redis_client
    
    if _redis_client:
        _redis_client.close()
        _redis_client = None