"""
MetaExtract Batch Processing Optimization

This module optimizes batch processing based on performance insights and monitoring data.
"""

import asyncio
import time
import threading
from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
from collections import defaultdict
import statistics
from datetime import datetime, timedelta


class BatchOptimizationStrategy(Enum):
    """Different strategies for batch processing optimization."""
    PERFORMANCE_BASED = "performance_based"
    FILE_TYPE_AWARE = "file_type_aware"
    DYNAMIC_ADJUSTMENT = "dynamic_adjustment"
    HYBRID = "hybrid"


@dataclass
class ProcessingMetrics:
    """Metrics for a single file processing operation."""
    filepath: str
    processing_time: float  # in seconds
    success: bool
    file_size: int
    file_type: str
    tier: str
    timestamp: float
    error_type: Optional[str] = None


@dataclass
class BatchOptimizationConfig:
    """Configuration for batch processing optimization."""
    max_workers: int = 4
    chunk_size: int = 10
    adaptive_sizing: bool = True
    performance_based_scheduling: bool = True
    file_type_grouping: bool = True
    retry_failed: bool = True
    retry_limit: int = 3
    timeout_per_file: int = 300  # 5 minutes per file


class BatchOptimizer:
    """Optimizes batch processing based on performance insights."""
    
    def __init__(self, config: Optional[BatchOptimizationConfig] = None):
        self.config = config or BatchOptimizationConfig()
        self.processing_history: List[ProcessingMetrics] = []
        self.file_type_performance: Dict[str, List[float]] = defaultdict(list)
        self.tier_performance: Dict[str, List[float]] = defaultdict(list)
        self.size_performance: List[Tuple[int, float]] = []  # (size, time)
        self.lock = threading.RLock()
        self.optimization_strategy = BatchOptimizationStrategy.HYBRID
    
    def record_processing_result(self, metrics: ProcessingMetrics):
        """Record the result of a processing operation for optimization."""
        with self.lock:
            self.processing_history.append(metrics)
            
            # Record performance by file type
            if metrics.success:
                self.file_type_performance[metrics.file_type].append(metrics.processing_time)
                self.tier_performance[metrics.tier].append(metrics.processing_time)
                self.size_performance.append((metrics.file_size, metrics.processing_time))
    
    def get_optimal_workers_count(self, file_paths: List[str]) -> int:
        """Determine optimal number of workers based on file characteristics."""
        if not file_paths:
            return self.config.max_workers
        
        # Analyze file types in the batch
        file_types = []
        total_size = 0
        
        for path in file_paths:
            try:
                size = Path(path).stat().st_size
                total_size += size
                # Determine file type
                suffix = Path(path).suffix.lower()
                file_types.append(suffix)
            except:
                file_types.append("unknown")
        
        # Calculate average file size
        avg_size = total_size / len(file_paths) if file_paths else 0
        
        # Adjust worker count based on performance history
        with self.lock:
            # If we have performance data for these file types, adjust accordingly
            avg_times_by_type = {}
            for ftype in set(file_types):
                times = self.file_type_performance.get(ftype, [])
                if times:
                    avg_times_by_type[ftype] = statistics.mean(times)
            
            # Calculate expected processing time based on historical data
            expected_total_time = 0
            for ftype in file_types:
                avg_time = avg_times_by_type.get(ftype, 10.0)  # Default to 10 seconds
                expected_total_time += avg_time
            
            # Adjust workers based on expected time and desired parallelism
            if expected_total_time > 60:  # If batch is expected to take more than 1 minute
                # Use more workers for longer batches
                optimal_workers = min(self.config.max_workers, len(file_paths))
            elif expected_total_time < 10:  # If batch is expected to be quick
                # Use fewer workers to avoid overhead
                optimal_workers = max(1, min(2, len(file_paths)))
            else:
                # Use moderate number of workers
                optimal_workers = min(self.config.max_workers, max(2, len(file_paths) // 2))
        
        return max(1, min(optimal_workers, self.config.max_workers))
    
    def sort_files_by_complexity(self, file_paths: List[str]) -> List[str]:
        """Sort files by expected processing complexity (slowest first)."""
        if not self.processing_history:
            return file_paths  # No optimization data available
        
        # Create a mapping of file path to estimated processing time
        file_estimates = {}
        
        for path in file_paths:
            try:
                size = Path(path).stat().st_size
                suffix = Path(path).suffix.lower()
                
                # Estimate processing time based on historical data
                estimated_time = self._estimate_processing_time(size, suffix)
                file_estimates[path] = estimated_time
            except:
                file_estimates[path] = 10.0  # Default estimate
        
        # Sort by estimated processing time (descending - slowest first)
        sorted_files = sorted(file_paths, key=lambda x: file_estimates[x], reverse=True)
        return sorted_files
    
    def _estimate_processing_time(self, file_size: int, file_type: str) -> float:
        """Estimate processing time based on historical data."""
        with self.lock:
            # Start with base time
            estimated_time = 1.0
            
            # Adjust based on file size (if we have size-performance data)
            if self.size_performance:
                # Find similar sized files
                similar_files = [
                    (size, time) for size, time in self.size_performance
                    if abs(size - file_size) < file_size * 0.5  # Within 50% size range
                ]
                
                if similar_files:
                    avg_time = statistics.mean([t for _, t in similar_files])
                    estimated_time = avg_time
                else:
                    # Use general trend if available
                    if len(self.size_performance) > 10:
                        # Calculate size-to-time ratio
                        avg_size = statistics.mean([s for s, _ in self.size_performance])
                        avg_time = statistics.mean([t for _, t in self.size_performance])
                        size_ratio = file_size / max(avg_size, 1)
                        estimated_time = avg_time * size_ratio
            
            # Adjust based on file type performance
            if file_type in self.file_type_performance:
                type_times = self.file_type_performance[file_type]
                if type_times:
                    type_avg = statistics.mean(type_times)
                    estimated_time = (estimated_time + type_avg) / 2  # Average with type-specific time
            
            return max(estimated_time, 0.1)  # Minimum 0.1 seconds
    
    def group_files_by_type(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group files by type for optimized processing."""
        groups = defaultdict(list)
        
        for path in file_paths:
            suffix = Path(path).suffix.lower()
            groups[suffix].append(path)
        
        return dict(groups)
    
    def optimize_batch_processing(self, file_paths: List[str]) -> Dict[str, Any]:
        """Generate optimization plan for batch processing."""
        with self.lock:
            # Determine optimal configuration
            optimal_workers = self.get_optimal_workers_count(file_paths)
            sorted_files = self.sort_files_by_complexity(file_paths)
            
            optimization_plan = {
                'optimal_workers': optimal_workers,
                'file_order': sorted_files,
                'grouped_by_type': self.group_files_by_type(file_paths),
                'strategy': self.optimization_strategy.value,
                'estimated_processing_time': sum(
                    self._estimate_processing_time(Path(f).stat().st_size, Path(f).suffix.lower())
                    for f in file_paths
                ) / optimal_workers if optimal_workers > 0 else 0
            }
            
            return optimization_plan


class OptimizedBatchProcessor:
    """Main batch processor with optimization capabilities."""
    
    def __init__(self, config: Optional[BatchOptimizationConfig] = None):
        self.optimizer = BatchOptimizer(config)
        self.executor = concurrent.futures.ThreadPoolExecutor()
    
    def process_batch_optimized(
        self, 
        file_paths: List[str], 
        processing_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Process a batch of files with optimization."""
        start_time = time.time()
        
        # Get optimization plan
        optimization_plan = self.optimizer.optimize_batch_processing(file_paths)
        
        # Apply optimization plan
        workers = optimization_plan['optimal_workers']
        ordered_files = optimization_plan['file_order']
        
        # Process files with optimized configuration
        results = {}
        failed_files = []
        successful_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(processing_func, file_path, *args, **kwargs): file_path 
                for file_path in ordered_files
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result(timeout=self.optimizer.config.timeout_per_file)
                    results[file_path] = result
                    successful_count += 1
                    
                    # Record successful processing for future optimization
                    try:
                        file_size = Path(file_path).stat().st_size
                        file_type = Path(file_path).suffix.lower()
                        processing_time = time.time() - start_time  # This is approximate
                        
                        metrics = ProcessingMetrics(
                            filepath=file_path,
                            processing_time=processing_time,
                            success=True,
                            file_size=file_size,
                            file_type=file_type,
                            tier=kwargs.get('tier', 'unknown'),
                            timestamp=time.time()
                        )
                        self.optimizer.record_processing_result(metrics)
                    except:
                        pass  # Don't let recording metrics break the processing
                        
                except Exception as e:
                    error_type = type(e).__name__
                    results[file_path] = {'error': str(e), 'error_type': error_type}
                    failed_files.append(file_path)
                    
                    # Record failed processing
                    try:
                        file_size = Path(file_path).stat().st_size
                        file_type = Path(file_path).suffix.lower()
                        
                        metrics = ProcessingMetrics(
                            filepath=file_path,
                            processing_time=0,  # Failed quickly or took too long
                            success=False,
                            file_size=file_size,
                            file_type=file_type,
                            tier=kwargs.get('tier', 'unknown'),
                            timestamp=time.time(),
                            error_type=error_type
                        )
                        self.optimizer.record_processing_result(metrics)
                    except:
                        pass  # Don't let recording metrics break the processing
        
        total_time = time.time() - start_time
        
        return {
            'results': results,
            'successful_count': successful_count,
            'failed_count': len(failed_files),
            'total_count': len(file_paths),
            'processing_time': total_time,
            'optimization_plan': optimization_plan,
            'throughput': len(file_paths) / total_time if total_time > 0 else 0,
            'failed_files': failed_files
        }
    
    def process_batch_by_type(
        self, 
        file_paths: List[str], 
        processing_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Process files grouped by type for better resource utilization."""
        # Group files by type
        type_groups = self.optimizer.group_files_by_type(file_paths)
        
        all_results = {}
        total_successful = 0
        total_failed = 0
        failed_files = []
        
        start_time = time.time()
        
        for file_type, type_files in type_groups.items():
            # Optimize processing for this specific type group
            group_result = self.process_batch_optimized(
                type_files, 
                processing_func, 
                *args, 
                **kwargs
            )
            
            all_results.update(group_result['results'])
            total_successful += group_result['successful_count']
            total_failed += group_result['failed_count']
            failed_files.extend(group_result['failed_files'])
        
        total_time = time.time() - start_time
        
        return {
            'results': all_results,
            'successful_count': total_successful,
            'failed_count': total_failed,
            'total_count': len(file_paths),
            'processing_time': total_time,
            'throughput': len(file_paths) / total_time if total_time > 0 else 0,
            'failed_files': failed_files,
            'type_groups_processed': len(type_groups)
        }


# Global batch processor instance
_batch_processor = None
_batch_processor_lock = threading.Lock()


def get_batch_processor(config: Optional[BatchOptimizationConfig] = None) -> OptimizedBatchProcessor:
    """Get the global batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        with _batch_processor_lock:
            if _batch_processor is None:
                _batch_processor = OptimizedBatchProcessor(config)
    return _batch_processor


def process_batch_optimized(
    file_paths: List[str], 
    processing_func: Callable,
    config: Optional[BatchOptimizationConfig] = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to process a batch with optimization."""
    processor = get_batch_processor(config)
    return processor.process_batch_optimized(file_paths, processing_func, *args, **kwargs)


def process_batch_by_type(
    file_paths: List[str], 
    processing_func: Callable,
    config: Optional[BatchOptimizationConfig] = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to process a batch grouped by file type."""
    processor = get_batch_processor(config)
    return processor.process_batch_by_type(file_paths, processing_func, *args, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import os
    
    print("Testing batch processing optimization...")
    
    # Create some test files
    test_files = []
    for i in range(5):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg', prefix=f'test_{i}_') as f:
            f.write(f"Test image content {i}" * 100)  # Varying sizes
            test_files.append(f.name)
    
    # Add some different file types
    for i in range(2):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf', prefix=f'doc_{i}_') as f:
            f.write(f"Test PDF content {i}" * 200)
            test_files.append(f.name)
    
    try:
        # Create a mock processing function
        def mock_processing_func(filepath, **kwargs):
            import time
            import random
            
            # Simulate processing time based on file size
            size = os.path.getsize(filepath)
            # Simulate processing time: 0.1s + size/100000 seconds + some randomness
            processing_time = 0.1 + (size / 100000.0) + random.uniform(0.05, 0.2)
            time.sleep(processing_time)
            
            return {
                'file': filepath,
                'size': size,
                'processing_time': processing_time,
                'success': True
            }
        
        print(f"Processing {len(test_files)} test files...")
        
        # Process with optimization
        result = process_batch_optimized(
            test_files, 
            mock_processing_func,
            tier="premium"
        )
        
        print(f"Results:")
        print(f"  Successful: {result['successful_count']}")
        print(f"  Failed: {result['failed_count']}")
        print(f"  Total time: {result['processing_time']:.2f}s")
        print(f"  Throughput: {result['throughput']:.2f} files/s")
        print(f"  Optimization plan: {result['optimization_plan']}")
        
        # Process by type
        print(f"\nProcessing by file type...")
        result_by_type = process_batch_by_type(
            test_files,
            mock_processing_func,
            tier="premium"
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