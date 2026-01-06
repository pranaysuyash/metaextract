"""
Extraction Result Cache for MetaExtract

Caches complete metadata extraction results to avoid re-running expensive operations.
"""

import logging
import time
from typing import Any, Dict, Optional
from datetime import timedelta

from .base_cache import BaseCache

logger = logging.getLogger("metaextract.cache.extraction")


class ExtractionCache(BaseCache):
    """
    Caches complete metadata extraction results.
    
    Features:
    - File content-based cache invalidation
    - Tier-specific caching
    - Format-specific optimization
    - Processing time tracking
    """
    
    def __init__(self):
        """Initialize extraction cache with 1-hour TTL."""
        super().__init__(cache_prefix="extraction", default_ttl=3600)  # 1 hour
    
    def get_cache_key(self, file_path: str, tier: str = "free", 
                     file_format: Optional[str] = None) -> str:
        """
        Generate cache key for extraction result.
        
        Args:
            file_path: Path to the file
            tier: User tier level
            file_format: File format (optional)
            
        Returns:
            Cache key string
        """
        # Calculate file hash for content-based invalidation
        file_hash = self._calculate_file_hash(file_path, quick=True)
        
        # Include tier and format in key
        key_components = [file_hash, tier]
        if file_format:
            key_components.append(file_format)
        
        return self._generate_cache_key(*key_components)
    
    def get_cached_result(self, file_path: str, tier: str = "free",
                         file_format: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached extraction result if available and valid.
        
        Args:
            file_path: Path to the file
            tier: User tier level
            file_format: File format (optional)
            
        Returns:
            Cached metadata or None if not available/valid
        """
        cache_key = self.get_cache_key(file_path, tier, file_format)
        
        # Check if file has been modified
        cached_result = self.get(cache_key)
        if cached_result is None:
            return None
        
        # Validate cached result structure
        if not isinstance(cached_result, dict):
            logger.warning(f"Invalid cached result format for {file_path}")
            self.delete(cache_key)
            return None
        
        # Check if cached file hash matches current file
        current_file_hash = self._calculate_file_hash(file_path, quick=True)
        cached_file_hash = cached_result.get('file_hash')
        
        if cached_file_hash != current_file_hash:
            logger.debug(f"File {file_path} modified, invalidating cache")
            self.delete(cache_key)
            return None
        
        # Add cache hit information
        cached_result['cache_info'] = {
            'hit': True,
            'cached_at': cached_result.get('cached_at'),
            'cache_key': cache_key
        }
        
        logger.debug(f"Cache hit for extraction: {file_path} (tier: {tier})")
        return cached_result
    
    def cache_result(self, result: Dict[str, Any], file_path: str, 
                    tier: str = "free", file_format: Optional[str] = None,
                    processing_time_ms: Optional[float] = None) -> bool:
        """
        Cache extraction result.
        
        Args:
            result: Extraction result to cache
            file_path: Path to the file
            tier: User tier level
            file_format: File format (optional)
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            True if caching was successful
        """
        cache_key = self.get_cache_key(file_path, tier, file_format)
        
        # Add metadata for cache validation
        cache_data = result.copy()
        cache_data['file_hash'] = self._calculate_file_hash(file_path, quick=True)
        cache_data['cached_at'] = int(time.time())
        cache_data['tier'] = tier
        cache_data['file_format'] = file_format
        cache_data['processing_time_ms'] = processing_time_ms
        
        # Remove any existing cache info to avoid confusion
        cache_data.pop('cache_info', None)
        
        # Set appropriate TTL based on tier
        if tier == "super":
            ttl = 7200  # 2 hours for super tier
        elif tier == "premium":
            ttl = 5400  # 1.5 hours for premium tier
        else:
            ttl = self.default_ttl  # Default 1 hour
        
        success = self.set(cache_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached extraction result: {file_path} (tier: {tier}, TTL: {ttl}s)")
        else:
            logger.warning(f"Failed to cache extraction result: {file_path}")
        
        return success
    
    def invalidate_file(self, file_path: str, tier: Optional[str] = None) -> int:
        """
        Invalidate all cached results for a file.
        
        Args:
            file_path: Path to the file
            tier: Specific tier to invalidate (optional)
            
        Returns:
            Number of invalidated entries
        """
        if tier:
            # Generate the exact cache key for this file+tier combination
            cache_key = self.get_cache_key(file_path, tier)
            success = self.delete(cache_key)
            count = 1 if success else 0
        else:
            # Invalidate all tiers - need to check all possible tiers
            count = 0
            for tier_name in ["free", "starter", "premium", "super"]:
                cache_key = self.get_cache_key(file_path, tier_name)
                if self.exists(cache_key):
                    if self.delete(cache_key):
                        count += 1
        logger.info(f"Invalidated {count} extraction cache entries for {file_path}")
        return count
    
    def get_tier_stats(self, tier: str) -> Dict[str, Any]:
        """Get cache statistics for specific tier."""
        stats = self.get_stats()
        
        # Count keys for this tier
        tier_pattern = f"*_{tier}*"
        tier_keys = self.redis_client.keys(f"{self.cache_prefix}:{tier_pattern}")
        
        stats['tier_keys'] = len(tier_keys)
        stats['tier'] = tier
        
        return stats
    
    def warm_cache(self, file_paths: list, tier: str = "free") -> Dict[str, bool]:
        """
        Pre-warm cache by extracting metadata for multiple files.
        
        Args:
            file_paths: List of file paths to warm
            tier: User tier level
            
        Returns:
            Dictionary mapping file paths to success status
        """
        from ..extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor
        
        results = {}
        extractor = NewComprehensiveMetadataExtractor()
        
        for file_path in file_paths:
            try:
                # Check if already cached
                if self.get_cached_result(file_path, tier) is not None:
                    results[file_path] = True
                    continue
                
                # Extract and cache
                start_time = time.time()
                result = extractor.extract_comprehensive_metadata(file_path, tier)
                processing_time = (time.time() - start_time) * 1000
                
                # Cache the result
                success = self.cache_result(
                    result, file_path, tier, 
                    processing_time_ms=processing_time
                )
                
                results[file_path] = success
                
            except Exception as e:
                logger.error(f"Failed to warm cache for {file_path}: {e}")
                results[file_path] = False
        
        logger.info(f"Cache warming completed: {sum(results.values())}/{len(results)} files")
        return results