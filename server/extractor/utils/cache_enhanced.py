#!/usr/bin/env python3
"""
Enhanced Metadata Cache with Memory Pressure Monitoring

Wraps the AdvancedMetadataCache with adaptive memory pressure handling:
- Monitors system memory in real-time
- Automatically adjusts cache size based on memory pressure
- Provides accurate metrics and memory tracking
- Implements intelligent eviction strategies

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional, List
from threading import Lock

from .cache import AdvancedMetadataCache
from .memory_pressure import (
    get_global_monitor,
    PressureLevel,
    MemoryStats,
    MemoryPressureMonitor
)

logger = logging.getLogger("metaextract.cache_enhanced")


class EnhancedMetadataCache:
    """
    Enhanced cache wrapper with memory pressure monitoring
    
    Features:
    - Adaptive cache sizing based on memory pressure
    - Automatic eviction during memory pressure
    - Detailed metrics tracking
    - Pressure-based callbacks and logging
    """
    
    def __init__(self,
                 cache_dir: Optional[str] = None,
                 max_memory_entries: int = 500,
                 max_disk_size_mb: int = 200,
                 enable_compression: bool = True,
                 enable_database: bool = True,
                 enable_redis: bool = True,
                 cache_ttl_hours: int = 24,
                 enable_memory_pressure_monitoring: bool = True):
        """
        Initialize enhanced cache with memory pressure monitoring
        
        Args:
            cache_dir: Cache directory path
            max_memory_entries: Maximum entries in memory cache (will be adjusted)
            max_disk_size_mb: Maximum disk cache size in MB
            enable_compression: Enable metadata compression
            enable_database: Enable database caching
            enable_redis: Enable Redis caching
            cache_ttl_hours: Cache TTL in hours
            enable_memory_pressure_monitoring: Enable memory pressure monitoring
        """
        # Initialize base cache with conservative settings
        self.base_cache = AdvancedMetadataCache(
            cache_dir=cache_dir,
            max_memory_entries=max_memory_entries,
            max_disk_size_mb=max_disk_size_mb,
            enable_compression=enable_compression,
            enable_database=enable_database,
            enable_redis=enable_redis,
            cache_ttl_hours=cache_ttl_hours,
            enable_background_cleanup=True
        )
        
        self.enable_memory_pressure_monitoring = enable_memory_pressure_monitoring
        self._memory_monitor: Optional[MemoryPressureMonitor] = None
        self._lock = Lock()
        
        # Enhanced stats
        self._enhanced_stats = {
            'pressure_evictions': 0,
            'pressure_events': 0,
            'adaptive_adjustments': 0,
            'memory_pressure_samples': 0
        }
        
        # Initialize memory pressure monitoring
        if self.enable_memory_pressure_monitoring:
            self._init_memory_pressure_monitoring()
        
        logger.info("Initialized EnhancedMetadataCache with memory pressure monitoring")
    
    def _init_memory_pressure_monitoring(self) -> None:
        """Initialize and configure memory pressure monitoring"""
        try:
            self._memory_monitor = get_global_monitor()
            
            # Register pressure callbacks
            self._memory_monitor.register_pressure_callback(
                PressureLevel.ELEVATED,
                self._on_elevated_pressure
            )
            self._memory_monitor.register_pressure_callback(
                PressureLevel.HIGH,
                self._on_high_pressure
            )
            self._memory_monitor.register_pressure_callback(
                PressureLevel.CRITICAL,
                self._on_critical_pressure
            )
            
            logger.info("Memory pressure monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory pressure monitoring: {e}")
            self.enable_memory_pressure_monitoring = False
    
    def _on_elevated_pressure(self, stats: MemoryStats) -> None:
        """Handle elevated memory pressure (60-80%)"""
        with self._lock:
            self._enhanced_stats['pressure_events'] += 1
            
        logger.warning(
            f"Elevated memory pressure: {stats.system_percent:.1f}% "
            f"({stats.system_available_mb:.0f}MB available)"
        )
        
        # Reduce memory cache by 25%
        original_size = self.base_cache._memory_cache.max_size
        new_size = max(100, int(original_size * 0.75))
        self.base_cache._memory_cache.max_size = new_size
        
        with self._lock:
            self._enhanced_stats['adaptive_adjustments'] += 1
        
        logger.info(f"Reduced memory cache from {original_size} to {new_size} entries")
    
    def _on_high_pressure(self, stats: MemoryStats) -> None:
        """Handle high memory pressure (80-90%)"""
        with self._lock:
            self._enhanced_stats['pressure_events'] += 1
            self._enhanced_stats['pressure_evictions'] += 1
        
        logger.error(
            f"High memory pressure: {stats.system_percent:.1f}% "
            f"({stats.system_available_mb:.0f}MB available)"
        )
        
        # Reduce memory cache by 50%
        original_size = self.base_cache._memory_cache.max_size
        new_size = max(100, int(original_size * 0.5))
        self.base_cache._memory_cache.max_size = new_size
        
        # Trigger disk cache cleanup
        self.base_cache._cleanup_disk_cache()
        
        with self._lock:
            self._enhanced_stats['adaptive_adjustments'] += 1
        
        logger.warning(f"Reduced memory cache from {original_size} to {new_size} entries")
        logger.warning("Triggered disk cache cleanup")
    
    def _on_critical_pressure(self, stats: MemoryStats) -> None:
        """Handle critical memory pressure (>90%)"""
        with self._lock:
            self._enhanced_stats['pressure_events'] += 1
            self._enhanced_stats['pressure_evictions'] += 1
        
        logger.critical(
            f"CRITICAL memory pressure: {stats.system_percent:.1f}% "
            f"({stats.system_available_mb:.0f}MB available)"
        )
        
        # Minimize memory cache
        self.base_cache._memory_cache.max_size = 50
        
        # Aggressively evict from all caches
        self.base_cache._memory_cache.clear()
        self.base_cache._cleanup_disk_cache()
        if self.base_cache.enable_database:
            self.base_cache._cleanup_expired_entries()
        
        with self._lock:
            self._enhanced_stats['adaptive_adjustments'] += 1
        
        logger.critical("Aggressively evicted cache entries due to critical memory pressure")
    
    # ============================================================================
    # Delegate methods to base cache
    # ============================================================================
    
    def get(self, file_path: str, tier: str = "premium") -> Optional[Dict[str, Any]]:
        """Retrieve metadata from cache"""
        return self.base_cache.get(file_path, tier)
    
    def put(self, file_path: str, metadata: Dict[str, Any], 
            tier: str = "premium", extraction_time_ms: int = 0) -> bool:
        """Store metadata in cache"""
        return self.base_cache.put(file_path, metadata, tier, extraction_time_ms)
    
    def invalidate_file(self, file_path: str, tier: Optional[str] = None) -> None:
        """Invalidate cache entries for a file"""
        self.base_cache.invalidate_file(file_path, tier)
    
    def clear_all(self) -> None:
        """Clear all cache data"""
        self.base_cache.clear_all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        base_stats = self.base_cache.get_stats()
        
        with self._lock:
            base_stats.update(self._enhanced_stats)
        
        # Add memory pressure info if available
        if self._memory_monitor:
            memory_summary = self._memory_monitor.get_summary()
            base_stats['memory_pressure'] = memory_summary
        
        return base_stats
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed cache and memory information"""
        detailed = self.base_cache.get_detailed_info()
        
        with self._lock:
            detailed['enhanced_stats'] = self._enhanced_stats.copy()
        
        # Add memory pressure history
        if self._memory_monitor:
            detailed['memory_history'] = [
                {
                    'timestamp': stat.timestamp.isoformat(),
                    'system_percent': stat.system_percent,
                    'available_mb': round(stat.system_available_mb, 2),
                    'pressure_level': stat.pressure_level.name
                }
                for stat in self._memory_monitor.get_history()[-10:]  # Last 10 samples
            ]
        
        return detailed
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory status and pressure information"""
        if not self._memory_monitor:
            return {'available': False}
        
        return self._memory_monitor.get_summary()
    
    def warm_cache(self, file_paths: List[str], tier: str = "premium",
                   max_workers: int = 4) -> Dict[str, bool]:
        """Pre-warm cache with metadata for multiple files"""
        return self.base_cache.warm_cache(file_paths, tier, max_workers)
    
    def shutdown(self) -> None:
        """Shutdown cache and monitoring"""
        self.base_cache.shutdown()
        logger.info("EnhancedMetadataCache shutdown complete")


# Global instance management
_global_enhanced_cache: Optional[EnhancedMetadataCache] = None
_cache_lock = Lock()


def get_enhanced_cache(**kwargs) -> EnhancedMetadataCache:
    """Get or create global enhanced cache instance"""
    global _global_enhanced_cache
    
    if _global_enhanced_cache is None:
        with _cache_lock:
            if _global_enhanced_cache is None:
                _global_enhanced_cache = EnhancedMetadataCache(**kwargs)
    
    return _global_enhanced_cache


def shutdown_enhanced_cache() -> None:
    """Shutdown global enhanced cache"""
    global _global_enhanced_cache
    
    if _global_enhanced_cache:
        _global_enhanced_cache.shutdown()
        _global_enhanced_cache = None
