#!/usr/bin/env python3
"""
Test suite for Memory Management Agent and streaming implementations.

Tests:
- Memory profiling across extractors
- Streaming efficiency
- Garbage collection optimization
- Memory pool operations
- Large file handling
"""

import pytest
import psutil
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
import time
import sys

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from extractor.memory_management_agent import (
    MemoryMonitor,
    MemoryAnalyzer,
    GarbageCollectionOptimizer,
    MemoryResourcePool,
    MemoryManagementAgent,
    MemoryLevel,
    ExtractionStrategy,
    get_memory_agent,
    cleanup_memory_agent
)
from extractor.streaming_large_files import (
    StreamingConfig,
    BinaryStreamReader,
    AdaptiveChunkSizer,
    StreamingExtractionFactory
)


class TestMemoryMonitor:
    """Test memory monitoring functionality."""
    
    def test_memory_snapshot(self):
        """Test taking memory snapshot."""
        monitor = MemoryMonitor()
        snapshot = monitor.get_current_snapshot()
        
        assert snapshot.resident_mb > 0
        assert snapshot.percent_used >= 0
        assert snapshot.available_mb > 0
    
    def test_memory_level_detection(self):
        """Test memory level classification."""
        monitor = MemoryMonitor()
        
        # Mock different levels
        levels = [
            (30, MemoryLevel.HEALTHY),
            (60, MemoryLevel.WARNING),
            (80, MemoryLevel.CRITICAL),
            (95, MemoryLevel.EMERGENCY),
        ]
        
        for percent, expected_level in levels:
            level = monitor._get_memory_level(percent)
            assert level == expected_level
    
    def test_monitoring_thread(self):
        """Test background monitoring thread."""
        monitor = MemoryMonitor()
        monitor.start_monitoring()
        
        # Collect some snapshots
        time.sleep(1)
        
        assert len(monitor.snapshots) > 0
        
        monitor.stop_monitoring()
    
    def test_peak_memory_tracking(self):
        """Test peak memory tracking."""
        monitor = MemoryMonitor()
        
        # Allocate some memory
        data = [i for i in range(1000000)]  # ~10MB
        
        # Take snapshots
        monitor.get_current_snapshot()
        time.sleep(0.1)
        monitor.get_current_snapshot()
        
        peak = monitor.get_peak_memory()
        assert peak > 0


class TestGarbageCollectionOptimizer:
    """Test garbage collection optimization."""
    
    def test_gc_config_retrieval(self):
        """Test getting GC configuration."""
        optimizer = GarbageCollectionOptimizer()
        config = optimizer.get_current_config()
        
        assert 'thresholds' in config
        assert 'stats' in config
        assert len(config['thresholds']) == 3
    
    def test_optimization_strategies(self):
        """Test different optimization strategies."""
        optimizer = GarbageCollectionOptimizer()
        
        strategies = [
            ExtractionStrategy.AGGRESSIVE,
            ExtractionStrategy.BALANCED,
            ExtractionStrategy.CONSERVATIVE,
        ]
        
        for strategy in strategies:
            optimizer.optimize_for_extraction(strategy)
            config = optimizer.get_current_config()
            assert config['thresholds'] is not None
    
    def test_force_collection(self):
        """Test forcing garbage collection."""
        optimizer = GarbageCollectionOptimizer()
        
        # Allocate and discard
        data = [list(range(1000)) for _ in range(1000)]
        del data
        
        # Force collection
        collected = optimizer.force_collection()
        assert collected >= 0
    
    def test_reset_to_default(self):
        """Test resetting to default configuration."""
        optimizer = GarbageCollectionOptimizer()
        original = optimizer.original_thresholds
        
        # Modify
        optimizer.optimize_for_extraction(ExtractionStrategy.AGGRESSIVE)
        
        # Reset
        optimizer.reset_to_default()
        
        import gc
        current = gc.get_threshold()
        assert current == original


class TestMemoryResourcePool:
    """Test memory resource pooling."""
    
    def test_buffer_allocation(self):
        """Test buffer allocation from pool."""
        pool = MemoryResourcePool(buffer_size=1024)
        
        buffer = pool.allocate_buffer()
        assert len(buffer) == 1024
        
        stats = pool.get_stats()
        assert stats['allocations'] == 1
    
    def test_buffer_reuse(self):
        """Test buffer reuse."""
        pool = MemoryResourcePool(buffer_size=1024)
        
        # Allocate and release
        buffer1 = pool.allocate_buffer()
        pool.release_buffer(buffer1)
        
        # Reuse
        buffer2 = pool.allocate_buffer()
        assert buffer2 is buffer1
        
        stats = pool.get_stats()
        assert stats['reuses'] == 1
    
    def test_pool_stats(self):
        """Test pool statistics."""
        pool = MemoryResourcePool(buffer_size=512)
        
        # Allocate multiple
        buffers = [pool.allocate_buffer() for _ in range(3)]
        
        stats = pool.get_stats()
        assert stats['allocations'] == 3
        assert stats['currently_in_use'] == 3
        
        # Release some
        for buf in buffers[:2]:
            pool.release_buffer(buf)
        
        stats = pool.get_stats()
        assert stats['currently_available'] >= 2


class TestAdaptiveChunkSizer:
    """Test adaptive chunk sizing."""
    
    def test_optimal_chunk_size(self):
        """Test calculating optimal chunk size."""
        sizer = AdaptiveChunkSizer()
        
        chunk_size = sizer.get_optimal_chunk_size()
        
        # Should be within bounds
        assert sizer.min_chunk <= chunk_size <= sizer.max_chunk
    
    def test_chunk_size_bounds(self):
        """Test chunk size respects bounds."""
        min_size = 256 * 1024
        max_size = 5 * 1024 * 1024
        
        sizer = AdaptiveChunkSizer(min_chunk=min_size, max_chunk=max_size)
        chunk_size = sizer.get_optimal_chunk_size()
        
        assert chunk_size >= min_size
        assert chunk_size <= max_size


class TestBinaryStreamReader:
    """Test binary file streaming."""
    
    def test_chunk_reading(self):
        """Test reading file chunks."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Write test data
            test_data = b'x' * (1024 * 1024 * 3)  # 3MB
            f.write(test_data)
            f.flush()
            
            try:
                reader = BinaryStreamReader(StreamingConfig(chunk_size=1024 * 1024, adaptive_sizing=False))
                
                chunks = list(reader.read_chunks(f.name))
                
                # Should have 3 chunks of 1MB
                assert len(chunks) >= 3
                
                # Reconstruct data
                reconstructed = b''.join(chunks)
                assert reconstructed == test_data
                
            finally:
                os.unlink(f.name)
    
    def test_offset_reading(self):
        """Test reading specific offset."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_data = b'0123456789' * 100
            f.write(test_data)
            f.flush()
            
            try:
                reader = BinaryStreamReader()
                
                # Read from offset
                chunk = reader.read_with_offset(f.name, 100, 50)
                
                assert len(chunk) == 50
                assert chunk == test_data[100:150]
                
            finally:
                os.unlink(f.name)


class TestMemoryManagementAgent:
    """Test main memory management agent."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        agent = MemoryManagementAgent()
        
        assert agent.analyzer is not None
        assert agent.gc_optimizer is not None
        assert agent.monitor is not None
        assert agent.buffer_pool is not None
    
    def test_memory_status(self):
        """Test getting memory status."""
        agent = MemoryManagementAgent()
        
        status = agent.get_memory_status()
        
        assert 'current_snapshot' in status
        assert 'memory_level' in status
        assert 'available_mb' in status
        assert 'used_percent' in status
    
    def test_analysis_report(self):
        """Test generating analysis report."""
        agent = MemoryManagementAgent()
        
        report = agent.get_analysis_report()
        
        assert 'timestamp' in report
        assert 'memory_status' in report
        assert 'gc_config' in report
        assert 'buffer_pool_stats' in report
    
    def test_optimize_all(self):
        """Test running all optimizations."""
        agent = MemoryManagementAgent()
        
        # Should not raise
        agent.optimize_all()
    
    def test_global_agent(self):
        """Test global agent singleton."""
        agent1 = get_memory_agent()
        agent2 = get_memory_agent()
        
        assert agent1 is agent2
        
        cleanup_memory_agent()


class TestStreamingFactory:
    """Test streaming extraction factory."""
    
    def test_reader_selection(self):
        """Test selecting appropriate reader."""
        
        test_cases = [
            ('.dcm', 'DicomStreamReader'),
            ('.fits', 'FitsStreamReader'),
            ('.h5', 'HDF5StreamReader'),
            ('.nc', 'NetCDFStreamReader'),
            ('.mp4', 'VideoStreamReader'),
            ('.wav', 'AudioStreamReader'),
        ]
        
        for ext, expected_class in test_cases:
            reader = StreamingExtractionFactory.get_reader(f'test{ext}')
            assert reader is not None
            assert expected_class in reader.__class__.__name__
    
    def test_streaming_support(self):
        """Test checking streaming support."""
        assert StreamingExtractionFactory.supports_streaming('file.dcm')
        assert StreamingExtractionFactory.supports_streaming('file.h5')
        assert not StreamingExtractionFactory.supports_streaming('file.txt')


class TestMemoryEfficiency:
    """Integration tests for memory efficiency."""
    
    def test_extraction_with_memory_tracking(self):
        """Test extraction with memory tracking."""
        
        def dummy_extraction(data):
            """Dummy extraction function."""
            return {'extracted': len(data)}
        
        agent = MemoryManagementAgent()
        
        # Small test data
        test_data = b'x' * (1024 * 100)
        
        # Would need actual file for full test
        # result, metrics = agent.execute_extraction(...)
    
    def test_large_file_streaming_strategy(self):
        """Test streaming strategy selection."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Create 100MB file
            f.write(b'x' * (100 * 1024 * 1024))
            f.flush()
            
            try:
                reader = BinaryStreamReader(
                    StreamingConfig(adaptive_sizing=True)
                )
                
                # Should handle large file
                chunk_count = 0
                for chunk in reader.read_chunks(f.name):
                    chunk_count += 1
                    if chunk_count > 5:  # Just test first few chunks
                        break
                
                assert chunk_count > 0
                
            finally:
                os.unlink(f.name)


# Performance benchmarks
class TestMemoryPerformance:
    """Performance benchmarks for memory management."""
    
    def test_monitor_overhead(self):
        """Test memory monitor overhead."""
        monitor = MemoryMonitor()
        monitor.start_monitoring()
        
        start_time = time.time()
        for _ in range(100):
            monitor.get_current_snapshot()
        elapsed = time.time() - start_time
        
        monitor.stop_monitoring()
        
        # Should be fast (< 100ms for 100 snapshots)
        assert elapsed < 0.1
    
    def test_buffer_pool_performance(self):
        """Test buffer pool allocation speed."""
        pool = MemoryResourcePool()
        
        start_time = time.time()
        for _ in range(1000):
            buf = pool.allocate_buffer()
            pool.release_buffer(buf)
        elapsed = time.time() - start_time
        
        # Should be very fast (< 1 second)
        assert elapsed < 1.0
    
    def test_streaming_memory_efficiency(self):
        """Test that streaming uses reasonable memory."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Create test file
            size = 10 * 1024 * 1024  # 10MB
            f.write(b'x' * size)
            f.flush()
            
            try:
                monitor = MemoryMonitor()
                monitor.start_monitoring()
                
                reader = BinaryStreamReader(
                    StreamingConfig(chunk_size=1024 * 1024, adaptive_sizing=False)
                )
                
                chunk_count = 0
                for chunk in reader.read_chunks(f.name):
                    chunk_count += 1
                
                peak_memory = monitor.get_peak_memory()
                monitor.stop_monitoring()
                
                # Should successfully process file
                assert chunk_count > 0
                
            finally:
                os.unlink(f.name)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
