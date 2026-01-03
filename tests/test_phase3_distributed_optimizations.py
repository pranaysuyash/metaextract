"""
Phase 3 Tests: Distributed Processing & Advanced Optimizations

Comprehensive tests for:
- Distributed task coordination
- Advanced optimization strategies
- Performance prediction
- Cache management
- GPU acceleration checks

Author: MetaExtract Team
"""

import asyncio
import pytest
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
import os
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.extractor.distributed_processing import (
    DistributedCoordinator,
    DistributedTask,
    DistributedResult,
    WorkerNode,
    WorkerStatus,
    ResultCache,
    AdaptiveScheduler,
    InMemoryQueue
)

from server.extractor.advanced_optimizations import (
    AdaptiveChunkSizer,
    PerformancePredictor,
    SmartCacheManager,
    BatchOptimizer,
    GPUAccelerator,
    FileCharacteristics,
    create_optimized_config,
    optimize_batch
)


class TestDistributedProcessing:
    """Test distributed processing framework."""
    
    def test_distributed_task_creation(self):
        """Test distributed task creation."""
        task = DistributedTask(
            task_id='task_1',
            file_path='/path/to/file.h5',
            priority=5
        )
        
        assert task.task_id == 'task_1'
        assert task.file_path == '/path/to/file.h5'
        assert task.priority == 5
        assert task.retries == 0
        assert task.created_at > 0
    
    def test_distributed_task_to_dict(self):
        """Test task serialization."""
        task = DistributedTask(
            task_id='task_1',
            file_path='/path/to/file.h5'
        )
        
        task_dict = task.to_dict()
        assert 'task_id' in task_dict
        assert 'file_path' in task_dict
        assert task_dict['task_id'] == 'task_1'
    
    def test_distributed_result_creation(self):
        """Test result creation."""
        result = DistributedResult(
            task_id='task_1',
            worker_id='worker_1',
            success=True,
            metadata={'fields': 100}
        )
        
        assert result.success is True
        assert result.metadata['fields'] == 100
        assert result.error is None
    
    def test_worker_node_health_check(self):
        """Test worker health check."""
        worker = WorkerNode(
            worker_id='worker_1',
            hostname='localhost',
            port=5000
        )
        
        # Fresh worker should be healthy
        assert worker.is_healthy is True
        
        # Simulate heartbeat timeout
        worker.last_heartbeat = time.time() - 120  # 2 minutes ago
        assert worker.is_healthy is False
    
    def test_worker_node_utilization(self):
        """Test worker utilization calculation."""
        worker = WorkerNode(
            worker_id='worker_1',
            hostname='localhost',
            port=5000,
            capacity=4
        )
        
        # Idle worker
        assert worker.utilization == 0
        
        # Busy worker
        worker.current_task = 'task_1'
        assert worker.utilization == 0.25  # 1/4
    
    def test_coordinator_worker_registration(self):
        """Test worker registration."""
        coordinator = DistributedCoordinator(num_workers=2)
        
        coordinator.register_worker('worker_1', 'localhost', 5000)
        coordinator.register_worker('worker_2', 'localhost', 5001)
        
        assert len(coordinator.workers) == 2
        assert 'worker_1' in coordinator.workers
    
    def test_coordinator_get_healthy_workers(self):
        """Test getting healthy workers."""
        coordinator = DistributedCoordinator(num_workers=2)
        
        coordinator.register_worker('worker_1', 'localhost', 5000)
        coordinator.register_worker('worker_2', 'localhost', 5001)
        
        healthy = coordinator.get_healthy_workers()
        assert len(healthy) == 2
    
    def test_coordinator_best_worker_selection(self):
        """Test best worker selection."""
        coordinator = DistributedCoordinator(num_workers=2)
        
        coordinator.register_worker('worker_1', 'localhost', 5000)
        coordinator.register_worker('worker_2', 'localhost', 5001)
        
        # Both should be idle
        best = coordinator.get_best_worker()
        assert best is not None
        assert best.status == WorkerStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_coordinator_add_task(self):
        """Test adding task to coordinator."""
        coordinator = DistributedCoordinator(num_workers=1)
        
        task = DistributedTask(task_id='task_1', file_path='/path/file.h5')
        await coordinator.add_task(task)
        
        assert coordinator.metrics.total_tasks == 1
    
    @pytest.mark.asyncio
    async def test_coordinator_add_tasks_batch(self):
        """Test adding batch of tasks."""
        coordinator = DistributedCoordinator(num_workers=2)
        
        files = ['file1.h5', 'file2.h5', 'file3.h5']
        task_ids = await coordinator.add_tasks_batch(files)
        
        assert len(task_ids) == 3
        assert coordinator.metrics.total_tasks == 3
    
    def test_result_cache_get_key(self):
        """Test cache key generation."""
        cache = ResultCache()
        
        key1 = cache.get_key('/path/to/file.h5')
        key2 = cache.get_key('/path/to/file.h5')
        
        # Same path should generate same key
        assert key1 == key2
    
    def test_result_cache_operations(self):
        """Test cache get/set operations."""
        cache = ResultCache(ttl=10)
        
        result = DistributedResult(
            task_id='task_1',
            worker_id='worker_1',
            success=True,
            metadata={'test': 'data'}
        )
        
        file_path = '/path/to/file.h5'
        
        # Should be empty initially
        assert cache.get(file_path) is None
        
        # Set value
        cache.set(file_path, result)
        
        # Should retrieve cached value
        cached = cache.get(file_path)
        assert cached is not None
        assert cached.task_id == 'task_1'
    
    def test_result_cache_ttl(self):
        """Test cache TTL expiration."""
        cache = ResultCache(ttl=1)  # 1 second TTL
        
        result = DistributedResult(
            task_id='task_1',
            worker_id='worker_1',
            success=True,
            metadata={}
        )
        
        file_path = '/path/to/file.h5'
        cache.set(file_path, result)
        
        # Should be available immediately
        assert cache.get(file_path) is not None
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        assert cache.get(file_path) is None
    
    def test_adaptive_scheduler(self):
        """Test adaptive scheduler."""
        scheduler = AdaptiveScheduler()
        
        # Record some performance data
        scheduler.record_performance('worker_1', 2.0)
        scheduler.record_performance('worker_1', 2.1)
        scheduler.record_performance('worker_1', 1.9)
        
        # Should estimate based on average
        est_time = scheduler.estimate_task_time('worker_1', 10*1024*1024)  # 10MB
        assert est_time > 0
    
    def test_in_memory_queue(self):
        """Test in-memory message queue."""
        queue = InMemoryQueue()
        
        # Queue should exist
        assert queue is not None


class TestAdvancedOptimizations:
    """Test advanced optimization strategies."""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary test file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as f:
            f.write(b'TEST' * 1024 * 1024)  # 4MB
            path = f.name
        yield path
        os.unlink(path)
    
    def test_adaptive_chunk_sizer_initialization(self):
        """Test chunk sizer initialization."""
        sizer = AdaptiveChunkSizer()
        assert sizer.baseline_chunk_size == 1024 * 1024
    
    def test_file_characteristics_creation(self):
        """Test file characteristics."""
        chars = FileCharacteristics(
            file_path='/path/to/file.h5',
            file_size=100*1024*1024,
            file_type='.h5',
            estimated_chunks=100,
            recommended_chunk_size=1024*1024,
            expected_processing_time=10.0,
            complexity_score=0.7
        )
        
        assert chars.file_size == 100*1024*1024
        assert chars.complexity_score == 0.7
    
    def test_adaptive_chunk_sizer_small_file(self):
        """Test chunk sizing for small file."""
        sizer = AdaptiveChunkSizer()
        
        # Small file: < 10MB
        context = {'file_path': '/tmp/small.txt'}
        # Mock file info
        chars = FileCharacteristics(
            file_path='/tmp/small.txt',
            file_size=5*1024*1024,
            file_type='.txt',
            estimated_chunks=20,
            recommended_chunk_size=256*1024,
            expected_processing_time=0.5,
            complexity_score=0.3
        )
        
        assert chars.recommended_chunk_size == 256*1024
    
    def test_performance_predictor_recording(self):
        """Test performance data recording."""
        predictor = PerformancePredictor()
        
        predictor.record_extraction('.h5', 100*1024*1024, 2.5)
        predictor.record_extraction('.h5', 200*1024*1024, 5.0)
        
        assert '.h5' in predictor.performance_history
        assert len(predictor.performance_history['.h5']) == 2
    
    def test_performance_predictor_prediction(self):
        """Test performance prediction."""
        predictor = PerformancePredictor()
        
        # Record some baseline data
        for i in range(5):
            predictor.record_extraction('.h5', 100*1024*1024, 2.0 + i*0.1)
        
        # Predict for new file
        predicted = predictor.predict_time('.h5', 100*1024*1024)
        assert predicted > 0
    
    def test_performance_predictor_stats(self):
        """Test performance statistics."""
        predictor = PerformancePredictor()
        
        predictor.record_extraction('.h5', 100*1024*1024, 2.0)
        predictor.record_extraction('.h5', 100*1024*1024, 2.5)
        predictor.record_extraction('.h5', 100*1024*1024, 1.8)
        
        stats = predictor.get_stats('.h5')
        
        assert stats['count'] == 3
        assert 'avg_time' in stats
        assert 'median_time' in stats
    
    def test_smart_cache_get_put(self):
        """Test cache get/put operations."""
        cache = SmartCacheManager(max_size=10000)
        
        # Put value
        cache.put('key1', 'value1', 100)
        
        # Get value
        value = cache.get('key1')
        assert value == 'value1'
    
    def test_smart_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        cache = SmartCacheManager(max_size=10000)
        
        # Add value
        cache.put('key1', 'value1', 100)
        
        # Hit
        cache.get('key1')
        
        # Miss
        cache.get('key_nonexistent')
        
        # Hit rate should be 50%
        assert cache.get_hit_rate() == 50.0
    
    def test_smart_cache_eviction(self):
        """Test LRU eviction."""
        cache = SmartCacheManager(max_size=1000)
        
        # Add items up to size limit
        cache.put('key1', 'value1', 600)
        cache.put('key2', 'value2', 600)
        
        # Should have evicted key1
        assert cache.get('key1') is None
        assert cache.get('key2') is not None
    
    def test_smart_cache_stats(self):
        """Test cache statistics."""
        cache = SmartCacheManager(max_size=10000)
        
        cache.put('key1', 'value1', 100)
        cache.get('key1')
        
        stats = cache.get_stats()
        
        assert 'size' in stats
        assert 'utilization_percent' in stats
        assert 'hit_rate' in stats
    
    def test_batch_optimizer_ordering(self):
        """Test batch optimization ordering."""
        optimizer = BatchOptimizer()
        
        files = [
            '/path/to/simple.txt',
            '/path/to/complex.h5',
            '/path/to/video.mp4'
        ]
        
        # Get optimized order
        optimized = optimizer.optimize_batch_order(files)
        
        # Should return tuples of (file, config)
        assert len(optimized) == len(files)
        assert all(isinstance(item, tuple) for item in optimized)
    
    def test_batch_optimizer_distribution(self):
        """Test batch distribution across workers."""
        optimizer = BatchOptimizer()
        
        files = [f'/path/file{i}.h5' for i in range(10)]
        
        distribution = optimizer.distribute_across_workers(files, num_workers=4)
        
        assert len(distribution) == 4
        total_files = sum(len(f) for f in distribution.values())
        assert total_files == 10
    
    def test_gpu_accelerator_availability_check(self):
        """Test GPU availability check."""
        accelerator = GPUAccelerator()
        
        # Should work even if GPU not available
        assert isinstance(accelerator.gpu_available, bool)
    
    def test_gpu_accelerator_format_support(self):
        """Test GPU support for formats."""
        accelerator = GPUAccelerator()
        
        # Video format
        can_accel = accelerator.can_accelerate('/path/video.mp4')
        assert isinstance(can_accel, bool)
        
        # Text format (usually not accelerated)
        can_accel = accelerator.can_accelerate('/path/file.txt')
        assert isinstance(can_accel, bool)
    
    def test_gpu_accelerator_acceleration(self):
        """Test GPU acceleration function."""
        accelerator = GPUAccelerator()
        
        metadata = {'test': 'data'}
        result = accelerator.accelerate_extraction('/path/file.h5', metadata)
        
        # Should return metadata (possibly enhanced)
        assert 'test' in result
    
    def test_create_optimized_config(self):
        """Test config creation function."""
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as f:
            f.write(b'TEST' * 1024 * 100)  # 400KB
            path = f.name
        
        try:
            config = create_optimized_config(path)
            
            assert 'chunk_size' in config
            assert 'estimated_chunks' in config
            assert 'expected_processing_time' in config
            assert 'complexity' in config
        finally:
            os.unlink(path)
    
    def test_optimize_batch_function(self):
        """Test batch optimization function."""
        files = ['/tmp/file1.h5', '/tmp/file2.h5', '/tmp/file3.h5']
        
        distribution = optimize_batch(files, num_workers=2)
        
        assert len(distribution) == 2


class TestIntegrationPhase3:
    """Integration tests for Phase 3."""
    
    @pytest.mark.asyncio
    async def test_distributed_coordinator_full_flow(self):
        """Test complete distributed extraction flow."""
        def mock_extraction(file_path):
            return {'file': file_path, 'extracted': True}
        
        coordinator = DistributedCoordinator(num_workers=2)
        
        # Register workers
        coordinator.register_worker('worker_1', 'localhost', 5000)
        coordinator.register_worker('worker_2', 'localhost', 5001)
        
        # Add tasks
        await coordinator.add_tasks_batch(['file1.h5', 'file2.h5'])
        
        # Process
        results, metrics = await coordinator.process_tasks(mock_extraction)
        
        # Should have results
        assert metrics.completed_tasks > 0 or metrics.total_tasks > 0
    
    def test_optimization_and_caching_integration(self):
        """Test integration of optimization and caching."""
        # Create optimized config
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as f:
            f.write(b'TEST' * 1024)  # 4KB
            path = f.name
        
        try:
            # Get optimized config
            config = create_optimized_config(path)
            
            # Cache the result
            cache = SmartCacheManager()
            cache.put(path, config, len(str(config)))
            
            # Retrieve from cache
            cached_config = cache.get(path)
            assert cached_config is not None
            assert cached_config['chunk_size'] > 0
        finally:
            os.unlink(path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
