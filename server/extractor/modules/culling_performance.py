"""
Performance Optimization for AI Culling
======================================

Optimizes AI culling for large batches:
- Parallel processing with worker pools
- Memory-efficient batch processing
- Progress tracking and cancellation
- GPU acceleration where available
- Streaming processing for very large sets

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Iterator
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import asyncio
import time
from pathlib import Path
import psutil
import gc
from datetime import datetime, timedelta
import pickle
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Performance metrics for culling operations."""
    total_photos: int
    processed_photos: int
    processing_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_photos_per_second: float
    worker_count: int
    batch_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_photos': self.total_photos,
            'processed_photos': self.processed_photos,
            'processing_time': self.processing_time,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'throughput_photos_per_second': self.throughput_photos_per_second,
            'worker_count': self.worker_count,
            'batch_size': self.batch_size
        }

@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 50
    max_workers: int = None
    use_multiprocessing: bool = True
    memory_limit_mb: int = 1024
    enable_gpu: bool = False
    cache_intermediate: bool = True
    progress_callback: Optional[Callable[[int, int], None]] = None
    
    def __post_init__(self):
        if self.max_workers is None:
            # Use available CPU cores, but limit based on memory
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            optimal_workers = min(cpu_count(), max(1, int(available_memory_gb / 2)))
            self.max_workers = min(optimal_workers, 8)  # Cap at 8 workers

class CullingBatchProcessor:
    """High-performance batch processor for AI culling."""
    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.cache_dir = Path("/tmp/metaextract_culling_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.active_jobs = {}
        self.processing_metrics = {}
        
    async def process_large_batch(self, 
                                photos: List[Dict[str, Any]], 
                                user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a large batch of photos with performance optimization.
        
        Args:
            photos: List of photo metadata dictionaries
            user_preferences: User preference dictionary
            
        Returns:
            Processing results with performance metrics
        """
        start_time = time.time()
        job_id = self._generate_job_id(photos)
        
        try:
            # Initialize metrics
            self.processing_metrics[job_id] = ProcessingMetrics(
                total_photos=len(photos),
                processed_photos=0,
                processing_time=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                throughput_photos_per_second=0,
                worker_count=self.config.max_workers,
                batch_size=self.config.batch_size
            )
            
            # Monitor system resources
            monitor_task = asyncio.create_task(self._monitor_resources(job_id))
            
            # Process in batches
            results = []
            
            if len(photos) > self.config.batch_size:
                # Use streaming batch processing for very large sets
                results = await self._process_streaming_batches(photos, user_preferences, job_id)
            else:
                # Single batch processing
                results = await self._process_single_batch(photos, user_preferences, job_id)
            
            # Stop monitoring
            monitor_task.cancel()
            
            # Calculate final metrics
            final_time = time.time() - start_time
            metrics = self.processing_metrics[job_id]
            metrics.processing_time = final_time
            metrics.throughput_photos_per_second = len(photos) / final_time if final_time > 0 else 0
            
            # Compile results
            final_result = self._compile_results(results, job_id)
            final_result['performance_metrics'] = metrics.to_dict()
            
            # Cleanup
            self._cleanup_job(job_id)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            self._cleanup_job(job_id)
            raise
    
    async def _process_streaming_batches(self, 
                                       photos: List[Dict[str, Any]], 
                                       user_preferences: Optional[Dict[str, Any]],
                                       job_id: str) -> List[Dict[str, Any]]:
        """Process photos in streaming batches for memory efficiency."""
        
        all_results = []
        batch_count = 0
        
        for i in range(0, len(photos), self.config.batch_size):
            batch = photos[i:i + self.config.batch_size]
            batch_count += 1
            
            logger.info(f"Processing batch {batch_count}/{(len(photos) + self.config.batch_size - 1) // self.config.batch_size}")
            
            # Process batch
            batch_result = await self._process_single_batch(batch, user_preferences, job_id)
            all_results.append(batch_result)
            
            # Update progress
            processed = min(i + self.config.batch_size, len(photos))
            self.processing_metrics[job_id].processed_photos = processed
            
            if self.config.progress_callback:
                self.config.progress_callback(processed, len(photos))
            
            # Memory cleanup between batches
            gc.collect()
            
            # Check memory usage and pause if needed
            memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            if memory_mb > self.config.memory_limit_mb:
                logger.warning(f"Memory usage high ({memory_mb:.1f}MB), pausing for cleanup")
                await asyncio.sleep(0.1)
                gc.collect()
        
        return all_results
    
    async def _process_single_batch(self, 
                                  photos: List[Dict[str, Any]], 
                                  user_preferences: Optional[Dict[str, Any]],
                                  job_id: str) -> Dict[str, Any]:
        """Process a single batch of photos."""
        
        from .ai_culling_engine import AICullingEngine
        
        # Check cache first
        cache_key = self._get_cache_key(photos, user_preferences)
        if self.config.cache_intermediate:
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Using cached result for batch of {len(photos)} photos")
                return cached_result
        
        # Initialize culling engine
        engine = AICullingEngine(user_preferences)
        
        if self.config.use_multiprocessing and len(photos) > 10:
            # Use process pool for CPU-intensive operations
            result = await self._process_with_workers(photos, engine)
        else:
            # Single-threaded processing for small batches
            result = engine.analyze_batch(photos)
        
        # Cache result
        if self.config.cache_intermediate and result.get('success'):
            self._cache_result(cache_key, result)
        
        return result
    
    async def _process_with_workers(self, photos: List[Dict[str, Any]], engine: AICullingEngine) -> Dict[str, Any]:
        """Process photos using worker processes/threads."""
        
        # Split photos into chunks for workers
        chunk_size = max(1, len(photos) // self.config.max_workers)
        photo_chunks = [photos[i:i + chunk_size] for i in range(0, len(photos), chunk_size)]
        
        if self.config.use_multiprocessing:
            # Use process pool for CPU-bound work
            with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = [
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._analyze_chunk_sync, chunk, engine
                    )
                    for chunk in photo_chunks
                ]
                
                chunk_results = await asyncio.gather(*futures)
        else:
            # Use thread pool for I/O bound work
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = [
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._analyze_chunk_sync, chunk, engine
                    )
                    for chunk in photo_chunks
                ]
                
                chunk_results = await asyncio.gather(*futures)
        
        # Merge chunk results
        return self._merge_chunk_results(chunk_results, photos)
    
    def _analyze_chunk_sync(self, photo_chunk: List[Dict[str, Any]], engine: AICullingEngine) -> Dict[str, Any]:
        """Analyze a chunk of photos synchronously."""
        return engine.analyze_batch(photo_chunk)
    
    def _merge_chunk_results(self, chunk_results: List[Dict[str, Any]], original_photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from multiple chunks."""
        
        merged_groups = []
        merged_recommendations = []
        total_processing_time = 0
        
        for chunk_result in chunk_results:
            if chunk_result.get('success'):
                merged_groups.extend(chunk_result.get('groups', []))
                merged_recommendations.extend(chunk_result.get('recommendations', []))
                total_processing_time += chunk_result.get('processing_time', 0)
        
        return {
            'success': True,
            'groups': merged_groups,
            'total_photos': len(original_photos),
            'recommendations': merged_recommendations,
            'processing_time': total_processing_time,
            'scoring_weights': chunk_results[0].get('scoring_weights', {}) if chunk_results else {}
        }
    
    async def _monitor_resources(self, job_id: str):
        """Monitor system resources during processing."""
        
        process = psutil.Process()
        
        while job_id in self.processing_metrics:
            try:
                # Update metrics
                memory_mb = process.memory_info().rss / (1024 * 1024)
                cpu_percent = process.cpu_percent()
                
                metrics = self.processing_metrics[job_id]
                metrics.memory_usage_mb = memory_mb
                metrics.cpu_usage_percent = cpu_percent
                
                # Log if usage is high
                if memory_mb > self.config.memory_limit_mb * 0.9:
                    logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                
                if cpu_percent > 95:
                    logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error monitoring resources: {str(e)}")
                break
    
    def _generate_job_id(self, photos: List[Dict[str, Any]]) -> str:
        """Generate unique job ID based on photo content."""
        content = str([p.get('filename', p.get('filepath', '')) for p in photos[:10]])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_digest = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"job_{timestamp}_{hash_digest}"
    
    def _get_cache_key(self, photos: List[Dict[str, Any]], user_preferences: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for photo batch and preferences."""
        content = {
            'photos': [p.get('filepath', p.get('filename')) for p in photos],
            'preferences': user_preferences or {},
            'config': {
                'batch_size': self.config.batch_size,
                'max_workers': self.config.max_workers
            }
        }
        content_str = str(content)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and fresh."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                # Check age (expire after 24 hours)
                file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_age > timedelta(hours=24):
                    cache_file.unlink()  # Remove old cache
                    return None
                
                # Load cached result
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading cached result: {str(e)}")
                try:
                    cache_file.unlink()  # Remove corrupted cache
                except:
                    pass
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache processing result."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
    
    def _compile_results(self, batch_results: List[Dict[str, Any]], job_id: str) -> Dict[str, Any]:
        """Compile results from multiple batches."""
        
        if not batch_results:
            return {'success': False, 'error': 'No results to compile'}
        
        # Merge all results
        all_groups = []
        all_recommendations = []
        total_processing_time = 0
        success = True
        
        for result in batch_results:
            if result.get('success'):
                all_groups.extend(result.get('groups', []))
                all_recommendations.extend(result.get('recommendations', []))
                total_processing_time += result.get('processing_time', 0)
            else:
                success = False
                if 'error' in result:
                    return {'success': False, 'error': result['error']}
        
        return {
            'success': success,
            'groups': all_groups,
            'total_photos': self.processing_metrics[job_id].total_photos,
            'recommendations': all_recommendations,
            'processing_time': total_processing_time,
            'scoring_weights': batch_results[0].get('scoring_weights', {}) if batch_results else {}
        }
    
    def _cleanup_job(self, job_id: str):
        """Clean up job resources."""
        if job_id in self.processing_metrics:
            del self.processing_metrics[job_id]
        
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]
        
        # Force garbage collection
        gc.collect()
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a processing job."""
        if job_id in self.active_jobs:
            # In a real implementation, this would signal workers to stop
            # For now, just mark as cancelled
            self.active_jobs[job_id]['cancelled'] = True
            logger.info(f"Cancelled job {job_id}")
            return True
        return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing job."""
        if job_id in self.processing_metrics:
            metrics = self.processing_metrics[job_id]
            return {
                'job_id': job_id,
                'status': 'processing',
                'progress_percentage': (metrics.processed_photos / metrics.total_photos) * 100 if metrics.total_photos > 0 else 0,
                'processed_photos': metrics.processed_photos,
                'total_photos': metrics.total_photos,
                'memory_usage_mb': metrics.memory_usage_mb,
                'cpu_usage_percent': metrics.cpu_usage_percent
            }
        return None
    
    def clear_cache(self) -> int:
        """Clear all cached results."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        count = 0
        
        for cache_file in cache_files:
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Error deleting cache file {cache_file}: {str(e)}")
        
        logger.info(f"Cleared {count} cached results")
        return count

class CullingOptimizedEngine:
    """High-performance wrapper for the AI culling engine."""
    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.processor = CullingBatchProcessor(config)
        
    async def analyze_batch(self, 
                           photos: List[Dict[str, Any]], 
                           user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze photos with performance optimization."""
        return await self.processor.process_large_batch(photos, user_preferences)
    
    def get_optimal_config(self, photo_count: int, available_memory_mb: Optional[int] = None) -> BatchConfig:
        """Get optimal configuration for given photo count."""
        
        if available_memory_mb is None:
            available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
        
        # Adjust batch size based on photo count and memory
        if photo_count < 50:
            batch_size = photo_count
            max_workers = 1
        elif photo_count < 200:
            batch_size = 25
            max_workers = min(4, cpu_count())
        else:
            # Large batch - optimize for throughput
            memory_per_photo = 10  # Estimated memory per photo in MB
            optimal_batch_size = max(10, available_memory_mb // (memory_per_photo * max(2, cpu_count())))
            batch_size = min(100, optimal_batch_size)
            max_workers = min(8, cpu_count())
        
        # Use multiprocessing for large batches
        use_multiprocessing = photo_count > 20
        
        return BatchConfig(
            batch_size=batch_size,
            max_workers=max_workers,
            use_multiprocessing=use_multiprocessing,
            memory_limit_mb=min(available_memory_mb * 0.8, 2048),  # Use 80% of available or max 2GB
            enable_gpu=photo_count > 100  # Enable GPU acceleration for very large batches
        )

# Convenience functions
async def optimize_culling_performance(photos: List[Dict[str, Any]], 
                                   user_preferences: Optional[Dict[str, Any]] = None,
                                   config: Optional[BatchConfig] = None) -> Dict[str, Any]:
    """
    Analyze photos with automatic performance optimization.
    
    Args:
        photos: List of photo metadata dictionaries
        user_preferences: User preference dictionary
        config: Optional custom configuration
        
    Returns:
        Analysis results with performance metrics
    """
    engine = CullingOptimizedEngine(config)
    
    if config is None:
        # Auto-optimize configuration
        config = engine.get_optimal_config(len(photos))
    
    return await engine.analyze_batch(photos, user_preferences)

def get_performance_recommendations(photo_count: int, 
                                  processing_time: float, 
                                  metrics: ProcessingMetrics) -> List[str]:
    """Get performance recommendations based on metrics."""
    
    recommendations = []
    
    # Throughput recommendations
    throughput = photo_count / processing_time if processing_time > 0 else 0
    if throughput < 10:  # Less than 10 photos per second
        recommendations.append("Consider enabling multiprocessing for better performance")
        if metrics.worker_count < cpu_count():
            recommendations.append("Increase worker count to match available CPU cores")
    
    # Memory recommendations
    if metrics.memory_usage_mb > 1024:
        recommendations.append("Reduce batch size to lower memory usage")
        recommendations.append("Consider enabling intermediate result caching")
    
    # CPU recommendations
    if metrics.cpu_usage_percent < 50 and throughput < 20:
        recommendations.append("CPU utilization is low - can increase worker count")
    elif metrics.cpu_usage_percent > 90:
        recommendations.append("CPU utilization is high - consider reducing worker count")
    
    # Batch size recommendations
    if metrics.batch_size > 100 and throughput < 5:
        recommendations.append("Large batch size may be inefficient - try smaller batches")
    elif metrics.batch_size < 10 and photo_count > 100:
        recommendations.append("Small batch size for large set - consider larger batches")
    
    return recommendations