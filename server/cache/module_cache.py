"""
Module Extraction Result Cache for MetaExtract

Caches results from individual extraction modules to avoid re-running expensive operations.
"""

import logging
import time
from typing import Any, Dict, Optional, List
from datetime import timedelta

from .base_cache import BaseCache

logger = logging.getLogger("metaextract.cache.module")


class ModuleCache(BaseCache):
    """
    Caches results from individual extraction modules.
    
    Features:
    - Module-specific caching
    - Parameter-based cache keys
    - File content validation
    - Module execution time tracking
    """
    
    def __init__(self):
        """Initialize module cache with 2-hour TTL."""
        super().__init__(cache_prefix="module", default_ttl=7200)  # 2 hours
    
    def get_cache_key(self, module_name: str, file_path: str, 
                     module_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate cache key for module result.
        
        Args:
            module_name: Name of the extraction module
            file_path: Path to the file
            module_params: Module parameters (optional)
            
        Returns:
            Cache key string
        """
        # Calculate file hash for content-based invalidation
        file_hash = self._calculate_file_hash(file_path, quick=True)
        
        # Create key components
        key_components = [module_name, file_hash]
        
        # Include module parameters if provided
        if module_params:
            # Sort parameters for consistent hashing
            sorted_params = sorted(module_params.items())
            key_components.append(str(sorted_params))
        
        return self._generate_cache_key(*key_components)
    
    def get_cached_result(self, module_name: str, file_path: str,
                         module_params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached module result if available and valid.
        
        Args:
            module_name: Name of the extraction module
            file_path: Path to the file
            module_params: Module parameters (optional)
            
        Returns:
            Cached module result or None if not available/valid
        """
        cache_key = self.get_cache_key(module_name, file_path, module_params)
        
        # Get cached result
        cached_result = self.get(cache_key)
        if cached_result is None:
            return None
        
        # Validate cached result structure
        if not isinstance(cached_result, dict):
            logger.warning(f"Invalid cached module result format for {module_name}")
            self.delete(cache_key)
            return None
        
        # Check if cached file hash matches current file
        current_file_hash = self._calculate_file_hash(file_path, quick=True)
        cached_file_hash = cached_result.get('file_hash')
        
        if cached_file_hash != current_file_hash:
            logger.debug(f"File {file_path} modified, invalidating {module_name} cache")
            self.delete(cache_key)
            return None
        
        # Check if module parameters match
        cached_params = cached_result.get('module_params', {})
        current_params = module_params or {}
        
        if cached_params != current_params:
            logger.debug(f"Module parameters changed for {module_name}, invalidating cache")
            self.delete(cache_key)
            return None
        
        # Add cache hit information
        cached_result['cache_info'] = {
            'hit': True,
            'cached_at': cached_result.get('cached_at'),
            'cache_key': cache_key,
            'module_name': module_name
        }
        
        logger.debug(f"Module cache hit: {module_name} for {file_path}")
        return cached_result
    
    def cache_result(self, result: Any, module_name: str, file_path: str,
                    module_params: Optional[Dict[str, Any]] = None,
                    execution_time_ms: Optional[float] = None) -> bool:
        """
        Cache module result.
        
        Args:
            result: Module result to cache
            module_name: Name of the extraction module
            file_path: Path to the file
            module_params: Module parameters (optional)
            execution_time_ms: Module execution time in milliseconds
            
        Returns:
            True if caching was successful
        """
        cache_key = self.get_cache_key(module_name, file_path, module_params)
        
        # Prepare cache data
        cache_data = {
            'result': result,
            'file_hash': self._calculate_file_hash(file_path, quick=True),
            'cached_at': int(time.time()),
            'module_name': module_name,
            'module_params': module_params or {},
            'execution_time_ms': execution_time_ms
        }
        
        # Set TTL based on module execution time
        # Longer execution time = longer cache TTL
        if execution_time_ms and execution_time_ms > 1000:  # > 1 second
            ttl = 14400  # 4 hours for expensive modules
        elif execution_time_ms and execution_time_ms > 100:  # > 100ms
            ttl = 10800  # 3 hours for moderate modules
        else:
            ttl = self.default_ttl  # 2 hours for fast modules
        
        success = self.set(cache_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached {module_name} result: {file_path} (TTL: {ttl}s)")
        else:
            logger.warning(f"Failed to cache {module_name} result: {file_path}")
        
        return success
    
    def invalidate_module(self, module_name: str, file_path: str,
                         module_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate cached results for specific module and file.
        
        Args:
            module_name: Name of the module
            file_path: Path to the file
            module_params: Specific parameters (optional)
            
        Returns:
            Number of invalidated entries
        """
        if module_params:
            # Invalidate specific parameter combination
            cache_key = self.get_cache_key(module_name, file_path, module_params)
            success = self.delete(cache_key)
            count = 1 if success else 0
        else:
            # Invalidate all parameter combinations - this is more complex
            # We need to find all keys that match this module+file combination
            file_hash = self._calculate_file_hash(file_path, quick=True)
            pattern = f"{module_name}_{file_hash}_*"
            count = self.invalidate_by_pattern(pattern)
        
        logger.info(f"Invalidated {count} cache entries for {module_name}: {file_path}")
        return count
    
    def invalidate_file(self, file_path: str) -> int:
        """
        Invalidate all cached module results for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of invalidated entries
        """
        # For module cache, we need to find all modules that cached results for this file
        # This is complex because we don't know which modules were used
        # We'll use the pattern approach but with the correct file hash
        file_hash = self._calculate_file_hash(file_path, quick=True)
        pattern = f"*_{file_hash}*"
        
        count = self.invalidate_by_pattern(pattern)
        logger.info(f"Invalidated {count} module cache entries for {file_path}")
        return count
    
    def get_module_stats(self, module_name: str) -> Dict[str, Any]:
        """Get cache statistics for specific module."""
        stats = self.get_stats()
        
        # Count keys for this module
        module_pattern = f"{module_name}_*"
        module_keys = self.redis_client.keys(f"{self.cache_prefix}:{module_pattern}")
        
        # Calculate average execution time
        total_time = 0
        count = 0
        for key in module_keys:
            cached_data = self.get(key)
            if cached_data and 'execution_time_ms' in cached_data:
                total_time += cached_data['execution_time_ms']
                count += 1
        
        avg_execution_time = total_time / count if count > 0 else 0
        
        stats.update({
            'module_keys': len(module_keys),
            'module_name': module_name,
            'avg_execution_time_ms': round(avg_execution_time, 2)
        })
        
        return stats
    
    def get_expensive_modules(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """
        Get modules with average execution time above threshold.
        
        Args:
            threshold_ms: Execution time threshold in milliseconds
            
        Returns:
            List of expensive module information
        """
        expensive_modules = []
        
        # Get all module cache keys
        all_keys = self.redis_client.keys(f"{self.cache_prefix}:*")
        
        # Group by module name
        module_stats = {}
        for key in all_keys:
            # Extract module name from key
            key_parts = key.split(":", 1)[1].split("_", 1)
            if len(key_parts) > 0:
                module_name = key_parts[0]
                cached_data = self.get(key)
                
                if cached_data and 'execution_time_ms' in cached_data:
                    if module_name not in module_stats:
                        module_stats[module_name] = {
                            'total_time': 0,
                            'count': 0,
                            'max_time': 0
                        }
                    
                    execution_time = cached_data['execution_time_ms']
                    module_stats[module_name]['total_time'] += execution_time
                    module_stats[module_name]['count'] += 1
                    module_stats[module_name]['max_time'] = max(
                        module_stats[module_name]['max_time'], execution_time
                    )
        
        # Find expensive modules
        for module_name, stats in module_stats.items():
            avg_time = stats['total_time'] / stats['count']
            if avg_time > threshold_ms:
                expensive_modules.append({
                    'module_name': module_name,
                    'avg_execution_time_ms': round(avg_time, 2),
                    'max_execution_time_ms': round(stats['max_time'], 2),
                    'cache_entries': stats['count']
                })
        
        # Sort by average execution time
        expensive_modules.sort(key=lambda x: x['avg_execution_time_ms'], reverse=True)
        
        return expensive_modules