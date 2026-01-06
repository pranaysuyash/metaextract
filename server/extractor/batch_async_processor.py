"""
Optimized Batch Async Processor for MetaExtract

Provides batch operation optimization with async processing and caching integration.
This replaces the existing batch_optimization.py with improved performance.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import statistics
from collections import defaultdict
import concurrent.futures
import threading

logger = logging.getLogger(__name__)


class BatchOptimizationStrategy(Enum):
    """Strategies for batch processing optimization."""
    PERFORMANCE_BASED = "performance_based"
    FILE_TYPE_AWARE = "file_type_aware"
    DYNAMIC_ADJUSTMENT = "dynamic_adjustment"
    HYBRID_ASYNC = "hybrid_async"


@dataclass
class BatchProcessingMetrics:
    """Metrics for batch processing operations."""
    batch_id: str
    file_count: int
    total_size_bytes: int
    start_time: float
    end_time: Optional[float] = None
    successful_count: int = 0
    failed_count: int = 0
    cache_hits: int = 0
    processing_times: List[float] = field(default_factory=list)
    file_types: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def avg_processing_time(self) -> float:
        return statistics.mean(self.processing_times) if self.processing_times else 0
    
    @property
    def throughput_files_per_sec(self) -> float:
        return self.file_count / self.duration if self.duration > 0 else 0
    
    @property
    def success_rate(self) -> float:
        if self.file_count == 0:
            return 0
        return (self.successful_count / self.file_count) * 100


@dataclass
class BatchOptimizationConfig:
    """Configuration for batch processing optimization."""
    max_concurrent_tasks: int = 10
    chunk_size: int = 10
    adaptive_sizing: bool = True
    performance_based_scheduling: bool = True
    file_type_grouping: bool = True
    enable_caching: bool = True
    enable_connection_pooling: bool = True
    retry_failed: bool = True
    retry_limit: int = 3
    timeout_per_file: int = 300
    batch_timeout: int = 3600  # 1 hour
    memory_efficient: bool = True
    progress_callback: Optional[Callable] = None


class AsyncBatchOptimizer:
    """Async-based batch processing optimizer with performance tracking."""
    
    def __init__(self, config: Optional[BatchOptimizationConfig] = None):
        self.config = config or BatchOptimizationConfig()
        self.processing_history: List[BatchProcessingMetrics] = []
        self.file_type_performance: Dict[str, List[float]] = defaultdict(list)
        self.size_performance: List[Tuple[int, float]] = []  # (size, time)
        self.lock = asyncio.Lock()
        self._cache_manager = None
        
    def record_batch_metrics(self, metrics: BatchProcessingMetrics):
        """Record batch processing metrics for optimization."""
        with self.lock:
            self.processing_history.append(metrics)
            
            # Record performance by file type
            for file_type in set(metrics.file_types):
                if metrics.processing_times:
                    avg_time = statistics.mean(metrics.processing_times)
                    self.file_type_performance[file_type].append(avg_time)
            
            # Record size-performance data
            if metrics.file_count > 0:
                avg_size = metrics.total_size_bytes / metrics.file_count
                avg_time = metrics.avg_processing_time
                self.size_performance.append((avg_size, avg_time))
    
    def get_optimal_concurrent_tasks(self, file_paths: List[str]) -> int:
        """Determine optimal number of concurrent tasks."""
        if not file_paths:
            return self.config.max_concurrent_tasks
        
        # Analyze file characteristics
        file_types = []
        total_size = 0
        
        for path in file_paths:
            try:
                size = Path(path).stat().st_size
                total_size += size
                suffix = Path(path).suffix.lower()
                file_types.append(suffix)
            except:
                file_types.append("unknown")
        
        # Calculate average file size
        avg_size = total_size / len(file_paths) if file_paths else 0
        
        # Adjust concurrent tasks based on performance history
        with self.lock:
            # If we have performance data for these file types, adjust accordingly
            avg_times_by_type = {}
            for ftype in set(file_types):
                times = self.file_type_performance.get(ftype, [])
                if times:
                    avg_times_by_type[ftype] = statistics.mean(times)
            
            # Calculate expected processing time
            expected_total_time = 0
            for ftype in file_types:
                avg_time = avg_times_by_type.get(ftype, 2.0)  # Default to 2 seconds
                expected_total_time += avg_time
            
            # Adjust concurrent tasks based on expected time and memory constraints
            if avg_size > 10 * 1024 * 1024:  # Large files > 10MB
                # Use fewer concurrent tasks for large files
                optimal_tasks = max(2, min(5, self.config.max_concurrent_tasks))
            elif expected_total_time > 60:  # Long processing time
                # Use more concurrent tasks for long batches
                optimal_tasks = min(self.config.max_concurrent_tasks, len(file_paths))
            elif expected_total_time < 10:  # Quick processing
                # Use moderate number of concurrent tasks
                optimal_tasks = min(self.config.max_concurrent_tasks // 2, len(file_paths))
            else:
                # Default optimization
                optimal_tasks = min(self.config.max_concurrent_tasks, max(4, len(file_paths) // 2))
        
        return max(1, min(optimal_tasks, self.config.max_concurrent_tasks))
    
    def group_files_by_characteristics(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group files by characteristics for optimized processing."""
        groups = defaultdict(list)
        
        for path in file_paths:
            try:
                path_obj = Path(path)
                file_type = path_obj.suffix.lower()
                size = path_obj.stat().st_size
                
                # Create groups based on file type and size
                if size > 10 * 1024 * 1024:  # Large files
                    group_key = f"{file_type}_large"
                elif size > 1024 * 1024:  # Medium files
                    group_key = f"{file_type}_medium"
                else:  # Small files
                    group_key = f"{file_type}_small"
                
                groups[group_key].append(path)
                
            except Exception:
                groups["unknown"].append(path)
        
        return dict(groups)
    
    def optimize_batch_processing(self, file_paths: List[str]) -> Dict[str, Any]:
        """Generate optimization plan for batch processing."""
        with self.lock:
            # Determine optimal configuration
            optimal_concurrent = self.get_optimal_concurrent_tasks(file_paths)
            file_groups = self.group_files_by_characteristics(file_paths)
            
            # Calculate estimated processing time
            estimated_time = 0
            for path in file_paths:
                try:
                    size = Path(path).stat().st_size
                    suffix = Path(path).suffix.lower()
                    estimated_time += self._estimate_processing_time(size, suffix)
                except:
                    estimated_time += 2.0  # Default estimate
            
            optimization_plan = {
                "optimal_concurrent_tasks": optimal_concurrent,
                "file_groups": file_groups,
                "chunk_size": self.config.chunk_size,
                "strategy": "hybrid_async",
                "estimated_processing_time": estimated_time / optimal_concurrent if optimal_concurrent > 0 else estimated_time,
                "total_files": len(file_paths),
                "enable_caching": self.config.enable_caching,
                "enable_connection_pooling": self.config.enable_connection_pooling
            }
            
            return optimization_plan
    
    def _estimate_processing_time(self, file_size: int, file_type: str) -> float:
        """Estimate processing time based on historical data."""
        with self.lock:
            # Start with base time
            estimated_time = 1.0
            
            # Adjust based on file size
            if self.size_performance:
                similar_files = [
                    (size, time) for size, time in self.size_performance
                    if abs(size - file_size) < file_size * 0.5
                ]
                
                if similar_files:
                    avg_time = statistics.mean([t for _, t in similar_files])
                    estimated_time = avg_time
            
            # Adjust based on file type performance
            if file_type in self.file_type_performance:
                type_times = self.file_type_performance[file_type]
                if type_times:
                    type_avg = statistics.mean(type_times)
                    estimated_time = (estimated_time + type_avg) / 2
            
            return max(estimated_time, 0.1)


class OptimizedAsyncBatchProcessor:
    """Main batch processor with async optimization capabilities."""
    
    def __init__(self, config: Optional[BatchOptimizationConfig] = None):
        self.optimizer = AsyncBatchOptimizer(config)
        self.config = config or BatchOptimizationConfig()
        self._cache_manager = None
        
    async def initialize(self):
        """Initialize the batch processor."""
        # Initialize cache manager if caching is enabled
        if self.config.enable_caching:
            try:
                from server.cache.cache_manager import get_cache_manager
                self._cache_manager = get_cache_manager()
            except ImportError:
                logger.warning("Cache manager not available, disabling caching")
                self.config.enable_caching = False
    
    def _check_cache(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Check if result is cached."""
        if not self.config.enable_caching or not self._cache_manager:
            return None
        
        try:
            return self._cache_manager.get_extraction_result(file_path, "batch")
        except Exception as e:
            logger.debug(f"Cache check failed for {file_path}: {e}")
            return None
    
    def _cache_result(self, result: Dict[str, Any], file_path: str, processing_time: float):
        """Cache extraction result."""
        if not self.config.enable_caching or not self._cache_manager:
            return
        
        try:
            file_format = Path(file_path).suffix.lower()
            self._cache_manager.cache_extraction_result(
                result, file_path, "batch", file_format, processing_time
            )
        except Exception as e:
            logger.debug(f"Failed to cache result for {file_path}: {e}")
    
    async def process_batch_optimized_async(
        self, 
        file_paths: List[str], 
        processing_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Process a batch of files with async optimization."""
        start_time = time.time()
        batch_id = f"batch_{int(start_time * 1000)}"
        
        # Initialize if needed
        await self.initialize()
        
        # Get optimization plan
        optimization_plan = self.optimizer.optimize_batch_processing(file_paths)
        logger.info(f"Batch optimization plan: {optimization_plan}")
        
        # Apply optimization plan
        concurrent_tasks = optimization_plan["optimal_concurrent_tasks"]
        file_groups = optimization_plan["file_groups"]
        
        # Process files with optimized configuration
        all_results = {}
        total_successful = 0
        total_failed = 0
        total_cache_hits = 0
        processing_times = []
        file_types = []
        total_size = 0
        
        # Process each file group
        for group_name, group_files in file_groups.items():
            logger.info(f"Processing group {group_name} with {len(group_files)} files")
            
            # Check cache first
            uncached_files = []
            cached_results = {}
            
            for file_path in group_files:
                cached_result = self._check_cache(file_path)
                if cached_result:
                    cached_results[file_path] = cached_result
                    total_cache_hits += 1
                else:
                    uncached_files.append(file_path)
            
            # Process uncached files
            if uncached_files:
                group_results = await self._process_file_group_async(
                    uncached_files, processing_func, concurrent_tasks, *args, **kwargs
                )
                
                # Cache successful results
                for file_path, result in group_results.items():
                    if result.get("success", False):
                        processing_time = result.get("processing_time", 0)
                        self._cache_result(result, file_path, processing_time)
                        total_successful += 1
                    else:
                        total_failed += 1
                        processing_times.append(result.get("processing_time", 0))
                    
                    file_types.append(Path(file_path).suffix.lower())
                    try:
                        total_size += Path(file_path).stat().st_size
                    except:
                        pass
                
                all_results.update(group_results)
            
            # Add cached results
            all_results.update(cached_results)
            total_successful += len(cached_results)
        
        total_time = time.time() - start_time
        
        # Record metrics
        metrics = BatchProcessingMetrics(
            batch_id=batch_id,
            file_count=len(file_paths),
            total_size_bytes=total_size,
            start_time=start_time,
            end_time=time.time(),
            successful_count=total_successful,
            failed_count=total_failed,
            cache_hits=total_cache_hits,
            processing_times=processing_times,
            file_types=file_types
        )
        
        self.optimizer.record_batch_metrics(metrics)
        
        return {
            "results": all_results,
            "successful_count": total_successful,
            "failed_count": total_failed,
            "cache_hits": total_cache_hits,
            "total_count": len(file_paths),
            "processing_time": total_time,
            "optimization_plan": optimization_plan,
            "throughput": len(file_paths) / total_time if total_time > 0 else 0,
            "metrics": metrics
        }
    
    async def _process_file_group_async(
        self,
        file_paths: List[str],
        processing_func: Callable,
        concurrent_tasks: int,
        *args,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """Process a group of files asynchronously."""
        results = {}
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_tasks)
        
        # Create tasks
        async def process_single_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
            async with semaphore:
                start_time = time.time()
                try:
                    # Execute processing function
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, processing_func, file_path, *args, **kwargs
                    )
                    
                    processing_time = time.time() - start_time
                    
                    # Ensure result has required structure
                    if isinstance(result, dict):
                        result["success"] = True
                        result["processing_time"] = processing_time
                        result["file_path"] = file_path
                    else:
                        result = {
                            "success": True,
                            "processing_time": processing_time,
                            "file_path": file_path,
                            "data": result
                        }
                    
                    return file_path, result
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    error_result = {
                        "success": False,
                        "processing_time": processing_time,
                        "file_path": file_path,
                        "error": str(e)
                    }
                    logger.error(f"Error processing {file_path}: {e}")
                    return file_path, error_result
        
        # Process all files concurrently
        tasks = [process_single_file(file_path) for file_path in file_paths]
        completed_tasks = await asyncio.gather(*tasks)
        
        # Collect results
        for file_path, result in completed_tasks:
            results[file_path] = result
            
            # Call progress callback if provided
            if self.config.progress_callback:
                try:
                    self.config.progress_callback(file_path, result)
                except Exception as e:
                    logger.warning(f"Progress callback failed: {e}")
        
        return results
    
    async def process_batch_by_type_async(
        self, 
        file_paths: List[str], 
        processing_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Process files grouped by type for better resource utilization."""
        # Group files by type
        type_groups = self.optimizer.group_files_by_characteristics(file_paths)
        
        all_results = {}
        total_successful = 0
        total_failed = 0
        total_cache_hits = 0
        processing_times = []
        
        start_time = time.time()
        
        # Process each type group
        for group_name, group_files in type_groups.items():
            logger.info(f"Processing {group_name} group with {len(group_files)} files")
            
            # Process group
            group_result = await self.process_batch_optimized_async(
                group_files, processing_func, *args, **kwargs
            )
            
            all_results.update(group_result['results'])
            total_successful += group_result['successful_count']
            total_failed += group_result['failed_count']
            total_cache_hits += group_result['cache_hits']
            
            if 'metrics' in group_result:
                processing_times.extend(group_result['metrics'].processing_times)
        
        total_time = time.time() - start_time
        
        return {
            'results': all_results,
            'successful_count': total_successful,
            'failed_count': total_failed,
            'cache_hits': total_cache_hits,
            'total_count': len(file_paths),
            'processing_time': total_time,
            'throughput': len(file_paths) / total_time if total_time > 0 else 0,
            'type_groups_processed': len(type_groups),
            'processing_times': processing_times
        }


# Global batch processor instance
_global_batch_processor: Optional[OptimizedAsyncBatchProcessor] = None
_global_batch_processor_lock = asyncio.Lock()


async def get_global_batch_processor(config: Optional[BatchOptimizationConfig] = None) -> OptimizedAsyncBatchProcessor:
    """Get the global batch processor instance."""
    global _global_batch_processor
    
    if _global_batch_processor is None:
        async with _global_batch_processor_lock:
            if _global_batch_processor is None:
                _global_batch_processor = OptimizedAsyncBatchProcessor(config)
                await _global_batch_processor.initialize()
    
    return _global_batch_processor


async def process_batch_optimized_async(
    file_paths: List[str], 
    processing_func: Callable,
    config: Optional[BatchOptimizationConfig] = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to process a batch with async optimization."""
    processor = await get_global_batch_processor(config)
    return await processor.process_batch_optimized_async(file_paths, processing_func, *args, **kwargs)


async def process_batch_by_type_async(
    file_paths: List[str], 
    processing_func: Callable,
    config: Optional[BatchOptimizationConfig] = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to process a batch grouped by file type with async optimization."""
    processor = await get_global_batch_processor(config)
    return await processor.process_batch_by_type_async(file_paths, processing_func, *args, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import os
    
    async def test_async_batch_processor():
        """Test the async batch processor."""
        
        print("Testing async batch processor...")
        
        # Create test files
        test_files = []
        for i in range(10):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg', prefix=f'test_{i}_') as f:
                f.write(f"Test image content {i}" * 100)
                test_files.append(f.name)
        
        # Add some different file types
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf', prefix=f'doc_{i}_') as f:
                f.write(f"Test PDF content {i}" * 200)
                test_files.append(f.name)
        
        try:
            # Mock processing function
            def mock_processing_func(filepath, **kwargs):
                import time
                import random
                
                # Simulate processing time based on file type
                if filepath.endswith('.pdf'):
                    processing_time = random.uniform(0.2, 0.5)
                else:
                    processing_time = random.uniform(0.1, 0.3)
                
                time.sleep(processing_time)
                
                return {
                    'file': filepath,
                    'size': os.path.getsize(filepath),
                    'processing_time': processing_time,
                    'success': True
                }
            
            print(f"Processing {len(test_files)} test files...")
            
            # Process with async optimization
            result = await process_batch_optimized_async(
                test_files, 
                mock_processing_func,
                enable_caching=False  # Disable caching for testing
            )
            
            print(f"Results:")
            print(f"  Successful: {result['successful_count']}")
            print(f"  Failed: {result['failed_count']}")
            print(f"  Cache hits: {result['cache_hits']}")
            print(f"  Total time: {result['processing_time']:.2f}s")
            print(f"  Throughput: {result['throughput']:.2f} files/s")
            print(f"  Optimization plan: {result['optimization_plan']}")
            
            # Process by type
            print(f"\nProcessing by file type...")
            result_by_type = await process_batch_by_type_async(
                test_files,
                mock_processing_func,
                enable_caching=False
            )
            
            print(f"Results by type:")
            print(f"  Successful: {result_by_type['successful_count']}")
            print(f"  Failed: {result_by_type['failed_count']}")
            print(f"  Total time: {result_by_type['processing_time']:.2f}s")
            print(f"  Throughput: {result_by_type['throughput']:.2f} files/s")
            print(f"  Type groups processed: {result_by_type['type_groups_processed']}")
            
        finally:
            # Clean up test files
            for file_path in test_files:
                try:
                    os.unlink(file_path)
                except:
                    pass
    
    # Run the test
    asyncio.run(test_async_batch_processor())