#!/usr/bin/env python3
"""
Tests for memory pressure monitoring system

Validates:
- Memory pressure detection and level classification
- Pressure callbacks and event triggering
- Memory statistics collection
- Trend analysis and history tracking
"""

import pytest
import time
import psutil
from datetime import datetime, timedelta

# Add parent to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'server'))

from extractor.utils.memory_pressure import (
    MemoryPressureMonitor,
    PressureLevel,
    MemoryStats,
    get_global_monitor,
    shutdown_monitoring
)


class TestMemoryPressureMonitor:
    """Test memory pressure monitoring"""
    
    def test_initialization(self):
        """Test monitor initialization"""
        monitor = MemoryPressureMonitor(
            normal_threshold=50,
            elevated_threshold=70,
            high_threshold=85,
            critical_threshold=95
        )
        
        assert monitor.normal_threshold == 50
        assert monitor.elevated_threshold == 70
        assert monitor.high_threshold == 85
        assert monitor.critical_threshold == 95
        assert not monitor._monitoring
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        monitor = MemoryPressureMonitor(sample_interval_seconds=1)
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor._monitoring
        assert monitor._monitor_thread is not None
        
        # Wait for first sample
        time.sleep(1.5)
        stats = monitor.get_current_stats()
        assert stats is not None
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor._monitoring
    
    def test_memory_sampling(self):
        """Test memory sampling"""
        monitor = MemoryPressureMonitor()
        stats = monitor._sample_memory()
        
        assert stats.timestamp is not None
        assert stats.process_rss_mb > 0
        assert stats.process_vms_mb > 0
        assert stats.system_total_mb > 0
        assert 0 <= stats.system_percent <= 100
        assert stats.pressure_level in [
            PressureLevel.NORMAL,
            PressureLevel.ELEVATED,
            PressureLevel.HIGH,
            PressureLevel.CRITICAL
        ]
    
    def test_pressure_level_classification(self):
        """Test pressure level classification"""
        monitor = MemoryPressureMonitor(
            normal_threshold=60,
            elevated_threshold=75,
            high_threshold=85,
            critical_threshold=95
        )
        
        # Test classification at different thresholds
        # Below elevated_threshold = NORMAL
        assert monitor._get_pressure_level(50) == PressureLevel.NORMAL
        # At or above elevated_threshold = ELEVATED
        assert monitor._get_pressure_level(75) == PressureLevel.ELEVATED
        # At or above high_threshold = HIGH
        assert monitor._get_pressure_level(85) == PressureLevel.HIGH
        # At or above critical_threshold = CRITICAL
        assert monitor._get_pressure_level(96) == PressureLevel.CRITICAL
    
    def test_available_memory(self):
        """Test available memory reporting"""
        monitor = MemoryPressureMonitor(sample_interval_seconds=1)
        monitor.start_monitoring()
        
        # Wait for first sample
        time.sleep(2.5)
        
        available = monitor.get_available_memory_mb()
        assert available > 0, f"Expected positive available memory, got {available}"
        
        # Should be roughly equal to psutil's value
        vm = psutil.virtual_memory()
        expected = vm.available / (1024 * 1024)
        assert abs(available - expected) < 500  # Within 500MB due to timing variations
        
        monitor.stop_monitoring()
    
    def test_under_pressure_detection(self):
        """Test pressure detection"""
        monitor = MemoryPressureMonitor(
            normal_threshold=50,
            elevated_threshold=70,
            high_threshold=85,
            critical_threshold=95
        )
        
        # Simulate sampling
        monitor._stats_history = [
            MemoryStats(
                timestamp=datetime.now(),
                process_rss_mb=100,
                process_vms_mb=200,
                process_percent=1,
                system_available_mb=500,
                system_total_mb=8000,
                system_percent=55,
                pressure_level=PressureLevel.NORMAL
            )
        ]
        monitor._current_stats = monitor._stats_history[0]
        
        assert not monitor.is_under_pressure()
        assert not monitor.is_critical_pressure()
    
    def test_eviction_target_calculation(self):
        """Test eviction target memory calculation"""
        monitor = MemoryPressureMonitor()
        
        # Create a high pressure scenario
        monitor._current_stats = MemoryStats(
            timestamp=datetime.now(),
            process_rss_mb=100,
            process_vms_mb=200,
            process_percent=2,
            system_available_mb=100,
            system_total_mb=8000,
            system_percent=87,  # High pressure
            pressure_level=PressureLevel.HIGH
        )
        
        # Should calculate eviction target to get to 75%
        target = monitor.get_eviction_target_mb()
        assert target > 0  # Should need to evict
    
    def test_callback_registration(self):
        """Test pressure callback registration"""
        monitor = MemoryPressureMonitor()
        callback_called = []
        
        def test_callback(stats):
            callback_called.append(stats)
        
        monitor.register_pressure_callback(PressureLevel.HIGH, test_callback)
        assert test_callback in monitor._pressure_callbacks[PressureLevel.HIGH]
    
    def test_memory_history(self):
        """Test memory history tracking"""
        monitor = MemoryPressureMonitor(
            sample_interval_seconds=1,
            history_size=5
        )
        
        monitor.start_monitoring()
        time.sleep(3)
        
        history = monitor.get_history()
        assert len(history) > 0
        assert len(history) <= 5
        
        # Verify history ordering
        for i in range(len(history) - 1):
            assert history[i].timestamp <= history[i + 1].timestamp
        
        monitor.stop_monitoring()
    
    def test_average_pressure(self):
        """Test average pressure calculation"""
        monitor = MemoryPressureMonitor()
        
        # Manually add some stats
        now = datetime.now()
        monitor._stats_history = [
            MemoryStats(
                timestamp=now,
                process_rss_mb=100,
                process_vms_mb=200,
                process_percent=1,
                system_available_mb=500,
                system_total_mb=8000,
                system_percent=50,
                pressure_level=PressureLevel.NORMAL
            ),
            MemoryStats(
                timestamp=now + timedelta(seconds=1),
                process_rss_mb=100,
                process_vms_mb=200,
                process_percent=1,
                system_available_mb=400,
                system_total_mb=8000,
                system_percent=60,
                pressure_level=PressureLevel.NORMAL
            ),
            MemoryStats(
                timestamp=now + timedelta(seconds=2),
                process_rss_mb=100,
                process_vms_mb=200,
                process_percent=1,
                system_available_mb=300,
                system_total_mb=8000,
                system_percent=70,
                pressure_level=PressureLevel.ELEVATED
            ),
        ]
        
        avg = monitor.get_average_pressure(seconds=5)
        expected_avg = (50 + 60 + 70) / 3
        assert abs(avg - expected_avg) < 0.1
    
    def test_summary_generation(self):
        """Test summary generation"""
        monitor = MemoryPressureMonitor(sample_interval_seconds=1)
        monitor.start_monitoring()
        
        # Wait for first sample
        time.sleep(2.5)
        
        summary = monitor.get_summary()
        
        assert 'timestamp' in summary
        assert 'pressure_level' in summary
        assert 'system' in summary
        assert 'process' in summary
        assert 'thresholds' in summary
        assert 'eviction_target_mb' in summary
        assert 'under_pressure' in summary
        assert 'critical' in summary
        
        # Check system info
        assert summary['system']['total_mb'] > 0
        assert summary['system']['available_mb'] >= 0  # Can be 0 on very constrained systems
        assert 0 <= summary['system']['percent'] <= 100
        
        monitor.stop_monitoring()


class TestEnhancedCacheIntegration:
    """Test enhanced cache with memory pressure monitoring"""
    
    def test_enhanced_cache_initialization(self):
        """Test enhanced cache initialization"""
        from extractor.utils.cache_enhanced import EnhancedMetadataCache
        
        cache = EnhancedMetadataCache(
            max_memory_entries=100,
            enable_memory_pressure_monitoring=True
        )
        
        assert cache.base_cache is not None
        assert cache.enable_memory_pressure_monitoring
        assert cache._memory_monitor is not None
    
    def test_enhanced_cache_stats(self):
        """Test enhanced cache statistics"""
        from extractor.utils.cache_enhanced import EnhancedMetadataCache
        
        cache = EnhancedMetadataCache(enable_memory_pressure_monitoring=True)
        
        stats = cache.get_stats()
        assert 'pressure_evictions' in stats
        assert 'pressure_events' in stats
        assert 'adaptive_adjustments' in stats
        assert 'memory_pressure' in stats
    
    def test_global_monitor(self):
        """Test global monitor singleton"""
        monitor1 = get_global_monitor()
        monitor2 = get_global_monitor()
        
        assert monitor1 is monitor2
        assert monitor1._monitoring
        
        shutdown_monitoring()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
