"""
Perceptual Hash Cache for MetaExtract

Caches perceptual hash calculations which are CPU-intensive operations.
"""

import logging
import time
from typing import Any, Dict, Optional, List
from datetime import timedelta

from .base_cache import BaseCache

logger = logging.getLogger("metaextract.cache.perceptual")


class PerceptualHashCache(BaseCache):
    """
    Caches perceptual hash calculations for images and videos.
    
    Features:
    - Multiple hash algorithm support (pHash, dHash, aHash, wHash)
    - Image content-based cache invalidation
    - Hash comparison result caching
    - Batch processing support
    """
    
    def __init__(self):
        """Initialize perceptual hash cache with 6-hour TTL."""
        super().__init__(cache_prefix="perceptual", default_ttl=21600)  # 6 hours
        self.supported_algorithms = ['phash', 'dhash', 'ahash', 'whash']
    
    def get_cache_key(self, file_path: str, algorithm: str = "phash", 
                     hash_size: int = 8, **kwargs) -> str:
        """
        Generate cache key for perceptual hash calculation.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (phash, dhash, ahash, whash)
            hash_size: Hash size (default 8)
            **kwargs: Additional algorithm parameters
            
        Returns:
            Cache key string
        """
        # Calculate file hash for content-based invalidation
        file_hash = self._calculate_file_hash(file_path, quick=True)
        
        # Create key components
        key_components = [algorithm, file_hash, str(hash_size)]
        
        # Include additional parameters if provided
        if kwargs:
            # Sort parameters for consistent hashing
            sorted_params = sorted(kwargs.items())
            key_components.append(str(sorted_params))
        
        return self._generate_cache_key(*key_components)
    
    def get_cached_result(self, file_path: str, algorithm: str = "phash",
                         hash_size: int = 8, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get cached perceptual hash calculation if available.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm
            hash_size: Hash size
            **kwargs: Additional algorithm parameters
            
        Returns:
            Cached hash result or None
        """
        # Validate algorithm
        if algorithm.lower() not in self.supported_algorithms:
            logger.warning(f"Unsupported algorithm: {algorithm}")
            return None
        
        cache_key = self.get_cache_key(file_path, algorithm, hash_size, **kwargs)
        
        cached_result = self.get(cache_key)
        if cached_result is None:
            return None
        
        # Validate cached result structure
        if not isinstance(cached_result, dict):
            logger.warning(f"Invalid cached perceptual hash format")
            self.delete(cache_key)
            return None
        
        # Check if cached file hash matches current file
        current_file_hash = self._calculate_file_hash(file_path, quick=True)
        cached_file_hash = cached_result.get('file_hash')
        
        if cached_file_hash != current_file_hash:
            logger.debug(f"File {file_path} modified, invalidating perceptual hash cache")
            self.delete(cache_key)
            return None
        
        # Check if hash parameters match
        cached_algorithm = cached_result.get('algorithm')
        cached_hash_size = cached_result.get('hash_size')
        cached_params = cached_result.get('parameters', {})
        
        if (cached_algorithm != algorithm.lower() or 
            cached_hash_size != hash_size or
            cached_params != kwargs):
            logger.debug(f"Hash parameters changed, invalidating cache")
            self.delete(cache_key)
            return None
        
        # Add cache hit information
        cached_result['cache_info'] = {
            'hit': True,
            'cached_at': cached_result.get('cached_at'),
            'cache_key': cache_key,
            'algorithm': algorithm
        }
        
        logger.debug(f"Perceptual hash cache hit: {file_path} ({algorithm})")
        return cached_result
    
    def cache_result(self, hash_value: str, file_path: str, algorithm: str = "phash",
                    hash_size: int = 8, execution_time_ms: Optional[float] = None,
                    **kwargs) -> bool:
        """
        Cache perceptual hash calculation result.
        
        Args:
            hash_value: Calculated perceptual hash
            file_path: Path to the file
            algorithm: Hash algorithm used
            hash_size: Hash size used
            execution_time_ms: Calculation time in milliseconds
            **kwargs: Additional algorithm parameters
            
        Returns:
            True if caching was successful
        """
        # Validate algorithm
        if algorithm.lower() not in self.supported_algorithms:
            logger.warning(f"Unsupported algorithm: {algorithm}")
            return False
        
        cache_key = self.get_cache_key(file_path, algorithm, hash_size, **kwargs)
        
        # Prepare cache data
        cache_data = {
            'hash_value': hash_value,
            'file_hash': self._calculate_file_hash(file_path, quick=True),
            'cached_at': int(time.time()),
            'algorithm': algorithm.lower(),
            'hash_size': hash_size,
            'parameters': kwargs,
            'execution_time_ms': execution_time_ms,
            'file_path': file_path  # For debugging/validation
        }
        
        # Set TTL based on calculation time
        if execution_time_ms and execution_time_ms > 5000:  # > 5 seconds
            ttl = 43200  # 12 hours for very expensive calculations
        elif execution_time_ms and execution_time_ms > 1000:  # > 1 second
            ttl = 32400  # 9 hours for expensive calculations
        else:
            ttl = self.default_ttl  # 6 hours default
        
        success = self.set(cache_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached perceptual hash: {file_path} ({algorithm}, TTL: {ttl}s)")
        else:
            logger.warning(f"Failed to cache perceptual hash: {file_path}")
        
        return success
    
    def get_comparison_cache_key(self, hash1: str, hash2: str, 
                                algorithm: str = "phash") -> str:
        """
        Generate cache key for hash comparison result.
        
        Args:
            hash1: First hash value
            hash2: Second hash value
            algorithm: Hash algorithm
            
        Returns:
            Cache key string
        """
        # Ensure consistent ordering
        if hash1 > hash2:
            hash1, hash2 = hash2, hash1
        
        return self._generate_cache_key("comparison", hash1, hash2, algorithm)
    
    def get_cached_comparison(self, hash1: str, hash2: str,
                             algorithm: str = "phash") -> Optional[float]:
        """
        Get cached hash comparison result.
        
        Args:
            hash1: First hash value
            hash2: Second hash value
            algorithm: Hash algorithm
            
        Returns:
            Cached similarity score (0-1) or None
        """
        cache_key = self.get_comparison_cache_key(hash1, hash2, algorithm)
        
        cached_result = self.get(cache_key)
        if cached_result is None:
            return None
        
        # Validate cached result
        if isinstance(cached_result, dict) and 'similarity' in cached_result:
            similarity = cached_result['similarity']
            if isinstance(similarity, (int, float)) and 0 <= similarity <= 1:
                logger.debug(f"Hash comparison cache hit: {algorithm}")
                return float(similarity)
        
        return None
    
    def cache_comparison_result(self, similarity: float, hash1: str, hash2: str,
                               algorithm: str = "phash") -> bool:
        """
        Cache hash comparison result.
        
        Args:
            similarity: Similarity score (0-1)
            hash1: First hash value
            hash2: Second hash value
            algorithm: Hash algorithm
            
        Returns:
            True if caching was successful
        """
        # Validate similarity score
        if not isinstance(similarity, (int, float)) or not (0 <= similarity <= 1):
            logger.warning(f"Invalid similarity score: {similarity}")
            return False
        
        cache_key = self.get_comparison_cache_key(hash1, hash2, algorithm)
        
        cache_data = {
            'similarity': similarity,
            'hash1': hash1,
            'hash2': hash2,
            'algorithm': algorithm,
            'cached_at': int(time.time())
        }
        
        # Longer TTL for comparison results (24 hours)
        ttl = 86400
        
        success = self.set(cache_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached hash comparison result (similarity: {similarity:.3f})")
        
        return success
    
    def batch_get_hashes(self, file_paths: List[str], algorithm: str = "phash",
                        hash_size: int = 8, **kwargs) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get cached perceptual hashes for multiple files.
        
        Args:
            file_paths: List of file paths
            algorithm: Hash algorithm
            hash_size: Hash size
            **kwargs: Additional algorithm parameters
            
        Returns:
            Dictionary mapping file paths to cached results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                cached_result = self.get_cached_result(
                    file_path, algorithm, hash_size, **kwargs
                )
                results[file_path] = cached_result
            except Exception as e:
                logger.error(f"Error getting cached hash for {file_path}: {e}")
                results[file_path] = None
        
        return results
    
    def batch_cache_hashes(self, hash_results: Dict[str, Dict[str, Any]], 
                          algorithm: str = "phash", hash_size: int = 8,
                          **default_kwargs) -> Dict[str, bool]:
        """
        Cache perceptual hashes for multiple files.
        
        Args:
            hash_results: Dictionary mapping file paths to hash result data
            algorithm: Hash algorithm
            hash_size: Hash size
            **default_kwargs: Default algorithm parameters
            
        Returns:
            Dictionary mapping file paths to caching success status
        """
        results = {}
        
        for file_path, result_data in hash_results.items():
            try:
                # Extract hash value and execution time
                hash_value = result_data.get('hash_value')
                execution_time_ms = result_data.get('execution_time_ms')
                
                # Merge with default kwargs
                kwargs = {**default_kwargs, **result_data.get('parameters', {})}
                
                if hash_value:
                    success = self.cache_result(
                        hash_value, file_path, algorithm, hash_size,
                        execution_time_ms=execution_time_ms, **kwargs
                    )
                    results[file_path] = success
                else:
                    logger.warning(f"No hash value provided for {file_path}")
                    results[file_path] = False
                    
            except Exception as e:
                logger.error(f"Error caching hash for {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def invalidate_file(self, file_path: str) -> int:
        """
        Invalidate all cached perceptual hashes for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of invalidated entries
        """
        file_hash = self._calculate_file_hash(file_path, quick=True)
        pattern = f"*_{file_hash}_*"
        
        count = self.invalidate_by_pattern(pattern)
        logger.info(f"Invalidated {count} perceptual hash cache entries for {file_path}")
        return count
    
    def get_algorithm_stats(self, algorithm: str) -> Dict[str, Any]:
        """Get cache statistics for specific algorithm."""
        if algorithm.lower() not in self.supported_algorithms:
            return {'error': f'Unsupported algorithm: {algorithm}'}
        
        stats = self.get_stats()
        
        # Count keys for this algorithm
        algorithm_pattern = f"{algorithm.lower()}_*"
        algorithm_keys = self.redis_client.keys(f"{self.cache_prefix}:{algorithm_pattern}")
        
        # Calculate average execution time
        total_time = 0
        count = 0
        for key in algorithm_keys:
            cached_data = self.get(key)
            if cached_data and 'execution_time_ms' in cached_data:
                total_time += cached_data['execution_time_ms']
                count += 1
        
        avg_execution_time = total_time / count if count > 0 else 0
        
        stats.update({
            'algorithm_keys': len(algorithm_keys),
            'algorithm': algorithm,
            'avg_execution_time_ms': round(avg_execution_time, 2)
        })
        
        return stats
    
    def get_expensive_calculations(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """
        Get files with expensive perceptual hash calculations.
        
        Args:
            threshold_ms: Execution time threshold in milliseconds
            
        Returns:
            List of expensive calculation information
        """
        expensive_calcs = []
        
        # Get all perceptual hash cache keys
        all_keys = self.redis_client.keys(f"{self.cache_prefix}:*")
        
        for key in all_keys:
            try:
                cached_data = self.get(key)
                if (cached_data and isinstance(cached_data, dict) and
                    'execution_time_ms' in cached_data and
                    'algorithm' in cached_data and
                    'file_path' in cached_data):
                    
                    execution_time = cached_data['execution_time_ms']
                    if execution_time > threshold_ms:
                        expensive_calcs.append({
                            'file_path': cached_data['file_path'],
                            'algorithm': cached_data['algorithm'],
                            'execution_time_ms': execution_time,
                            'hash_size': cached_data.get('hash_size', 8),
                            'cached_at': cached_data.get('cached_at')
                        })
            except Exception as e:
                logger.error(f"Error reading cached data from key {key}: {e}")
        
        # Sort by execution time
        expensive_calcs.sort(key=lambda x: x['execution_time_ms'], reverse=True)
        
        return expensive_calcs[:50]  # Limit to top 50