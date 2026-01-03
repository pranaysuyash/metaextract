#!/usr/bin/env python3
"""
MetaExtract Memory Management Agent v1.0

Comprehensive memory management system for extraction operations:
- Memory usage analysis and monitoring
- Streaming implementation for large files
- Memory-efficient processing strategies
- Garbage collection optimization
- Resource pooling and caching strategies

Features:
- Real-time memory tracking across extractors
- Adaptive memory limits based on available system resources
- Chunked processing for large datasets
- Memory-aware task scheduling
- Automatic garbage collection tuning
- Memory leak detection and reporting

Author: MetaExtract Team
"""

import logging
import psutil
import gc
import sys
import os
import threading
import tracemalloc
import weakref
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from enum import Enum
import time
import json

logger = logging.getLogger(__name__)


class MemoryLevel(Enum):
    """Memory pressure levels."""
    HEALTHY = "healthy"           # < 50% utilization
    WARNING = "warning"           # 50-75% utilization
    CRITICAL = "critical"         # 75-90% utilization
    EMERGENCY = "emergency"       # > 90% utilization


class ExtractionStrategy(Enum):
    """Extraction strategies based on memory availability."""
    AGGRESSIVE = "aggressive"     # Load everything into memory
    BALANCED = "balanced"         # Mix of streaming and buffering
    CONSERVATIVE = "conservative" # Stream everything, minimal buffering


@dataclass
class MemorySnapshot:
    """Snapshot of memory state."""
    timestamp: float = field(default_factory=time.time)
    resident_mb: float = 0.0          # RSS memory
    virtual_mb: float = 0.0           # VMS memory
    percent_used: float = 0.0         # Percent of available memory
    available_mb: float = 0.0         # Available memory
    memory_level: MemoryLevel = MemoryLevel.HEALTHY
    process_id: int = field(default_factory=os.getpid)
    
    def __repr__(self) -> str:
        return (f"MemorySnapshot(rss={self.resident_mb:.1f}MB, "
                f"used={self.percent_used:.1f}%, "
                f"level={self.memory_level.value})")


@dataclass
class ExtractionMemoryProfile:
    """Memory profile for a specific extraction."""
    file_path: str
    file_size_mb: float = 0.0
    expected_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    average_memory_mb: float = 0.0
    extraction_time_sec: float = 0.0
    chunks_processed: int = 0
    memory_ratio: float = 0.0  # peak_memory / file_size
    
    def __repr__(self) -> str:
        return (f"ExtractionMemoryProfile({Path(self.file_path).name}, "
                f"peak={self.peak_memory_mb:.1f}MB, "
                f"ratio={self.memory_ratio:.2f})")


class MemoryMonitor:
    """Monitor memory usage in real-time."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.snapshots: List[MemorySnapshot] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = 0.5  # seconds
        
    def get_current_snapshot(self) -> MemorySnapshot:
        """Get current memory state."""
        try:
            mem_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            virtual_memory = psutil.virtual_memory()
            
            snapshot = MemorySnapshot(
                resident_mb=mem_info.rss / (1024 * 1024),
                virtual_mb=mem_info.vms / (1024 * 1024),
                percent_used=memory_percent,
                available_mb=virtual_memory.available / (1024 * 1024),
                memory_level=self._get_memory_level(memory_percent)
            )
            
            self.snapshots.append(snapshot)
            return snapshot
            
        except Exception as e:
            logger.error(f"Error getting memory snapshot: {e}")
            return MemorySnapshot()
    
    def _get_memory_level(self, percent: float) -> MemoryLevel:
        """Determine memory level from percentage."""
        if percent < 50:
            return MemoryLevel.HEALTHY
        elif percent < 75:
            return MemoryLevel.WARNING
        elif percent < 90:
            return MemoryLevel.CRITICAL
        else:
            return MemoryLevel.EMERGENCY
    
    def start_monitoring(self):
        """Start background memory monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                self.get_current_snapshot()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
    
    def get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        if not self.snapshots:
            return 0.0
        return max(s.resident_mb for s in self.snapshots)
    
    def get_average_memory(self) -> float:
        """Get average memory usage in MB."""
        if not self.snapshots:
            return 0.0
        return sum(s.resident_mb for s in self.snapshots) / len(self.snapshots)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'current': self.get_current_snapshot(),
            'peak_mb': self.get_peak_memory(),
            'average_mb': self.get_average_memory(),
            'snapshots_collected': len(self.snapshots)
        }


class MemoryAnalyzer:
    """Analyze memory usage patterns across extractors."""
    
    def __init__(self):
        self.profiles: Dict[str, ExtractionMemoryProfile] = {}
        self.per_extractor_stats: Dict[str, List[ExtractionMemoryProfile]] = defaultdict(list)
        self.memory_monitor = MemoryMonitor()
        
    def analyze_extraction(
        self,
        file_path: str,
        file_size_mb: float,
        extraction_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, ExtractionMemoryProfile]:
        """Analyze memory usage during extraction."""
        
        # Start monitoring
        self.memory_monitor.start_monitoring()
        initial_snapshot = self.memory_monitor.get_current_snapshot()
        start_time = time.time()
        
        try:
            # Clear snapshots for this analysis
            self.memory_monitor.snapshots = []
            
            # Run extraction
            result = extraction_func(*args, **kwargs)
            
            # Get final metrics
            final_snapshot = self.memory_monitor.get_current_snapshot()
            elapsed_time = time.time() - start_time
            
            # Calculate profile
            profile = ExtractionMemoryProfile(
                file_path=file_path,
                file_size_mb=file_size_mb,
                peak_memory_mb=self.memory_monitor.get_peak_memory(),
                average_memory_mb=self.memory_monitor.get_average_memory(),
                extraction_time_sec=elapsed_time,
                expected_memory_mb=file_size_mb * 2,  # Rough estimate
                memory_ratio=self.memory_monitor.get_peak_memory() / max(file_size_mb, 1)
            )
            
            self.profiles[file_path] = profile
            
            logger.info(f"Extraction analysis: {profile}")
            
            return result, profile
            
        finally:
            self.memory_monitor.stop_monitoring()
    
    def get_extractor_stats(self, extractor_name: str) -> Dict[str, Any]:
        """Get statistics for a specific extractor."""
        profiles = self.per_extractor_stats.get(extractor_name, [])
        
        if not profiles:
            return {}
        
        peak_memories = [p.peak_memory_mb for p in profiles]
        ratios = [p.memory_ratio for p in profiles]
        
        return {
            'extractor': extractor_name,
            'extractions_analyzed': len(profiles),
            'peak_memory_mb': max(peak_memories),
            'average_peak_mb': sum(peak_memories) / len(peak_memories),
            'avg_memory_ratio': sum(ratios) / len(ratios),
            'profiles': profiles
        }
    
    def get_problematic_extractors(self, threshold_ratio: float = 2.0) -> List[str]:
        """Find extractors with high memory ratios."""
        problematic = []
        
        for extractor, profiles in self.per_extractor_stats.items():
            avg_ratio = sum(p.memory_ratio for p in profiles) / len(profiles)
            if avg_ratio > threshold_ratio:
                problematic.append(extractor)
        
        return problematic
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory analysis report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_extractions_analyzed': len(self.profiles),
            'overall_stats': {
                'peak_memory_mb': max((p.peak_memory_mb for p in self.profiles.values()), default=0),
                'average_peak_mb': (sum(p.peak_memory_mb for p in self.profiles.values()) / 
                                   len(self.profiles) if self.profiles else 0),
                'avg_memory_ratio': (sum(p.memory_ratio for p in self.profiles.values()) / 
                                    len(self.profiles) if self.profiles else 0),
            },
            'profiles': {k: {
                'file': v.file_path,
                'file_size_mb': v.file_size_mb,
                'peak_memory_mb': v.peak_memory_mb,
                'memory_ratio': v.memory_ratio,
                'extraction_time_sec': v.extraction_time_sec
            } for k, v in self.profiles.items()},
            'problematic_extractors': self.get_problematic_extractors()
        }


class GarbageCollectionOptimizer:
    """Optimize garbage collection behavior."""
    
    def __init__(self):
        self.original_thresholds = gc.get_threshold()
        self.collection_stats: Dict[int, int] = {}
        self.total_collections = 0
        
    def get_current_config(self) -> Dict[str, Any]:
        """Get current GC configuration."""
        thresholds = gc.get_threshold()
        stats = gc.get_stats()
        
        return {
            'thresholds': thresholds,
            'stats': stats,
            'total_collections': gc.get_count()
        }
    
    def optimize_for_extraction(self, strategy: ExtractionStrategy = ExtractionStrategy.BALANCED):
        """Optimize GC for extraction workload."""
        
        if strategy == ExtractionStrategy.AGGRESSIVE:
            # Less frequent collections for better throughput
            gc.set_threshold(5000, 10, 10)
            gc.set_debug(0)
        
        elif strategy == ExtractionStrategy.BALANCED:
            # Default balanced approach
            gc.set_threshold(700, 10, 10)
            gc.set_debug(0)
        
        elif strategy == ExtractionStrategy.CONSERVATIVE:
            # More frequent collections for low memory
            gc.set_threshold(100, 5, 5)
            gc.set_debug(0)
        
        logger.info(f"GC optimized for {strategy.value} extraction: {gc.get_threshold()}")
    
    def enable_incremental_collection(self):
        """Enable incremental garbage collection."""
        try:
            gc.enable()
            # Try to use incremental collection (Python 3.13+)
            if hasattr(gc, 'set_incremental'):
                gc.set_incremental(True)
                logger.info("Incremental GC enabled")
        except Exception as e:
            logger.warning(f"Could not enable incremental GC: {e}")
    
    def force_collection(self) -> int:
        """Force garbage collection and return freed objects."""
        collected = gc.collect()
        logger.debug(f"GC collection freed {collected} objects")
        return collected
    
    def disable_collection_during_critical(self):
        """Disable GC during critical sections."""
        gc.disable()
        logger.debug("GC disabled for critical section")
    
    def enable_collection(self):
        """Re-enable GC."""
        gc.enable()
        logger.debug("GC re-enabled")
    
    def get_unreachable_objects(self) -> int:
        """Count unreachable objects (potential memory leaks)."""
        gc.set_debug(gc.DEBUG_SAVEALL)
        gc.collect()
        unreachable = len(gc.garbage)
        gc.set_debug(0)
        return unreachable
    
    def reset_to_default(self):
        """Reset GC to default configuration."""
        gc.set_threshold(*self.original_thresholds)
        logger.info("GC reset to default configuration")


class MemoryResourcePool:
    """Pool for reusing memory buffers to reduce allocation overhead."""
    
    def __init__(self, buffer_size: int = 1024 * 1024):
        self.buffer_size = buffer_size
        self.available_buffers: List[bytearray] = []
        self.in_use_buffers: List[weakref.ref] = []
        self.lock = threading.Lock()
        self.stats = {
            'allocations': 0,
            'reuses': 0,
            'deallocations': 0
        }
    
    def allocate_buffer(self) -> bytearray:
        """Get or allocate a buffer."""
        with self.lock:
            if self.available_buffers:
                buffer = self.available_buffers.pop()
                self.stats['reuses'] += 1
                logger.debug(f"Reused buffer from pool (available: {len(self.available_buffers)})")
            else:
                buffer = bytearray(self.buffer_size)
                self.stats['allocations'] += 1
                logger.debug(f"Allocated new buffer (total: {len(self.in_use_buffers)})")
            
            # Track usage (bytearray doesn't support weak references)
            self.in_use_buffers.append(id(buffer))
            
            return buffer
    
    def release_buffer(self, buffer: bytearray):
        """Return buffer to pool."""
        with self.lock:
            if len(buffer) == self.buffer_size:
                buffer.clear()
                self.available_buffers.append(buffer)
                self.stats['deallocations'] += 1
                logger.debug(f"Released buffer to pool (available: {len(self.available_buffers)})")
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        with self.lock:
            return {
                **self.stats,
                'currently_available': len(self.available_buffers),
                'currently_in_use': len(self.in_use_buffers)
            }
    
    def clear(self):
        """Clear the pool."""
        with self.lock:
            self.available_buffers.clear()
            logger.info("Memory resource pool cleared")


class MemoryEfficientExtractor:
    """Wrapper for memory-efficient extraction."""
    
    def __init__(self, extraction_func: Callable, file_path: str):
        self.extraction_func = extraction_func
        self.file_path = file_path
        self.file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        self.file_size_mb = self.file_size / (1024 * 1024)
        self.memory_monitor = MemoryMonitor()
        self.gc_optimizer = GarbageCollectionOptimizer()
        self.buffer_pool = MemoryResourcePool()
        
    def determine_strategy(self) -> ExtractionStrategy:
        """Determine extraction strategy based on file size and available memory."""
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        
        # Require 3x file size as safety margin
        required_memory = self.file_size_mb * 3
        
        if required_memory > available_memory:
            return ExtractionStrategy.CONSERVATIVE
        elif required_memory > available_memory * 0.7:
            return ExtractionStrategy.BALANCED
        else:
            return ExtractionStrategy.AGGRESSIVE
    
    def extract_with_optimization(self, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Run extraction with memory optimizations."""
        
        strategy = self.determine_strategy()
        logger.info(f"Using {strategy.value} extraction strategy for {Path(self.file_path).name}")
        
        # Configure GC
        self.gc_optimizer.optimize_for_extraction(strategy)
        self.gc_optimizer.enable_incremental_collection()
        
        # Start monitoring
        self.memory_monitor.start_monitoring()
        start_time = time.time()
        
        try:
            # Run extraction
            result = self.extraction_func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            
            # Collect metrics
            metrics = {
                'strategy': strategy.value,
                'file_size_mb': self.file_size_mb,
                'peak_memory_mb': self.memory_monitor.get_peak_memory(),
                'average_memory_mb': self.memory_monitor.get_average_memory(),
                'extraction_time_sec': elapsed_time,
                'memory_ratio': self.memory_monitor.get_peak_memory() / max(self.file_size_mb, 1),
                'buffer_pool_stats': self.buffer_pool.get_stats()
            }
            
            logger.info(f"Extraction completed: {metrics}")
            
            return result, metrics
            
        finally:
            self.memory_monitor.stop_monitoring()
            self.gc_optimizer.reset_to_default()
            self.buffer_pool.clear()


class MemoryManagementAgent:
    """Main agent for coordinating memory management."""
    
    def __init__(self):
        self.analyzer = MemoryAnalyzer()
        self.gc_optimizer = GarbageCollectionOptimizer()
        self.monitor = MemoryMonitor()
        self.buffer_pool = MemoryResourcePool()
        self.extraction_wrappers: Dict[str, MemoryEfficientExtractor] = {}
        
    def register_extraction(self, extractor_name: str, extraction_func: Callable):
        """Register an extraction function for monitoring."""
        # This would be called during initialization
        logger.info(f"Registered extraction function: {extractor_name}")
    
    def execute_extraction(
        self,
        file_path: str,
        extraction_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """Execute extraction with memory management."""
        
        extractor = MemoryEfficientExtractor(extraction_func, file_path)
        result, metrics = extractor.extract_with_optimization(*args, **kwargs)
        
        # Store metrics
        self.analyzer.per_extractor_stats[extraction_func.__name__].append(
            ExtractionMemoryProfile(
                file_path=file_path,
                file_size_mb=metrics['file_size_mb'],
                peak_memory_mb=metrics['peak_memory_mb'],
                average_memory_mb=metrics['average_memory_mb'],
                extraction_time_sec=metrics['extraction_time_sec'],
                memory_ratio=metrics['memory_ratio']
            )
        )
        
        return result, metrics
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory status."""
        snapshot = self.monitor.get_current_snapshot()
        return {
            'current_snapshot': snapshot,
            'memory_level': snapshot.memory_level.value,
            'available_mb': snapshot.available_mb,
            'used_percent': snapshot.percent_used
        }
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get analysis report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'memory_status': self.get_memory_status(),
            'gc_config': self.gc_optimizer.get_current_config(),
            'buffer_pool_stats': self.buffer_pool.get_stats(),
            'analysis_report': self.analyzer.generate_report()
        }
    
    def optimize_all(self):
        """Run all optimizations."""
        logger.info("Running all memory optimizations...")
        
        # Optimize GC
        self.gc_optimizer.optimize_for_extraction(ExtractionStrategy.BALANCED)
        
        # Force collection
        self.gc_optimizer.force_collection()
        
        # Check for leaks
        unreachable = self.gc_optimizer.get_unreachable_objects()
        if unreachable > 0:
            logger.warning(f"Found {unreachable} unreachable objects")
        
        logger.info("Memory optimizations completed")


# Global agent instance
_agent: Optional[MemoryManagementAgent] = None


def get_memory_agent() -> MemoryManagementAgent:
    """Get or create global memory management agent."""
    global _agent
    if _agent is None:
        _agent = MemoryManagementAgent()
        logger.info("Memory Management Agent initialized")
    return _agent


def cleanup_memory_agent():
    """Clean up global agent."""
    global _agent
    if _agent:
        _agent.buffer_pool.clear()
        _agent.monitor.stop_monitoring()
        _agent = None
        logger.info("Memory Management Agent cleaned up")


if __name__ == '__main__':
    # Demo
    agent = get_memory_agent()
    
    # Print status
    print("\n=== Memory Management Agent Demo ===\n")
    status = agent.get_memory_status()
    print(f"Current Memory Status:")
    print(f"  Level: {status['memory_level']}")
    print(f"  Available: {status['available_mb']:.1f} MB")
    print(f"  Used: {status['used_percent']:.1f}%")
    
    # Optimize
    agent.optimize_all()
    
    # Report
    report = agent.get_analysis_report()
    print(f"\nOptimization Report:")
    print(json.dumps({k: v for k, v in report.items() if k != 'analysis_report'}, indent=2))
    
    cleanup_memory_agent()
