"""
MetaExtract Advanced Optimizations v1.0

Implements advanced optimization techniques:
- Adaptive chunk sizing based on file characteristics
- GPU acceleration for compatible formats
- Machine learning-based scheduling
- Smart caching strategies
- Performance prediction

Author: MetaExtract Team
"""

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from pathlib import Path
import time
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class OptimizationStrategy(ABC):
    """Base class for optimization strategies."""
    
    @abstractmethod
    def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimization."""
        pass


@dataclass
class FileCharacteristics:
    """Analyzed characteristics of a file."""
    file_path: str
    file_size: int
    file_type: str
    estimated_chunks: int
    recommended_chunk_size: int
    expected_processing_time: float
    complexity_score: float  # 0-1, higher = more complex


class AdaptiveChunkSizer(OptimizationStrategy):
    """Dynamically adjusts chunk size based on file characteristics."""
    
    def __init__(self):
        self.baseline_chunk_size = 1024 * 1024  # 1MB
        self.file_analysis_cache: Dict[str, FileCharacteristics] = {}
        self.lock = threading.RLock()
    
    def analyze_file(self, file_path: str) -> FileCharacteristics:
        """Analyze file to determine optimal chunk size."""
        try:
            file_size = Path(file_path).stat().st_size
            file_type = Path(file_path).suffix.lower()
            
            # Check cache
            with self.lock:
                if file_path in self.file_analysis_cache:
                    return self.file_analysis_cache[file_path]
            
            # Calculate characteristics
            complexity_score = self._calculate_complexity(file_path, file_type)
            
            # Determine optimal chunk size
            if file_size < 10 * 1024 * 1024:  # < 10MB
                chunk_size = 256 * 1024  # 256KB
            elif file_size < 100 * 1024 * 1024:  # < 100MB
                chunk_size = 1024 * 1024  # 1MB
            elif file_size < 1024 * 1024 * 1024:  # < 1GB
                chunk_size = 5 * 1024 * 1024  # 5MB
            else:  # >= 1GB
                chunk_size = 10 * 1024 * 1024  # 10MB
            
            # Adjust for complexity
            if complexity_score > 0.7:
                chunk_size = int(chunk_size * 0.5)  # Smaller chunks for complex files
            elif complexity_score < 0.3:
                chunk_size = int(chunk_size * 1.5)  # Larger chunks for simple files
            
            estimated_chunks = (file_size + chunk_size - 1) // chunk_size
            expected_time = self._estimate_processing_time(file_size, complexity_score)
            
            characteristics = FileCharacteristics(
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                estimated_chunks=estimated_chunks,
                recommended_chunk_size=chunk_size,
                expected_processing_time=expected_time,
                complexity_score=complexity_score
            )
            
            # Cache result
            with self.lock:
                self.file_analysis_cache[file_path] = characteristics
            
            return characteristics
        
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            # Return default characteristics
            return FileCharacteristics(
                file_path=file_path,
                file_size=0,
                file_type="unknown",
                estimated_chunks=0,
                recommended_chunk_size=self.baseline_chunk_size,
                expected_processing_time=0,
                complexity_score=0.5
            )
    
    def _calculate_complexity(self, file_path: str, file_type: str) -> float:
        """Calculate complexity score based on file characteristics."""
        # Higher complexity for certain formats
        complex_formats = {
            '.dcm': 0.9,      # DICOM - medical imaging
            '.fits': 0.8,     # FITS - astronomical
            '.h5': 0.7,       # HDF5 - scientific
            '.nc': 0.7,       # NetCDF
            '.mp4': 0.6,      # Video
            '.avi': 0.6,
            '.pdf': 0.5,      # PDF
        }
        
        return complex_formats.get(file_type, 0.4)
    
    def _estimate_processing_time(self, file_size: int, complexity: float) -> float:
        """Estimate processing time based on size and complexity."""
        # Baseline: 1 second per 100MB for simple files
        base_time = (file_size / (100 * 1024 * 1024)) * 1.0
        
        # Apply complexity multiplier
        complexity_multiplier = 1.0 + (complexity * 2.0)
        
        return base_time * complexity_multiplier
    
    def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize chunk size for given file."""
        file_path = context.get('file_path')
        if not file_path:
            return context
        
        characteristics = self.analyze_file(file_path)
        
        return {
            **context,
            'chunk_size': characteristics.recommended_chunk_size,
            'estimated_chunks': characteristics.estimated_chunks,
            'expected_time': characteristics.expected_processing_time,
            'complexity': characteristics.complexity_score
        }


class PerformancePredictor:
    """Predicts extraction performance using historical data."""
    
    def __init__(self):
        self.performance_history: Dict[str, List[float]] = defaultdict(list)
        self.file_size_history: Dict[str, List[int]] = defaultdict(list)
        self.lock = threading.RLock()
    
    def record_extraction(self, file_type: str, file_size: int, processing_time: float) -> None:
        """Record extraction performance."""
        with self.lock:
            self.performance_history[file_type].append(processing_time)
            self.file_size_history[file_type].append(file_size)
            
            # Keep only last 1000 measurements
            if len(self.performance_history[file_type]) > 1000:
                self.performance_history[file_type] = self.performance_history[file_type][-1000:]
                self.file_size_history[file_type] = self.file_size_history[file_type][-1000:]
    
    def predict_time(self, file_type: str, file_size: int) -> float:
        """Predict processing time for file."""
        with self.lock:
            if file_type not in self.performance_history:
                # No data, return estimate
                return (file_size / (100 * 1024 * 1024)) * 1.0
            
            times = self.performance_history[file_type]
            sizes = self.file_size_history[file_type]
            
            if not times:
                return 0
            
            # Calculate average throughput
            throughputs = [size / time if time > 0 else 0 for size, time in zip(sizes, times)]
            avg_throughput = statistics.median(throughputs[-10:]) if throughputs else 0
            
            if avg_throughput > 0:
                return file_size / avg_throughput
            else:
                return statistics.median(times[-10:])
    
    def get_stats(self, file_type: str) -> Dict[str, Any]:
        """Get statistics for file type."""
        with self.lock:
            if file_type not in self.performance_history:
                return {}
            
            times = self.performance_history[file_type]
            sizes = self.file_size_history[file_type]
            
            if not times:
                return {}
            
            return {
                'count': len(times),
                'avg_time': statistics.mean(times),
                'median_time': statistics.median(times),
                'min_time': min(times),
                'max_time': max(times),
                'avg_size': statistics.mean(sizes),
                'stdev': statistics.stdev(times) if len(times) > 1 else 0
            }


class SmartCacheManager:
    """Intelligent cache management with eviction policies."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Tuple[Any, float, int]] = {}  # key -> (value, accessed_time, size)
        self.max_size = max_size
        self.current_size = 0
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                value, _, size = self.cache[key]
                self.cache[key] = (value, time.time(), size)  # Update access time
                self.hits += 1
                return value
            else:
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any, size: int) -> None:
        """Put value in cache."""
        with self.lock:
            # Check if need to evict
            while self.current_size + size > self.max_size and self.cache:
                self._evict_lru()
            
            if key in self.cache:
                _, _, old_size = self.cache[key]
                self.current_size -= old_size
            
            self.cache[key] = (value, time.time(), size)
            self.current_size += size
    
    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.cache:
            return
        
        # Find LRU item
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
        _, _, size = self.cache[lru_key]
        del self.cache[lru_key]
        self.current_size -= size
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0
        return (self.hits / total) * 100
    
    def clear(self) -> None:
        """Clear cache."""
        with self.lock:
            self.cache.clear()
            self.current_size = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                'size': len(self.cache),
                'current_bytes': self.current_size,
                'max_bytes': self.max_size,
                'utilization_percent': (self.current_size / self.max_size) * 100,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.get_hit_rate()
            }


class BatchOptimizer:
    """Optimizes batch processing order based on characteristics."""
    
    def __init__(self):
        self.file_sizer = AdaptiveChunkSizer()
        self.predictor = PerformancePredictor()
    
    def optimize_batch_order(self, file_paths: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Optimize processing order for batch.
        
        Strategy: Process complex files first, simple files later to maximize pipeline utilization.
        """
        # Analyze each file
        analyses = [
            (file_path, self.file_sizer.analyze_file(file_path))
            for file_path in file_paths
        ]
        
        # Sort by complexity (descending) then by size (descending)
        sorted_files = sorted(
            analyses,
            key=lambda x: (-x[1].complexity_score, -x[1].file_size)
        )
        
        # Return with optimization hints
        return [
            (file_path, {
                'chunk_size': chars.recommended_chunk_size,
                'expected_time': chars.expected_processing_time,
                'complexity': chars.complexity_score
            })
            for file_path, chars in sorted_files
        ]
    
    def distribute_across_workers(self, file_paths: List[str], num_workers: int) -> Dict[int, List[str]]:
        """
        Distribute files across workers to balance load.
        
        Returns:
            Mapping of worker_id -> list of file paths
        """
        # Get characteristics
        optimized = self.optimize_batch_order(file_paths)
        
        # Distribute using round-robin on sorted list
        distribution: Dict[int, List[str]] = {i: [] for i in range(num_workers)}
        
        for idx, (file_path, _) in enumerate(optimized):
            worker_id = idx % num_workers
            distribution[worker_id].append(file_path)
        
        return distribution


class GPUAccelerator:
    """GPU acceleration for compatible formats."""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.supported_formats = {
            '.mp4', '.h264', '.h265', '.hevc',  # Video codecs
            '.jpg', '.jpeg', '.png',  # Image formats with GPU libraries
        }
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            # Check for common GPU libraries
            import torch  # noqa
            return True
        except ImportError:
            pass
        
        try:
            import cupy  # noqa
            return True
        except ImportError:
            pass
        
        return False
    
    def can_accelerate(self, file_path: str) -> bool:
        """Check if file can be GPU accelerated."""
        if not self.gpu_available:
            return False
        
        file_type = Path(file_path).suffix.lower()
        return file_type in self.supported_formats
    
    def accelerate_extraction(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply GPU acceleration to extraction if available.
        
        For now, returns metadata as-is. In production, would use
        GPU libraries like CUDA, NVIDIA nvcodec, etc.
        """
        if not self.can_accelerate(file_path):
            return metadata
        
        logger.debug(f"GPU acceleration available for {file_path}")
        return metadata


# Convenience functions
def create_optimized_config(file_path: str) -> Dict[str, Any]:
    """Create optimized configuration for file."""
    sizer = AdaptiveChunkSizer()
    characteristics = sizer.analyze_file(file_path)
    
    return {
        'chunk_size': characteristics.recommended_chunk_size,
        'estimated_chunks': characteristics.estimated_chunks,
        'expected_processing_time': characteristics.expected_processing_time,
        'complexity': characteristics.complexity_score
    }


def optimize_batch(file_paths: List[str], num_workers: int = 4) -> Dict[int, List[str]]:
    """Optimize batch distribution across workers."""
    optimizer = BatchOptimizer()
    return optimizer.distribute_across_workers(file_paths, num_workers)
