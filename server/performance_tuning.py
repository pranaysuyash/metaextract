"""
MetaExtract Performance Tuning Module

This module provides performance optimizations based on real-world usage considerations
and adaptive tuning mechanisms.
"""

import time
import threading
import statistics
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import psutil
import gc
from collections import deque, defaultdict
import asyncio
import concurrent.futures
from pathlib import Path


class PerformanceTier(Enum):
    """Performance tiers based on system resources and usage patterns."""
    DEVELOPMENT = "development"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    MAXIMUM = "maximum"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    operation: str
    duration: float  # in seconds
    memory_before: float  # in MB
    memory_after: float  # in MB
    cpu_usage: float
    timestamp: float
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    success: bool = True


class AdaptiveThreadPool:
    """Thread pool that adapts based on system load and performance metrics."""
    
    def __init__(self, min_workers: int = 2, max_workers: int = 8, 
                 target_load: float = 0.7, adjustment_interval: int = 30):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.target_load = target_load  # Target CPU utilization
        self.adjustment_interval = adjustment_interval  # seconds
        self.current_workers = min_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.current_workers)
        self.metrics_history = deque(maxlen=100)
        self.adjustment_lock = threading.Lock()
        self.last_adjustment = time.time()
        self.running = True
        
        # Start adjustment thread
        self.adjustment_thread = threading.Thread(target=self._adjust_workers, daemon=True)
        self.adjustment_thread.start()
    
    def submit(self, func: Callable, *args, **kwargs):
        """Submit a task to the thread pool."""
        return self.executor.submit(func, *args, **kwargs)
    
    def _adjust_workers(self):
        """Periodically adjust the number of workers based on system load."""
        while self.running:
            time.sleep(self.adjustment_interval)
            
            with self.adjustment_lock:
                if time.time() - self.last_adjustment < self.adjustment_interval:
                    continue
                
                # Get current system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Calculate target worker count based on load
                if cpu_percent < self.target_load * 50 and memory_percent < 70:  # Low load
                    target_workers = min(self.max_workers, self.current_workers + 1)
                elif cpu_percent > self.target_load * 120 or memory_percent > 85:  # High load
                    target_workers = max(self.min_workers, self.current_workers - 1)
                else:  # Stable load
                    target_workers = self.current_workers
                
                # Only adjust if there's a significant change
                if target_workers != self.current_workers:
                    self._resize_executor(target_workers)
                
                self.last_adjustment = time.time()
    
    def _resize_executor(self, new_size: int):
        """Resize the thread pool executor."""
        if new_size == self.current_workers:
            return
        
        # Shutdown current executor and create a new one
        self.executor.shutdown(wait=True)
        self.current_workers = new_size
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.current_workers)
    
    def shutdown(self):
        """Shutdown the thread pool."""
        self.running = False
        self.executor.shutdown(wait=True)


class PerformanceOptimizer:
    """Main performance optimizer that tunes various aspects of the system."""
    
    def __init__(self, tier: PerformanceTier = PerformanceTier.MODERATE):
        self.tier = tier
        self.metrics_collector = PerformanceMetricsCollector()
        self.thread_pool = AdaptiveThreadPool(
            min_workers=self._get_min_workers(tier),
            max_workers=self._get_max_workers(tier),
            target_load=self._get_target_load(tier)
        )
        self.cache_optimizer = CacheOptimizer(tier)
        self.batch_optimizer = BatchProcessingOptimizer(tier)
        self.resource_monitor = ResourceMonitor()
        
        # Performance tuning parameters based on tier
        self.tuning_params = self._get_tuning_parameters(tier)
        
        # Start monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitoring_thread.start()
    
    def _get_min_workers(self, tier: PerformanceTier) -> int:
        """Get minimum number of workers based on tier."""
        tier_workers = {
            PerformanceTier.DEVELOPMENT: 1,
            PerformanceTier.LIGHT: 2,
            PerformanceTier.MODERATE: 4,
            PerformanceTier.HEAVY: 6,
            PerformanceTier.MAXIMUM: 8
        }
        return tier_workers.get(tier, 4)
    
    def _get_max_workers(self, tier: PerformanceTier) -> int:
        """Get maximum number of workers based on tier."""
        tier_workers = {
            PerformanceTier.DEVELOPMENT: 2,
            PerformanceTier.LIGHT: 4,
            PerformanceTier.MODERATE: 8,
            PerformanceTier.HEAVY: 12,
            PerformanceTier.MAXIMUM: 16
        }
        return tier_workers.get(tier, 8)
    
    def _get_target_load(self, tier: PerformanceTier) -> float:
        """Get target system load based on tier."""
        tier_load = {
            PerformanceTier.DEVELOPMENT: 0.5,
            PerformanceTier.LIGHT: 0.6,
            PerformanceTier.MODERATE: 0.7,
            PerformanceTier.HEAVY: 0.8,
            PerformanceTier.MAXIMUM: 0.9
        }
        return tier_load.get(tier, 0.7)
    
    def _get_tuning_parameters(self, tier: PerformanceTier) -> Dict[str, Any]:
        """Get performance tuning parameters based on tier."""
        base_params = {
            'batch_chunk_size': 10,
            'cache_ttl': 3600,
            'cache_max_size': 1000,
            'file_read_buffer_size': 8192,
            'compression_level': 6,
            'gc_threshold_multiplier': 1.0,
            'timeout_multiplier': 1.0
        }
        
        tier_modifiers = {
            PerformanceTier.DEVELOPMENT: {
                'batch_chunk_size': 5,
                'cache_ttl': 1800,
                'cache_max_size': 100,
                'file_read_buffer_size': 4096,
                'compression_level': 1,
                'gc_threshold_multiplier': 0.5,
                'timeout_multiplier': 1.5
            },
            PerformanceTier.LIGHT: {
                'batch_chunk_size': 8,
                'cache_ttl': 2700,
                'cache_max_size': 500,
                'file_read_buffer_size': 6144,
                'compression_level': 3,
                'gc_threshold_multiplier': 0.7,
                'timeout_multiplier': 1.2
            },
            PerformanceTier.MODERATE: base_params.copy(),
            PerformanceTier.HEAVY: {
                'batch_chunk_size': 15,
                'cache_ttl': 7200,
                'cache_max_size': 2000,
                'file_read_buffer_size': 16384,
                'compression_level': 9,
                'gc_threshold_multiplier': 1.5,
                'timeout_multiplier': 0.8
            },
            PerformanceTier.MAXIMUM: {
                'batch_chunk_size': 25,
                'cache_ttl': 14400,
                'cache_max_size': 5000,
                'file_read_buffer_size': 32768,
                'compression_level': 9,
                'gc_threshold_multiplier': 2.0,
                'timeout_multiplier': 0.5
            }
        }
        
        return tier_modifiers.get(tier, base_params)
    
    def _monitor_performance(self):
        """Monitor system performance and adjust settings accordingly."""
        while True:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_usage = psutil.disk_usage('/').percent
                load_average = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else cpu_percent
                
                # Adjust garbage collection threshold based on memory pressure
                if memory_percent > 80:
                    # Increase GC threshold to run less frequently under memory pressure
                    gc.set_threshold(
                        int(gc.get_threshold()[0] * self.tuning_params['gc_threshold_multiplier'] * 1.5),
                        gc.get_threshold()[1],
                        gc.get_threshold()[2]
                    )
                elif memory_percent < 50:
                    # Decrease GC threshold to run more frequently when memory is available
                    gc.set_threshold(
                        int(gc.get_threshold()[0] * self.tuning_params['gc_threshold_multiplier']),
                        gc.get_threshold()[1],
                        gc.get_threshold()[2]
                    )
                
                # Log performance metrics periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.metrics_collector.log_system_metrics({
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'disk_usage': disk_usage,
                        'load_average': load_average,
                        'timestamp': time.time()
                    })
                
                time.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(60)  # Wait longer if there's an error
    
    def optimize_for_file_type(self, file_path: str) -> Dict[str, Any]:
        """Optimize processing parameters based on file type."""
        file_ext = Path(file_path).suffix.lower()
        
        # Default optimization settings
        opt_settings = {
            'buffer_size': self.tuning_params['file_read_buffer_size'],
            'timeout': 300 * self.tuning_params['timeout_multiplier'],  # 5 minutes default
            'compression': self.tuning_params['compression_level'],
            'parallel_processing': True
        }
        
        # Adjust settings based on file type
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            # Image files - may need more memory but faster processing
            opt_settings.update({
                'buffer_size': min(65536, self.tuning_params['file_read_buffer_size'] * 2),
                'timeout': 120 * self.tuning_params['timeout_multiplier'],
                'parallel_processing': True
            })
        elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
            # Video files - need more time and memory
            opt_settings.update({
                'buffer_size': min(131072, self.tuning_params['file_read_buffer_size'] * 4),
                'timeout': 600 * self.tuning_params['timeout_multiplier'],  # 10 minutes
                'parallel_processing': False  # Video processing often sequential
            })
        elif file_ext in ['.pdf']:
            # PDF files - variable processing time
            opt_settings.update({
                'buffer_size': min(32768, self.tuning_params['file_read_buffer_size'] * 2),
                'timeout': 300 * self.tuning_params['timeout_multiplier'],
                'parallel_processing': True
            })
        elif file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            # Office files - moderate processing
            opt_settings.update({
                'buffer_size': self.tuning_params['file_read_buffer_size'],
                'timeout': 240 * self.tuning_params['timeout_multiplier'],
                'parallel_processing': True
            })
        
        return opt_settings
    
    def get_adaptive_batch_size(self, file_paths: List[str]) -> int:
        """Determine optimal batch size based on file characteristics."""
        if not file_paths:
            return self.tuning_params['batch_chunk_size']
        
        # Analyze file characteristics
        total_size = 0
        file_types = set()
        
        for path in file_paths:
            try:
                size = Path(path).stat().st_size
                total_size += size
                file_types.add(Path(path).suffix.lower())
            except:
                continue
        
        avg_size = total_size / len(file_paths) if file_paths else 0
        
        # Adjust batch size based on characteristics
        base_size = self.tuning_params['batch_chunk_size']
        
        if avg_size > 50 * 1024 * 1024:  # Larger than 50MB average
            return max(1, int(base_size * 0.5))  # Smaller batches for large files
        elif avg_size > 10 * 1024 * 1024:  # Larger than 10MB average
            return max(2, int(base_size * 0.7))
        elif len(file_types) > 5:  # Many different file types
            return max(3, int(base_size * 0.8))  # Smaller batches for variety
        else:
            return base_size  # Normal batch size
    
    def tune_gc_settings(self):
        """Tune garbage collection settings based on current system state."""
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > 85:
            # Under high memory pressure, run GC more aggressively
            gc.set_threshold(100, 10, 10)  # Very aggressive GC
        elif memory_percent > 70:
            # Moderate memory pressure
            gc.set_threshold(
                int(gc.get_threshold()[0] * self.tuning_params['gc_threshold_multiplier'] * 0.8),
                gc.get_threshold()[1],
                gc.get_threshold()[2]
            )
        else:
            # Normal conditions
            gc.set_threshold(
                int(gc.get_threshold()[0] * self.tuning_params['gc_threshold_multiplier']),
                gc.get_threshold()[1],
                gc.get_threshold()[2]
            )


class PerformanceMetricsCollector:
    """Collects and analyzes performance metrics."""
    
    def __init__(self):
        self.operation_metrics = defaultdict(list)
        self.system_metrics = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    def record_operation(self, metrics: PerformanceMetrics):
        """Record metrics for an operation."""
        with self.lock:
            self.operation_metrics[metrics.operation].append(metrics)
    
    def get_performance_summary(self, operation: str = None) -> Dict[str, Any]:
        """Get performance summary for operations."""
        with self.lock:
            if operation:
                metrics_list = self.operation_metrics[operation]
            else:
                metrics_list = []
                for op_metrics in self.operation_metrics.values():
                    metrics_list.extend(op_metrics)
            
            if not metrics_list:
                return {}
            
            durations = [m.duration for m in metrics_list]
            memory_changes = [(m.memory_after - m.memory_before) for m in metrics_list]
            success_rates = [float(m.success) for m in metrics_list]
            
            return {
                'operation': operation or 'all',
                'count': len(metrics_list),
                'avg_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'std_dev_duration': statistics.stdev(durations) if len(durations) > 1 else 0,
                'avg_memory_change': statistics.mean(memory_changes),
                'success_rate': statistics.mean(success_rates),
                'total_processing_time': sum(durations)
            }
    
    def log_system_metrics(self, metrics: Dict[str, Any]):
        """Log system metrics."""
        with self.lock:
            self.system_metrics.append(metrics)


class CacheOptimizer:
    """Optimizes cache settings based on usage patterns."""
    
    def __init__(self, tier: PerformanceTier):
        self.tier = tier
        self.access_pattern = defaultdict(int)
        self.hit_rates = defaultdict(float)
        self.size_distribution = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_access(self, key: str, size: int, hit: bool):
        """Record cache access."""
        with self.lock:
            self.access_pattern[key] += 1
            if key in self.hit_rates:
                # Update hit rate with exponential moving average
                self.hit_rates[key] = 0.9 * self.hit_rates[key] + 0.1 * float(hit)
            else:
                self.hit_rates[key] = float(hit)
            
            self.size_distribution[key].append(size)
    
    def get_optimal_cache_settings(self) -> Dict[str, int]:
        """Get optimal cache settings based on access patterns."""
        with self.lock:
            if not self.access_pattern:
                return {
                    'max_size': 1000,
                    'ttl': 3600
                }
            
            # Calculate average size of cached items
            avg_sizes = {}
            for key, sizes in self.size_distribution.items():
                avg_sizes[key] = statistics.mean(sizes) if sizes else 1024
            
            # Determine cache size based on access frequency and hit rates
            total_accesses = sum(self.access_pattern.values())
            weighted_size = 0
            
            for key, count in self.access_pattern.items():
                weight = count / total_accesses
                avg_size = avg_sizes.get(key, 1024)
                hit_rate = self.hit_rates.get(key, 0.5)
                
                # Weight by access frequency and hit rate
                weighted_size += weight * avg_size * (0.5 + hit_rate / 2)  # Emphasize high hit rates
            
            # Adjust based on performance tier
            size_multiplier = {
                PerformanceTier.DEVELOPMENT: 0.5,
                PerformanceTier.LIGHT: 0.8,
                PerformanceTier.MODERATE: 1.0,
                PerformanceTier.HEAVY: 1.5,
                PerformanceTier.MAXIMUM: 2.0
            }.get(self.tier, 1.0)
            
            optimal_size = int(weighted_size * 100 * size_multiplier)  # Arbitrary scaling factor
            optimal_size = max(100, min(optimal_size, 100000))  # Clamp between 100 and 100k
            
            # TTL based on access frequency (more frequent access = longer TTL)
            avg_frequency = total_accesses / len(self.access_pattern) if self.access_pattern else 0
            if avg_frequency > 100:
                ttl = 7200  # 2 hours for very frequent access
            elif avg_frequency > 50:
                ttl = 3600  # 1 hour for frequent access
            elif avg_frequency > 10:
                ttl = 1800  # 30 minutes for moderate access
            else:
                ttl = 900  # 15 minutes for infrequent access
            
            return {
                'max_size': optimal_size,
                'ttl': ttl
            }


class BatchProcessingOptimizer:
    """Optimizes batch processing based on file characteristics."""
    
    def __init__(self, tier: PerformanceTier):
        self.tier = tier
        self.processing_history = []
        self.lock = threading.Lock()
    
    def record_batch_result(self, file_count: int, total_time: float, success_count: int):
        """Record results of a batch processing operation."""
        with self.lock:
            self.processing_history.append({
                'file_count': file_count,
                'total_time': total_time,
                'success_count': success_count,
                'throughput': file_count / total_time if total_time > 0 else 0,
                'success_rate': success_count / file_count if file_count > 0 else 0,
                'timestamp': time.time()
            })
            
            # Keep only recent history (last 100 batches)
            if len(self.processing_history) > 100:
                self.processing_history = self.processing_history[-100:]
    
    def suggest_optimal_batch_size(self) -> int:
        """Suggest optimal batch size based on historical performance."""
        with self.lock:
            if len(self.processing_history) < 5:
                # Not enough data, return default based on tier
                tier_defaults = {
                    PerformanceTier.DEVELOPMENT: 5,
                    PerformanceTier.LIGHT: 8,
                    PerformanceTier.MODERATE: 10,
                    PerformanceTier.HEAVY: 15,
                    PerformanceTier.MAXIMUM: 20
                }
                return tier_defaults.get(self.tier, 10)
            
            # Analyze recent performance
            recent_batches = self.processing_history[-20:]  # Last 20 batches
            
            # Calculate average throughput for different batch sizes
            size_throughput = defaultdict(list)
            for batch in recent_batches:
                size = batch['file_count']
                throughput = batch['throughput']
                size_throughput[size].append(throughput)
            
            # Find batch size with highest average throughput
            best_size = 10
            best_throughput = 0
            
            for size, throughputs in size_throughput.items():
                avg_throughput = statistics.mean(throughputs)
                if avg_throughput > best_throughput:
                    best_throughput = avg_throughput
                    best_size = size
            
            return max(1, min(best_size, 50))  # Clamp between 1 and 50


class ResourceMonitor:
    """Monitors system resources and provides optimization suggestions."""
    
    def __init__(self):
        self.resource_history = deque(maxlen=100)
        self.last_check = time.time()
        self.lock = threading.Lock()
    
    def get_current_resources(self) -> Dict[str, float]:
        """Get current system resource usage."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'timestamp': time.time()
        }
    
    def should_reduce_load(self) -> bool:
        """Check if system load should be reduced."""
        resources = self.get_current_resources()
        
        # Reduce load if any resource is critically high
        return (resources['cpu_percent'] > 90 or 
                resources['memory_percent'] > 90 or 
                resources['disk_usage'] > 95)
    
    def should_increase_load(self) -> bool:
        """Check if system load can be increased."""
        resources = self.get_current_resources()
        
        # Increase load if resources are underutilized
        return (resources['cpu_percent'] < 30 and 
                resources['memory_percent'] < 50 and 
                resources['disk_usage'] < 60)


# Global performance optimizer instance
_performance_optimizer = None
_performance_lock = threading.Lock()


def get_performance_optimizer(tier: PerformanceTier = PerformanceTier.MODERATE) -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        with _performance_lock:
            if _performance_optimizer is None:
                _performance_optimizer = PerformanceOptimizer(tier)
    return _performance_optimizer


def optimize_processing_for_file(file_path: str) -> Dict[str, Any]:
    """Get optimization settings for processing a specific file."""
    optimizer = get_performance_optimizer()
    return optimizer.optimize_for_file_type(file_path)


def get_adaptive_batch_size(file_paths: List[str]) -> int:
    """Get adaptive batch size for processing multiple files."""
    optimizer = get_performance_optimizer()
    return optimizer.get_adaptive_batch_size(file_paths)


def record_performance_metrics(operation: str, duration: float, file_path: str = None, 
                             success: bool = True):
    """Record performance metrics for an operation."""
    # Get memory usage before and after
    memory_before = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    memory_after = memory_before  # Placeholder, in real usage you'd measure before and after
    
    metrics = PerformanceMetrics(
        operation=operation,
        duration=duration,
        memory_before=memory_before,
        memory_after=memory_after,
        cpu_usage=psutil.cpu_percent(),
        timestamp=time.time(),
        file_type=Path(file_path).suffix.lower() if file_path else None,
        success=success
    )
    
    optimizer = get_performance_optimizer()
    optimizer.metrics_collector.record_operation(metrics)


def get_performance_summary(operation: str = None) -> Dict[str, Any]:
    """Get performance summary."""
    optimizer = get_performance_optimizer()
    return optimizer.metrics_collector.get_performance_summary(operation)


def tune_gc_settings():
    """Tune garbage collection settings."""
    optimizer = get_performance_optimizer()
    optimizer.tune_gc_settings()


def record_batch_processing_result(file_count: int, total_time: float, success_count: int):
    """Record results of batch processing for optimization."""
    optimizer = get_performance_optimizer()
    optimizer.batch_optimizer.record_batch_result(file_count, total_time, success_count)


def suggest_optimal_batch_size() -> int:
    """Get suggested optimal batch size."""
    optimizer = get_performance_optimizer()
    return optimizer.batch_optimizer.suggest_optimal_batch_size()


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import os
    
    print("Testing Performance Optimization System...")
    
    # Initialize optimizer
    optimizer = get_performance_optimizer(PerformanceTier.HEAVY)
    
    # Test file type optimization
    print("\n--- File Type Optimization ---")
    test_files = [
        "test.jpg",
        "video.mp4", 
        "document.pdf",
        "spreadsheet.xlsx"
    ]
    
    for file in test_files:
        opts = optimizer.optimize_for_file_type(file)
        print(f"{file}: {opts}")
    
    # Test batch size optimization
    print("\n--- Batch Size Optimization ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files of different sizes
        test_paths = []
        for i in range(10):
            path = os.path.join(tmpdir, f"test_{i}.jpg")
            # Create a file of varying sizes
            size = (i + 1) * 1024 * 1024  # 1MB to 10MB
            with open(path, 'wb') as f:
                f.write(b"x" * size)
            test_paths.append(path)
        
        optimal_batch = optimizer.get_adaptive_batch_size(test_paths)
        print(f"Optimal batch size for {len(test_paths)} files: {optimal_batch}")
    
    # Simulate recording some operations
    print("\n--- Performance Metrics Collection ---")
    for i in range(5):
        # Simulate operation timing
        start_time = time.time()
        time.sleep(0.1)  # Simulate work
        duration = time.time() - start_time
        
        record_performance_metrics(
            operation="metadata_extraction", 
            duration=duration, 
            file_path=f"test_{i}.jpg",
            success=True
        )
    
    # Get performance summary
    summary = get_performance_summary("metadata_extraction")
    print(f"Performance Summary: {summary}")
    
    # Test batch processing optimization
    print("\n--- Batch Processing Optimization ---")
    for i in range(3):
        record_batch_processing_result(file_count=10, total_time=5.0 + i, success_count=10 - i)
    
    suggested_size = suggest_optimal_batch_size()
    print(f"Suggested optimal batch size: {suggested_size}")
    
    print("\nPerformance optimization system initialized and tested!")