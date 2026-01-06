"""
Cache Manager for MetaExtract

Provides centralized cache management and coordination between different cache types.
"""

import logging
import time
from typing import Any, Dict, Optional, List
from datetime import timedelta

from .extraction_cache import ExtractionCache
from .module_cache import ModuleCache
from .geocoding_cache import GeocodingCache
from .perceptual_cache import PerceptualHashCache
from .redis_client import get_redis_client

logger = logging.getLogger("metaextract.cache.manager")


class CacheManager:
    """
    Centralized cache manager for all caching operations.
    
    Features:
    - Unified cache management
    - Cross-cache invalidation
    - Performance monitoring
    - Cache warming coordination
    - Health monitoring
    """
    
    def __init__(self):
        """Initialize cache manager with all cache types."""
        self.extraction_cache = ExtractionCache()
        self.module_cache = ModuleCache()
        self.geocoding_cache = GeocodingCache()
        self.perceptual_cache = PerceptualHashCache()
        self.redis_client = get_redis_client()
        
        # Cache configuration
        self.cache_enabled = True
        self.auto_invalidation = True
        self.performance_monitoring = True
        
        # Performance tracking
        self._performance_stats = {
            'cache_lookups': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_saves': 0,
            'cache_invalidations': 0,
            'time_saved_ms': 0
        }
        
        logger.info("Initialized CacheManager with all cache types")
    
    def get_extraction_result(self, file_path: str, tier: str = "free",
                            file_format: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached extraction result with performance tracking.
        
        Args:
            file_path: Path to the file
            tier: User tier level
            file_format: File format (optional)
            
        Returns:
            Cached extraction result or None
        """
        if not self.cache_enabled:
            return None
        
        start_time = time.time()
        self._performance_stats['cache_lookups'] += 1
        
        try:
            result = self.extraction_cache.get_cached_result(
                file_path, tier, file_format
            )
            
            if result:
                self._performance_stats['cache_hits'] += 1
                # Estimate time saved (assume 2-5 seconds for extraction)
                time_saved = 3000  # 3 seconds average
                self._performance_stats['time_saved_ms'] += time_saved
                logger.debug(f"Extraction cache hit: {file_path}")
            else:
                self._performance_stats['cache_misses'] += 1
                logger.debug(f"Extraction cache miss: {file_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting extraction cache for {file_path}: {e}")
            return None
        finally:
            lookup_time = (time.time() - start_time) * 1000
            logger.debug(f"Extraction cache lookup took {lookup_time:.2f}ms")
    
    def cache_extraction_result(self, result: Dict[str, Any], file_path: str,
                              tier: str = "free", file_format: Optional[str] = None,
                              processing_time_ms: Optional[float] = None) -> bool:
        """
        Cache extraction result with performance tracking.
        
        Args:
            result: Extraction result
            file_path: Path to the file
            tier: User tier level
            file_format: File format (optional)
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            True if caching was successful
        """
        if not self.cache_enabled:
            return False
        
        try:
            success = self.extraction_cache.cache_result(
                result, file_path, tier, file_format, processing_time_ms
            )
            
            if success:
                self._performance_stats['cache_saves'] += 1
                logger.debug(f"Cached extraction result: {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error caching extraction result for {file_path}: {e}")
            return False
    
    def get_module_result(self, module_name: str, file_path: str,
                         module_params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Get cached module result.
        
        Args:
            module_name: Name of the module
            file_path: Path to the file
            module_params: Module parameters (optional)
            
        Returns:
            Cached module result or None
        """
        if not self.cache_enabled:
            return None
        
        try:
            cached_result = self.module_cache.get_cached_result(
                module_name, file_path, module_params
            )
            
            if cached_result:
                # Extract just the result, not the cache metadata
                return cached_result.get('result')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting module cache for {module_name}: {file_path}: {e}")
            return None
    
    def cache_module_result(self, result: Any, module_name: str, file_path: str,
                           module_params: Optional[Dict[str, Any]] = None,
                           execution_time_ms: Optional[float] = None) -> bool:
        """
        Cache module result.
        
        Args:
            result: Module result
            module_name: Name of the module
            file_path: Path to the file
            module_params: Module parameters (optional)
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            True if caching was successful
        """
        if not self.cache_enabled:
            return False
        
        try:
            return self.module_cache.cache_result(
                result, module_name, file_path, module_params, execution_time_ms
            )
        except Exception as e:
            logger.error(f"Error caching module result for {module_name}: {file_path}: {e}")
            return False
    
    def get_geocoding_result(self, lat: float, lon: float,
                           provider: str = "nominatim") -> Optional[Dict[str, Any]]:
        """
        Get cached geocoding result.
        
        Args:
            lat: Latitude
            lon: Longitude
            provider: Geocoding provider
            
        Returns:
            Cached geocoding result or None
        """
        if not self.cache_enabled:
            return None
        
        try:
            cached_result = self.geocoding_cache.get_cached_result(lat, lon, provider)
            
            if cached_result:
                # Extract just the result, not the cache metadata
                result = {k: v for k, v in cached_result.items() 
                         if k not in ['cache_info', 'cached_at', 'lat', 'lon', 'provider']}
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting geocoding cache for ({lat}, {lon}): {e}")
            return None
    
    def cache_geocoding_result(self, result: Dict[str, Any], lat: float, lon: float,
                              provider: str = "nominatim") -> bool:
        """
        Cache geocoding result.
        
        Args:
            result: Geocoding result
            lat: Latitude
            lon: Longitude
            provider: Geocoding provider
            
        Returns:
            True if caching was successful
        """
        if not self.cache_enabled:
            return False
        
        try:
            return self.geocoding_cache.cache_result(result, lat, lon, provider)
        except Exception as e:
            logger.error(f"Error caching geocoding result for ({lat}, {lon}): {e}")
            return False
    
    def get_perceptual_hash(self, file_path: str, algorithm: str = "phash",
                           hash_size: int = 8, **kwargs) -> Optional[str]:
        """
        Get cached perceptual hash.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm
            hash_size: Hash size
            **kwargs: Additional algorithm parameters
            
        Returns:
            Cached hash value or None
        """
        if not self.cache_enabled:
            return None
        
        try:
            cached_result = self.perceptual_cache.get_cached_result(
                file_path, algorithm, hash_size, **kwargs
            )
            
            if cached_result:
                return cached_result.get('hash_value')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting perceptual hash cache for {file_path}: {e}")
            return None
    
    def cache_perceptual_hash(self, hash_value: str, file_path: str,
                             algorithm: str = "phash", hash_size: int = 8,
                             execution_time_ms: Optional[float] = None,
                             **kwargs) -> bool:
        """
        Cache perceptual hash calculation.
        
        Args:
            hash_value: Calculated hash
            file_path: Path to the file
            algorithm: Hash algorithm
            hash_size: Hash size
            execution_time_ms: Calculation time
            **kwargs: Additional algorithm parameters
            
        Returns:
            True if caching was successful
        """
        if not self.cache_enabled:
            return False
        
        try:
            return self.perceptual_cache.cache_result(
                hash_value, file_path, algorithm, hash_size, execution_time_ms, **kwargs
            )
        except Exception as e:
            logger.error(f"Error caching perceptual hash for {file_path}: {e}")
            return False
    
    def invalidate_file(self, file_path: str) -> int:
        """
        Invalidate all cached results for a file across all cache types.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Total number of invalidated entries
        """
        if not self.auto_invalidation:
            return 0
        
        total_invalidated = 0
        
        try:
            # Invalidate extraction cache
            extraction_count = self.extraction_cache.invalidate_file(file_path)
            total_invalidated += extraction_count
            
            # Invalidate module cache
            module_count = self.module_cache.invalidate_file(file_path)
            total_invalidated += module_count
            
            # Invalidate perceptual hash cache
            perceptual_count = self.perceptual_cache.invalidate_file(file_path)
            total_invalidated += perceptual_count
            
            self._performance_stats['cache_invalidations'] += total_invalidated
            
            logger.info(f"Invalidated {total_invalidated} cache entries for {file_path}")
            return total_invalidated
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {file_path}: {e}")
            return 0
    
    def invalidate_coordinates(self, lat: float, lon: float) -> int:
        """
        Invalidate geocoding cache for specific coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Number of invalidated entries
        """
        try:
            count = self.geocoding_cache.invalidate_coordinates(lat, lon)
            self._performance_stats['cache_invalidations'] += count
            return count
        except Exception as e:
            logger.error(f"Error invalidating geocoding cache for ({lat}, {lon}): {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary containing all cache statistics
        """
        # Get individual cache stats
        extraction_stats = self.extraction_cache.get_stats()
        module_stats = self.module_cache.get_stats()
        geocoding_stats = self.geocoding_cache.get_stats()
        perceptual_stats = self.perceptual_cache.get_stats()
        
        # Calculate overall statistics
        total_hits = (extraction_stats['stats']['hits'] + 
                     module_stats['stats']['hits'] + 
                     geocoding_stats['stats']['hits'] + 
                     perceptual_stats['stats']['hits'])
        
        # Calculate total requests from hits + misses for each cache
        total_requests = (extraction_stats['stats']['hits'] + extraction_stats['stats']['misses'] +
                         module_stats['stats']['hits'] + module_stats['stats']['misses'] +
                         geocoding_stats['stats']['hits'] + geocoding_stats['stats']['misses'] +
                         perceptual_stats['stats']['hits'] + perceptual_stats['stats']['misses'])
        
        overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_manager': {
                'enabled': self.cache_enabled,
                'auto_invalidation': self.auto_invalidation,
                'performance_monitoring': self.performance_monitoring,
                'performance_stats': self._performance_stats.copy()
            },
            'overall_stats': {
                'total_hits': total_hits,
                'total_requests': total_requests,
                'overall_hit_rate_percent': round(overall_hit_rate, 2)
            },
            'extraction_cache': extraction_stats,
            'module_cache': module_stats,
            'geocoding_cache': geocoding_stats,
            'perceptual_cache': perceptual_stats,
            'redis_status': {
                'connected': self.redis_client.is_connected,
                'info': self.redis_client.info() if self.redis_client.is_connected else None
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary showing cache effectiveness.
        
        Returns:
            Performance summary dictionary
        """
        stats = self.get_stats()
        perf_stats = self._performance_stats
        
        # Calculate time saved
        time_saved_hours = perf_stats['time_saved_ms'] / (1000 * 60 * 60)
        
        # Get expensive operations from module cache
        expensive_modules = self.module_cache.get_expensive_modules(threshold_ms=1000)
        expensive_calcs = self.perceptual_cache.get_expensive_calculations(threshold_ms=1000)
        
        return {
            'cache_effectiveness': {
                'hit_rate_percent': stats['overall_stats']['overall_hit_rate_percent'],
                'time_saved_hours': round(time_saved_hours, 2),
                'total_lookups': perf_stats['cache_lookups'],
                'total_invalidations': perf_stats['cache_invalidations']
            },
            'expensive_operations': {
                'expensive_modules': expensive_modules[:10],  # Top 10
                'expensive_perceptual_calculations': expensive_calcs[:10]  # Top 10
            },
            'cache_distribution': {
                'extraction_cache_hit_rate': stats['extraction_cache']['hit_rate_percent'],
                'module_cache_hit_rate': stats['module_cache']['hit_rate_percent'],
                'geocoding_cache_hit_rate': stats['geocoding_cache']['hit_rate_percent'],
                'perceptual_cache_hit_rate': stats['perceptual_cache']['hit_rate_percent']
            }
        }
    
    def warm_cache(self, file_paths: List[str], tier: str = "free") -> Dict[str, bool]:
        """
        Pre-warm cache for multiple files.
        
        Args:
            file_paths: List of file paths to warm
            tier: User tier level
            
        Returns:
            Dictionary mapping file paths to success status
        """
        logger.info(f"Starting cache warming for {len(file_paths)} files")
        
        # Use extraction cache's warm_cache method
        return self.extraction_cache.warm_cache(file_paths, tier)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all cache systems.
        
        Returns:
            Health check results
        """
        health_status = {
            'overall_status': 'healthy',
            'cache_enabled': self.cache_enabled,
            'redis_connected': self.redis_client.is_connected,
            'cache_systems': {}
        }
        
        # Check each cache system
        cache_systems = {
            'extraction_cache': self.extraction_cache,
            'module_cache': self.module_cache,
            'geocoding_cache': self.geocoding_cache,
            'perceptual_cache': self.perceptual_cache
        }
        
        for name, cache in cache_systems.items():
            try:
                stats = cache.get_stats()
                health_status['cache_systems'][name] = {
                    'status': 'healthy',
                    'hit_rate_percent': stats['hit_rate_percent'],
                    'redis_connected': stats['redis_connected']
                }
            except Exception as e:
                health_status['cache_systems'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        
        # Overall health determination
        if not self.redis_client.is_connected:
            health_status['overall_status'] = 'unhealthy'
        elif health_status['overall_status'] == 'healthy':
            # Check if any cache has very low hit rate
            for cache_name, cache_status in health_status['cache_systems'].items():
                if cache_status['status'] == 'healthy' and cache_status['hit_rate_percent'] < 10:
                    health_status['overall_status'] = 'warning'
                    break
        
        return health_status
    
    def clear_all_caches(self) -> bool:
        """
        Clear all cache data across all cache types.
        
        Returns:
            True if successful
        """
        try:
            success = True
            
            # Clear each cache type
            success &= self.extraction_cache.clear_all()
            success &= self.module_cache.clear_all()
            success &= self.geocoding_cache.clear_all()
            success &= self.perceptual_cache.clear_all()
            
            # Reset performance stats
            self._performance_stats = {k: 0 for k in self._performance_stats}
            
            logger.info("All caches cleared successfully")
            return success
            
        except Exception as e:
            logger.error(f"Error clearing all caches: {e}")
            return False


# Global cache manager instance
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _global_cache_manager
    
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    
    return _global_cache_manager


def invalidate_file_caches(file_path: str) -> int:
    """
    Convenience function to invalidate all caches for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Number of invalidated entries
    """
    manager = get_cache_manager()
    return manager.invalidate_file(file_path)


def get_cache_stats() -> Dict[str, Any]:
    """
    Convenience function to get comprehensive cache statistics.
    
    Returns:
        Cache statistics
    """
    manager = get_cache_manager()
    return manager.get_stats()


def health_check() -> Dict[str, Any]:
    """
    Convenience function to perform cache health check.
    
    Returns:
        Health check results
    """
    manager = get_cache_manager()
    return manager.health_check()