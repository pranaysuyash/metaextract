#!/usr/bin/env python3
"""
Advanced Metadata Caching System

Provides intelligent caching for metadata extraction results with:
- Multi-tier storage (memory, disk, database, Redis)
- Content-based cache keys (file hashes)
- Automatic cache invalidation
- Compression and serialization
- Performance analytics
- Cache warming and preloading
- Intelligent cache eviction policies

Author: MetaExtract Team
Version: 3.0.0 - Ultimate Edition
"""

import os
import json
import hashlib
import pickle
import gzip
import sqlite3
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from threading import Lock, Thread
import tempfile
import threading
from collections import OrderedDict
import weakref

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
        decode_responses=False,  # Keep binary for compression
        socket_timeout=5,
        socket_connect_timeout=5
    )
    
    # Test connection
    try:
        redis_client.ping()
        logger.info("Redis cache connected successfully")
    except:
        REDIS_AVAILABLE = False
        logger.warning("Redis connection failed, using local cache only")
        
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available, using local cache only")

@dataclass
class CacheEntry:
    """Represents a cached metadata entry"""
    file_path: str
    file_hash: str
    file_size: int
    file_mtime: float
    metadata: Dict[str, Any]
    extraction_tier: str
    extraction_time_ms: int
    cached_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    compression_ratio: float = 1.0
    cache_level: str = "memory"  # memory, disk, database, redis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['cached_at'] = self.cached_at.isoformat()
        result['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        data['cached_at'] = datetime.fromisoformat(data['cached_at'])
        if data['last_accessed']:
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

class LRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = OrderedDict()
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                entry = self._cache.pop(key)
                self._cache[key] = entry
                return entry
            return None
    
    def put(self, key: str, entry: CacheEntry):
        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # Remove least recently used
                self._cache.popitem(last=False)
            
            self._cache[key] = entry
    
    def remove(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> List[str]:
        with self._lock:
            return list(self._cache.keys())

class AdvancedMetadataCache:
    """Advanced multi-tier metadata caching system"""
    
    def __init__(self, 
                 cache_dir: Optional[str] = None,
                 max_memory_entries: int = 1000,
                 max_disk_size_mb: int = 500,
                 enable_compression: bool = True,
                 enable_database: bool = True,
                 enable_redis: bool = True,
                 cache_ttl_hours: int = 24,
                 enable_background_cleanup: bool = True):
        
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.metaextract' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_memory_entries = max_memory_entries
        self.max_disk_size_mb = max_disk_size_mb
        self.enable_compression = enable_compression
        self.enable_database = enable_database
        self.enable_redis = enable_redis and REDIS_AVAILABLE
        self.cache_ttl_hours = cache_ttl_hours
        self.enable_background_cleanup = enable_background_cleanup
        
        # Multi-tier cache storage
        self._memory_cache = LRUCache(max_memory_entries)
        self._cache_lock = Lock()
        
        # Database connection
        self._db_path = self.cache_dir / 'metadata_cache.db'
        self._init_database()
        
        # Performance tracking
        self._stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'db_hits': 0,
            'redis_hits': 0,
            'evictions': 0,
            'total_requests': 0,
            'compression_savings_bytes': 0,
            'cache_writes': 0,
            'cache_invalidations': 0
        }
        
        # Background cleanup thread
        self._cleanup_thread = None
        self._shutdown_event = threading.Event()
        
        if self.enable_background_cleanup:
            self._start_background_cleanup()
        
        logger.info(f"Initialized AdvancedMetadataCache at {self.cache_dir}")
        logger.info(f"Cache tiers: Memory={max_memory_entries}, Disk={max_disk_size_mb}MB, "
                   f"DB={enable_database}, Redis={self.enable_redis}")
    
    def _init_database(self):
        """Initialize SQLite database for persistent caching"""
        if not self.enable_database:
            return
        
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        cache_key TEXT PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        file_hash TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        file_mtime REAL NOT NULL,
                        extraction_tier TEXT NOT NULL,
                        extraction_time_ms INTEGER NOT NULL,
                        cached_at TEXT NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT,
                        compression_ratio REAL DEFAULT 1.0,
                        metadata_compressed BLOB,
                        cache_level TEXT DEFAULT 'database'
                    )
                ''')
                
                # Create indexes for performance
                indexes = [
                    'CREATE INDEX IF NOT EXISTS idx_file_hash ON cache_entries(file_hash)',
                    'CREATE INDEX IF NOT EXISTS idx_cached_at ON cache_entries(cached_at)',
                    'CREATE INDEX IF NOT EXISTS idx_access_count ON cache_entries(access_count DESC)',
                    'CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)',
                    'CREATE INDEX IF NOT EXISTS idx_tier ON cache_entries(extraction_tier)'
                ]
                
                for index_sql in indexes:
                    conn.execute(index_sql)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            self.enable_database = False
    
    def _start_background_cleanup(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while not self._shutdown_event.wait(300):  # Run every 5 minutes
                try:
                    self._cleanup_expired_entries()
                    self._cleanup_disk_cache()
                    self._optimize_database()
                except Exception as e:
                    logger.error(f"Background cleanup error: {e}")
        
        self._cleanup_thread = Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.debug("Started background cleanup thread")
    
    def _generate_cache_key(self, file_path: str, tier: str = "premium") -> str:
        """Generate cache key based on file content and extraction parameters"""
        try:
            # Use file hash + tier as cache key
            file_hash = self._calculate_file_hash(file_path)
            cache_key = f"meta_{file_hash}_{tier}"
            return cache_key
        except Exception as e:
            logger.error(f"Failed to generate cache key for {file_path}: {e}")
            # Fallback to path-based key
            path_hash = hashlib.md5(f"{file_path}_{tier}".encode()).hexdigest()
            return f"fallback_{path_hash}"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate optimized hash of file content"""
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            
            # For small files (< 1MB), hash entire content
            if file_size < 1024 * 1024:
                with open(file_path, "rb") as f:
                    content = f.read()
                    return hashlib.sha256(content).hexdigest()
            
            # For large files, use optimized hashing
            hasher = hashlib.sha256()
            hasher.update(str(file_size).encode())
            hasher.update(str(stat_info.st_mtime).encode())
            
            with open(file_path, "rb") as f:
                # First 4KB
                first_chunk = f.read(4096)
                hasher.update(first_chunk)
                
                # Middle chunk
                if file_size > 8192:
                    f.seek(file_size // 2)
                    middle_chunk = f.read(4096)
                    hasher.update(middle_chunk)
                
                # Last 4KB
                if file_size > 4096:
                    f.seek(-4096, 2)
                    last_chunk = f.read(4096)
                    hasher.update(last_chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            # Fallback to path + mtime + size
            fallback_data = f"{file_path}_{stat_info.st_mtime}_{stat_info.st_size}".encode()
            return hashlib.sha256(fallback_data).hexdigest()
    
    def _compress_metadata(self, metadata: Dict[str, Any]) -> Tuple[bytes, float]:
        """Compress metadata using gzip"""
        if not self.enable_compression:
            serialized = pickle.dumps(metadata)
            return serialized, 1.0
        
        try:
            serialized = pickle.dumps(metadata)
            compressed = gzip.compress(serialized, compresslevel=6)
            compression_ratio = len(compressed) / len(serialized)
            
            # Track compression savings
            savings = len(serialized) - len(compressed)
            self._stats['compression_savings_bytes'] += savings
            
            # Always return compressed data when compression is enabled
            return compressed, compression_ratio
        except Exception as e:
            logger.error(f"Failed to compress metadata: {e}")
            serialized = pickle.dumps(metadata)
            return serialized, 1.0
    
    def _decompress_metadata(self, compressed_data: bytes, compression_ratio: float) -> Dict[str, Any]:
        """Decompress metadata"""
        try:
            if compression_ratio == 1.0:  # Was not compressed
                return pickle.loads(compressed_data)
            else:  # Was compressed (regardless of ratio)
                decompressed = gzip.decompress(compressed_data)
                return pickle.loads(decompressed)
        except Exception as e:
            logger.error(f"Failed to decompress metadata: {e}")
            return {}
    
    def get(self, file_path: str, tier: str = "premium") -> Optional[Dict[str, Any]]:
        """Retrieve metadata from cache (multi-tier lookup)"""
        self._stats['total_requests'] += 1
        
        cache_key = self._generate_cache_key(file_path, tier)
        
        # Check if file still exists and hasn't changed
        if not os.path.exists(file_path):
            self._invalidate_key(cache_key)
            return None
        
        current_stat = os.stat(file_path)
        
        # 1. Check memory cache first (fastest)
        entry = self._memory_cache.get(cache_key)
        if entry and self._validate_entry(entry, current_stat):
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            entry.cache_level = "memory"
            
            self._stats['hits'] += 1
            self._stats['memory_hits'] += 1
            logger.debug(f"Memory cache hit for {file_path}")
            return entry.metadata.copy()
        
        # 2. Check Redis cache (fast, distributed)
        if self.enable_redis:
            entry = self._get_from_redis(cache_key, file_path, current_stat)
            if entry:
                # Promote to memory cache
                self._memory_cache.put(cache_key, entry)
                self._stats['hits'] += 1
                self._stats['redis_hits'] += 1
                logger.debug(f"Redis cache hit for {file_path}")
                return entry.metadata.copy()
        
        # 3. Check disk cache
        entry = self._get_from_disk(cache_key, file_path, current_stat)
        if entry:
            # Promote to memory and Redis cache
            self._memory_cache.put(cache_key, entry)
            if self.enable_redis:
                self._save_to_redis(cache_key, entry)
            
            self._stats['hits'] += 1
            self._stats['disk_hits'] += 1
            logger.debug(f"Disk cache hit for {file_path}")
            return entry.metadata.copy()
        
        # 4. Check database cache (slowest but most persistent)
        if self.enable_database:
            entry = self._get_from_database(cache_key, file_path, current_stat)
            if entry:
                # Promote to all upper cache levels
                self._memory_cache.put(cache_key, entry)
                if self.enable_redis:
                    self._save_to_redis(cache_key, entry)
                self._save_to_disk(cache_key, entry)
                
                self._stats['hits'] += 1
                self._stats['db_hits'] += 1
                logger.debug(f"Database cache hit for {file_path}")
                return entry.metadata.copy()
        
        # Cache miss
        self._stats['misses'] += 1
        logger.debug(f"Cache miss for {file_path}")
        return None
    
    def _validate_entry(self, entry: CacheEntry, current_stat) -> bool:
        """Validate that cache entry is still current"""
        return (entry.file_size == current_stat.st_size and 
                abs(entry.file_mtime - current_stat.st_mtime) < 1.0)
    
    def put(self, file_path: str, metadata: Dict[str, Any], tier: str = "premium", 
            extraction_time_ms: int = 0) -> bool:
        """Store metadata in all cache tiers"""
        try:
            cache_key = self._generate_cache_key(file_path, tier)
            
            if not os.path.exists(file_path):
                logger.warning(f"Cannot cache metadata for non-existent file: {file_path}")
                return False
            
            stat = os.stat(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            # Create cache entry
            entry = CacheEntry(
                file_path=file_path,
                file_hash=file_hash,
                file_size=stat.st_size,
                file_mtime=stat.st_mtime,
                metadata=metadata,
                extraction_tier=tier,
                extraction_time_ms=extraction_time_ms,
                cached_at=datetime.now(),
                cache_level="all"
            )
            
            # Store in all available cache tiers
            success = True
            
            # Memory cache (always available)
            self._memory_cache.put(cache_key, entry)
            
            # Redis cache
            if self.enable_redis:
                success &= self._save_to_redis(cache_key, entry)
            
            # Disk cache
            success &= self._save_to_disk(cache_key, entry)
            
            # Database cache
            if self.enable_database:
                success &= self._save_to_database(cache_key, entry)
            
            if success:
                self._stats['cache_writes'] += 1
                logger.debug(f"Cached metadata for {file_path} (key: {cache_key[:16]}...)")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cache metadata for {file_path}: {e}")
            return False

    def _save_to_redis(self, cache_key: str, entry: CacheEntry) -> bool:
        """Save entry to Redis cache"""
        if not self.enable_redis:
            return True
        
        try:
            compressed_metadata, compression_ratio = self._compress_metadata(entry.metadata)
            entry.compression_ratio = compression_ratio
            
            # Create Redis-compatible entry
            redis_entry = entry.to_dict()
            redis_entry['metadata_compressed'] = compressed_metadata
            del redis_entry['metadata']  # Remove uncompressed metadata
            
            # Serialize entry
            serialized_entry = pickle.dumps(redis_entry)
            
            # Store with TTL
            ttl_seconds = self.cache_ttl_hours * 3600
            redis_client.setex(cache_key, ttl_seconds, serialized_entry)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cache entry to Redis: {e}")
            return False
    
    def _get_from_redis(self, cache_key: str, file_path: str, current_stat) -> Optional[CacheEntry]:
        """Retrieve entry from Redis cache"""
        if not self.enable_redis:
            return None
        
        try:
            serialized_entry = redis_client.get(cache_key)
            if not serialized_entry:
                return None
            
            redis_entry = pickle.loads(serialized_entry)
            
            # Validate entry is still current
            if (redis_entry['file_size'] != current_stat.st_size or 
                abs(redis_entry['file_mtime'] - current_stat.st_mtime) >= 1.0):
                # Entry is stale, remove it
                redis_client.delete(cache_key)
                return None
            
            # Create entry object
            entry = CacheEntry.from_dict(redis_entry)
            
            # Decompress metadata
            compressed_metadata = redis_entry['metadata_compressed']
            entry.metadata = self._decompress_metadata(compressed_metadata, entry.compression_ratio)
            
            # Update access tracking
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            entry.cache_level = "redis"
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to load cache entry from Redis: {e}")
            return None
    
    def _save_to_disk(self, cache_key: str, entry: CacheEntry) -> bool:
        """Save entry to disk cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            # Compress metadata
            compressed_metadata, compression_ratio = self._compress_metadata(entry.metadata)
            entry.compression_ratio = compression_ratio
            
            # Save entry info and compressed metadata
            cache_data = {
                'entry': entry.to_dict(),
                'metadata_compressed': compressed_metadata
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cache entry to disk: {e}")
            return False
    
    def _get_from_disk(self, cache_key: str, file_path: str, current_stat) -> Optional[CacheEntry]:
        """Retrieve entry from disk cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            if not cache_file.exists():
                return None
            
            # Check if cache file is too old
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age > timedelta(hours=self.cache_ttl_hours):
                cache_file.unlink(missing_ok=True)
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            entry_dict = cache_data['entry']
            entry = CacheEntry.from_dict(entry_dict)
            
            # Validate entry is still current
            if (entry.file_size != current_stat.st_size or 
                abs(entry.file_mtime - current_stat.st_mtime) >= 1.0):
                # Entry is stale, remove it
                cache_file.unlink(missing_ok=True)
                return None
            
            # Decompress metadata
            compressed_metadata = cache_data['metadata_compressed']
            entry.metadata = self._decompress_metadata(compressed_metadata, entry.compression_ratio)
            
            # Update access tracking
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            entry.cache_level = "disk"
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to load cache entry from disk: {e}")
            return None
    
    def _save_to_database(self, cache_key: str, entry: CacheEntry) -> bool:
        """Save entry to database cache"""
        if not self.enable_database:
            return True
        
        try:
            compressed_metadata, compression_ratio = self._compress_metadata(entry.metadata)
            entry.compression_ratio = compression_ratio
            
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (cache_key, file_path, file_hash, file_size, file_mtime, 
                     extraction_tier, extraction_time_ms, cached_at, access_count, 
                     last_accessed, compression_ratio, metadata_compressed, cache_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cache_key, entry.file_path, entry.file_hash, entry.file_size,
                    entry.file_mtime, entry.extraction_tier, entry.extraction_time_ms,
                    entry.cached_at.isoformat(), entry.access_count,
                    entry.last_accessed.isoformat() if entry.last_accessed else None,
                    entry.compression_ratio, compressed_metadata, entry.cache_level
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cache entry to database: {e}")
            return False
    
    def _get_from_database(self, cache_key: str, file_path: str, current_stat) -> Optional[CacheEntry]:
        """Retrieve entry from database cache"""
        if not self.enable_database:
            return None
        
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                cursor = conn.execute('''
                    SELECT file_path, file_hash, file_size, file_mtime, extraction_tier,
                           extraction_time_ms, cached_at, access_count, last_accessed,
                           compression_ratio, metadata_compressed, cache_level
                    FROM cache_entries WHERE cache_key = ?
                ''', (cache_key,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                (db_file_path, file_hash, file_size, file_mtime, extraction_tier,
                 extraction_time_ms, cached_at, access_count, last_accessed,
                 compression_ratio, metadata_compressed, cache_level) = row
                
                # Check if entry is too old
                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time > timedelta(hours=self.cache_ttl_hours):
                    conn.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
                    conn.commit()
                    return None
                
                # Validate entry is still current
                if (file_size != current_stat.st_size or 
                    abs(file_mtime - current_stat.st_mtime) >= 1.0):
                    # Entry is stale, remove it
                    conn.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
                    conn.commit()
                    return None
                
                # Create entry
                entry = CacheEntry(
                    file_path=db_file_path,
                    file_hash=file_hash,
                    file_size=file_size,
                    file_mtime=file_mtime,
                    metadata={},  # Will be filled below
                    extraction_tier=extraction_tier,
                    extraction_time_ms=extraction_time_ms,
                    cached_at=cached_time,
                    access_count=access_count,
                    last_accessed=datetime.fromisoformat(last_accessed) if last_accessed else None,
                    compression_ratio=compression_ratio,
                    cache_level=cache_level or "database"
                )
                
                # Decompress metadata
                entry.metadata = self._decompress_metadata(metadata_compressed, compression_ratio)
                
                # Update access tracking
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Update database with new access info
                conn.execute('''
                    UPDATE cache_entries 
                    SET access_count = ?, last_accessed = ?
                    WHERE cache_key = ?
                ''', (entry.access_count, entry.last_accessed.isoformat(), cache_key))
                conn.commit()
                
                return entry
                
        except Exception as e:
            logger.error(f"Failed to load cache entry from database: {e}")
            return None
    
    def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        cutoff_time = datetime.now() - timedelta(hours=self.cache_ttl_hours)
        
        # Clean up disk cache
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_time:
                    cache_file.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error cleaning disk cache: {e}")
        
        # Clean up database
        if self.enable_database:
            try:
                with sqlite3.connect(str(self._db_path)) as conn:
                    cursor = conn.execute('''
                        DELETE FROM cache_entries 
                        WHERE cached_at < ?
                    ''', (cutoff_time.isoformat(),))
                    deleted = cursor.rowcount
                    conn.commit()
                    
                    if deleted > 0:
                        logger.debug(f"Cleaned up {deleted} expired database entries")
            except Exception as e:
                logger.error(f"Error cleaning database cache: {e}")
    
    def _cleanup_disk_cache(self):
        """Clean up disk cache if it exceeds size limit"""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in cache_files)
            max_size_bytes = self.max_disk_size_mb * 1024 * 1024
            
            if total_size <= max_size_bytes:
                return
            
            # Sort by access time (oldest first)
            cache_files.sort(key=lambda f: f.stat().st_atime)
            
            # Remove oldest files until under limit
            removed_count = 0
            for cache_file in cache_files:
                file_size = cache_file.stat().st_size
                cache_file.unlink(missing_ok=True)
                total_size -= file_size
                removed_count += 1
                
                if total_size <= max_size_bytes * 0.8:  # Leave some headroom
                    break
            
            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} disk cache files")
                self._stats['evictions'] += removed_count
                    
        except Exception as e:
            logger.error(f"Failed to cleanup disk cache: {e}")
    
    def _optimize_database(self):
        """Optimize database performance"""
        if not self.enable_database:
            return
        
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                # Vacuum database to reclaim space
                conn.execute('VACUUM')
                
                # Analyze tables for query optimization
                conn.execute('ANALYZE')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
    
    def _invalidate_key(self, cache_key: str):
        """Remove cache entry by key from all cache levels"""
        # Remove from memory
        self._memory_cache.remove(cache_key)
        
        # Remove from Redis
        if self.enable_redis:
            try:
                redis_client.delete(cache_key)
            except Exception as e:
                logger.error(f"Failed to remove Redis cache entry: {e}")
        
        # Remove from disk
        cache_file = self.cache_dir / f"{cache_key}.cache"
        cache_file.unlink(missing_ok=True)
        
        # Remove from database
        if self.enable_database:
            try:
                with sqlite3.connect(str(self._db_path)) as conn:
                    conn.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to remove database cache entry: {e}")
        
        self._stats['cache_invalidations'] += 1
    
    def invalidate_file(self, file_path: str, tier: str = None):
        """Invalidate cache entries for a specific file"""
        if tier:
            cache_key = self._generate_cache_key(file_path, tier)
            self._invalidate_key(cache_key)
        else:
            # Invalidate all tiers for this file
            for tier_name in ["free", "starter", "premium", "super"]:
                cache_key = self._generate_cache_key(file_path, tier_name)
                self._invalidate_key(cache_key)
    
    def warm_cache(self, file_paths: List[str], tier: str = "premium", 
                   max_workers: int = 4) -> Dict[str, bool]:
        """Pre-warm cache with metadata for multiple files"""
        from concurrent.futures import ThreadPoolExecutor
        
        results = {}
        
        def warm_single_file(file_path: str) -> Tuple[str, bool]:
            try:
                # Check if already cached
                if self.get(file_path, tier) is not None:
                    return file_path, True
                
                # Extract and cache metadata
                # This would typically call the main extraction function
                # For now, we'll just mark as attempted
                return file_path, False
                
            except Exception as e:
                logger.error(f"Failed to warm cache for {file_path}: {e}")
                return file_path, False
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for file_path, success in executor.map(warm_single_file, file_paths):
                results[file_path] = success
        
        return results
    
    def clear_all(self):
        """Clear all cache data"""
        # Clear memory
        self._memory_cache.clear()
        
        # Clear Redis
        if self.enable_redis:
            try:
                # Delete all keys matching our pattern
                keys = redis_client.keys("meta_*")
                if keys:
                    redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")
        
        # Clear disk
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink(missing_ok=True)
        
        # Clear database
        if self.enable_database:
            try:
                with sqlite3.connect(str(self._db_path)) as conn:
                    conn.execute('DELETE FROM cache_entries')
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to clear database cache: {e}")
        
        # Reset stats
        self._stats = {key: 0 for key in self._stats}
        
        logger.info("Cleared all cache data")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._stats['total_requests']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': self._memory_cache.size(),
            'cache_dir': str(self.cache_dir),
            'disk_cache_files': len(list(self.cache_dir.glob("*.cache"))),
            'database_enabled': self.enable_database,
            'redis_enabled': self.enable_redis,
            'compression_enabled': self.enable_compression,
            'ttl_hours': self.cache_ttl_hours
        }
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        stats = self.get_stats()
        
        # Memory cache info
        memory_info = {
            'entries': self._memory_cache.size(),
            'max_entries': self.max_memory_entries,
            'usage_percent': (self._memory_cache.size() / self.max_memory_entries * 100) if self.max_memory_entries > 0 else 0
        }
        
        # Disk cache info
        cache_files = list(self.cache_dir.glob("*.cache"))
        disk_size_mb = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
        disk_info = {
            'files': len(cache_files),
            'size_mb': round(disk_size_mb, 2),
            'max_size_mb': self.max_disk_size_mb,
            'usage_percent': (disk_size_mb / self.max_disk_size_mb * 100) if self.max_disk_size_mb > 0 else 0
        }
        
        # Redis info
        redis_info = {'enabled': self.enable_redis}
        if self.enable_redis:
            try:
                info = redis_client.info()
                redis_info.update({
                    'connected': True,
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                })
            except Exception as e:
                redis_info.update({'connected': False, 'error': str(e)})
        
        # Database info
        db_info = {'enabled': self.enable_database}
        if self.enable_database:
            try:
                with sqlite3.connect(str(self._db_path)) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                    db_entries = cursor.fetchone()[0]
                    db_info['entries'] = db_entries
                    
                    # Database file size
                    if self._db_path.exists():
                        db_info['size_mb'] = round(self._db_path.stat().st_size / (1024 * 1024), 2)
            except Exception as e:
                db_info['error'] = str(e)
        
        return {
            'statistics': stats,
            'memory_cache': memory_info,
            'disk_cache': disk_info,
            'redis_cache': redis_info,
            'database_cache': db_info,
            'configuration': {
                'compression_enabled': self.enable_compression,
                'cache_directory': str(self.cache_dir),
                'ttl_hours': self.cache_ttl_hours,
                'background_cleanup': self.enable_background_cleanup
            }
        }
    
    def shutdown(self):
        """Shutdown cache system gracefully"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._shutdown_event.set()
            self._cleanup_thread.join(timeout=5)
        
        logger.info("Cache system shutdown complete")

# ============================================================================
# Legacy API Compatibility
# ============================================================================

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

# ============================================================================
# Legacy API Compatibility
# ============================================================================

def get_file_hash_quick(filepath: str) -> str:
    """
    Generate a quick hash for file identification.
    Uses file size + first/last 1KB for speed on large files.
    """
    cache = get_cache()
    return cache._calculate_file_hash(filepath)

def get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get metadata from cache if available (legacy API)."""
    # This is a simplified version for backward compatibility
    # In practice, you'd need to extract file_path and tier from cache_key
    logger.warning("Using legacy cache API - consider upgrading to AdvancedMetadataCache")
    return None

def set_cache(cache_key: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
    """Store metadata in cache (legacy API)."""
    logger.warning("Using legacy cache API - consider upgrading to AdvancedMetadataCache")
    return False

def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern (legacy API)."""
    logger.warning("Using legacy cache API - consider upgrading to AdvancedMetadataCache")
    return 0

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics (legacy API)."""
    cache = get_cache()
    return cache.get_stats()

# ============================================================================
# Global Cache Instance
# ============================================================================

# Global cache instance
_global_cache: Optional[AdvancedMetadataCache] = None

def get_cache() -> AdvancedMetadataCache:
    """Get or create the global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = AdvancedMetadataCache()
    return _global_cache

def clear_cache():
    """Clear the global cache"""
    cache = get_cache()
    cache.clear_all()

def get_cache_info() -> Dict[str, Any]:
    """Get detailed global cache information"""
    cache = get_cache()
    return cache.get_detailed_info()

def shutdown_cache():
    """Shutdown the global cache system"""
    global _global_cache
    if _global_cache:
        _global_cache.shutdown()
        _global_cache = None