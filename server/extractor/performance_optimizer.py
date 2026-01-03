#!/usr/bin/env python3
"""
Performance Optimization Agent
Identifies extraction bottlenecks, profiles memory usage, and provides
streaming optimizations for large files.

Builds on existing infrastructure in:
- server/performance_tuning.py
- server/extractor/utils/performance.py
- tools/benchmark_suite.py

Author: MetaExtract Team
Version: 1.0.0
"""

import gc
import hashlib
import json
import logging
import os
import sys
import time
import tracemalloc
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Generator

logger = logging.getLogger(__name__)


class BottleneckSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class OptimizationType(Enum):
    STREAMING = "streaming"
    CACHING = "caching"
    PARALLEL = "parallel"
    MEMORY = "memory"
    IO_OPT = "io"
    ALGORITHM = "algorithm"


@dataclass
class Bottleneck:
    """Identified performance bottleneck"""
    component: str
    operation: str
    severity: BottleneckSeverity
    description: str
    impact_ms: float
    memory_impact_mb: float
    recommendations: List[str]
    affected_formats: List[str]


@dataclass
class OptimizationSuggestion:
    """Suggested optimization"""
    optimization_type: OptimizationType
    component: str
    description: str
    expected_improvement: str
    implementation_difficulty: str
    priority: int
    code_changes: Optional[str] = None


@dataclass
class ExtractorProfile:
    """Performance profile for an extractor"""
    extractor_name: str
    extractor_type: str
    
    # Timing
    total_calls: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    
    # Memory
    peak_memory_mb: float = 0.0
    avg_memory_mb: float = 0.0
    memory_growth_mb: float = 0.0
    
    # Success
    success_count: int = 0
    error_count: int = 0
    
    # File types
    file_formats: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Comprehensive performance optimization report"""
    timestamp: str
    system_info: Dict[str, Any]
    
    # Profiles
    extractor_profiles: Dict[str, ExtractorProfile]
    identified_bottlenecks: List[Bottleneck]
    
    # Metrics
    total_extraction_time_ms: float
    total_memory_peak_mb: float
    overall_throughput_files_per_min: float
    success_rate: float
    
    # Optimizations
    optimization_suggestions: List[OptimizationSuggestion]
    
    # Recommendations
    high_priority_actions: List[str]
    medium_priority_actions: List[str]
    low_priority_actions: List[str]


class PerformanceProfiler:
    """
    Profiles extraction performance to identify bottlenecks.
    """

    def __init__(self):
        self.extractor_profiles: Dict[str, ExtractorProfile] = {}
        self.operation_timings: Dict[str, List[float]] = defaultdict(list)
        self.memory_samples: List[Dict[str, float]] = []
        self.current_extractor: Optional[str] = None
        self.tracemalloc_started = False

    @contextmanager
    def profile_extractor(self, extractor_name: str, extractor_type: str):
        """Context manager to profile an extractor."""
        old_extractor = self.current_extractor
        self.current_extractor = extractor_name

        if extractor_name not in self.extractor_profiles:
            self.extractor_profiles[extractor_name] = ExtractorProfile(
                extractor_name=extractor_name,
                extractor_type=extractor_type
            )

        gc.collect()
        tracemalloc.start()
        start_time = time.time()
        start_memory = self._get_memory_mb()

        try:
            yield
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = self._get_memory_mb()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            elapsed_ms = (end_time - start_time) * 1000
            profile = self.extractor_profiles[extractor_name]

            profile.total_calls += 1
            profile.total_time_ms += elapsed_ms
            profile.avg_time_ms = profile.total_time_ms / profile.total_calls
            profile.min_time_ms = min(profile.min_time_ms, elapsed_ms)
            profile.max_time_ms = max(profile.max_time_ms, elapsed_ms)
            profile.peak_memory_mb = max(profile.peak_memory_mb, peak / 1024 / 1024)
            profile.memory_growth_mb += end_memory - start_memory

            if success:
                profile.success_count += 1
            else:
                profile.error_count += 1

            self.current_extractor = old_extractor

    def _get_memory_mb(self) -> float:
        """Get current process memory in MB."""
        import psutil
        return psutil.Process().memory_info().rss / 1024 / 1024

    def get_bottlenecks(self) -> List[Bottleneck]:
        """Identify bottlenecks from collected profiles."""
        bottlenecks = []

        for name, profile in self.extractor_profiles.items():
            if profile.avg_time_ms > 1000:
                bottlenecks.append(Bottleneck(
                    component=name,
                    operation="extraction",
                    severity=BottleneckSeverity.HIGH if profile.avg_time_ms > 5000 else BottleneckSeverity.MEDIUM,
                    description=f"Average extraction time {profile.avg_time_ms:.0f}ms exceeds 1 second",
                    impact_ms=profile.avg_time_ms,
                    memory_impact_mb=profile.peak_memory_mb,
                    recommendations=[
                        "Consider implementing streaming for large files",
                        "Add caching for repeated extractions",
                        "Profile specific operations within extractor"
                    ],
                    affected_formats=profile.file_formats
                ))

            if profile.peak_memory_mb > 500:
                bottlenecks.append(Bottleneck(
                    component=name,
                    operation="memory_allocation",
                    severity=BottleneckSeverity.CRITICAL if profile.peak_memory_mb > 1000 else BottleneckSeverity.HIGH,
                    description=f"Peak memory usage {profile.peak_memory_mb:.0f}MB is excessive",
                    impact_ms=0,
                    memory_impact_mb=profile.peak_memory_mb,
                    recommendations=[
                        "Implement streaming file reading",
                        "Process in chunks instead of loading entire file",
                        "Use generators for large data structures"
                    ],
                    affected_formats=profile.file_formats
                ))

            if profile.error_count > profile.total_calls * 0.1:
                bottlenecks.append(Bottleneck(
                    component=name,
                    operation="error_handling",
                    severity=BottleneckSeverity.HIGH,
                    description=f"Error rate {profile.error_count/profile.total_calls*100:.0f}% exceeds 10%",
                    impact_ms=profile.avg_time_ms * profile.error_count,
                    memory_impact_mb=0,
                    recommendations=[
                        "Review error handling in extractor",
                        "Add fallback extraction methods",
                        "Log detailed error information"
                    ],
                    affected_formats=profile.file_formats
                ))

        bottlenecks.sort(key=lambda b: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[b.severity.value],
            -b.impact_ms
        ))

        return bottlenecks


class StreamingOptimizer:
    """
    Provides streaming optimizations for large file processing.
    """

    CHUNK_SIZES = {
        "small": 64 * 1024,       # 64KB
        "medium": 1 * 1024 * 1024, # 1MB
        "large": 4 * 1024 * 1024,  # 4MB
        "xlarge": 16 * 1024 * 1024, # 16MB
    }

    @staticmethod
    def get_optimal_chunk_size(file_size: int) -> int:
        """Get optimal chunk size based on file size."""
        size_mb = file_size / 1024 / 1024

        if size_mb < 1:
            return StreamingOptimizer.CHUNK_SIZES["small"]
        elif size_mb < 10:
            return StreamingOptimizer.CHUNK_SIZES["medium"]
        elif size_mb < 100:
            return StreamingOptimizer.CHUNK_SIZES["large"]
        else:
            return StreamingOptimizer.CHUNK_SIZES["xlarge"]

    @staticmethod
    @contextmanager
    def stream_file(filepath: str, chunk_size: Optional[int] = None) -> Generator[bytes, None, None]:
        """Stream a file in chunks to reduce memory usage."""
        file_size = os.path.getsize(filepath)
        if chunk_size is None:
            chunk_size = StreamingOptimizer.get_optimal_chunk_size(file_size)

        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    def estimate_memory_savings(file_size: int, chunk_size: int) -> Dict[str, Any]:
        """Estimate memory savings from streaming vs full load."""
        full_load_mb = file_size / 1024 / 1024
        chunked_peak_mb = chunk_size / 1024 / 1024

        return {
            "full_load_memory_mb": full_load_mb,
            "chunked_peak_mb": chunked_peak_mb,
            "memory_reduction_mb": full_load_mb - chunked_peak_mb,
            "memory_reduction_percent": (1 - chunked_peak_mb / full_load_mb) * 100 if full_load_mb > 0 else 0
        }


class MemoryOptimizer:
    """
    Memory optimization utilities for extraction.
    """

    @staticmethod
    def get_optimal_batch_size(files: List[str], available_memory_mb: float) -> int:
        """Calculate optimal batch size based on available memory."""
        if not files:
            return 1

        avg_file_size = sum(os.path.getsize(f) for f in files) / len(files)
        avg_file_mb = avg_file_size / 1024 / 1024

        safe_batch_size = int(available_memory_mb / (avg_file_mb * 2))
        return max(1, min(safe_batch_size, 50))

    @staticmethod
    @contextmanager
    def memory_efficient_context():
        """Context for memory-efficient operations."""
        gc.collect()
        initial_memory = MemoryOptimizer._get_memory_mb()

        try:
            yield
        finally:
            gc.collect()
            final_memory = MemoryOptimizer._get_memory_mb()
            if final_memory > initial_memory * 1.5:
                logger.warning(
                    f"Memory grew significantly: {initial_memory:.1f}MB -> {final_memory:.1f}MB"
                )

    @staticmethod
    def _get_memory_mb() -> float:
        """Get current process memory in MB."""
        import psutil
        return psutil.Process().memory_info().rss / 1024 / 1024


class IOWaitAnalyzer:
    """
    Analyzes I/O wait times to identify bottlenecks.
    """

    @staticmethod
    def get_io_stats() -> Dict[str, Any]:
        """Get I/O statistics for the current process."""
        import psutil

        try:
            process = psutil.Process()
            io_counters = process.io_counters()

            return {
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
                "read_speed_mbps": 0,
                "write_speed_mbps": 0
            }
        except Exception as e:
            logger.warning(f"Could not get I/O stats: {e}")
            return {}

    @staticmethod
    def estimate_read_speed(filepath: str) -> float:
        """Estimate file read speed in MB/s."""
        if not os.path.exists(filepath):
            return 0

        file_size = os.path.getsize(filepath)
        start_time = time.time()

        with open(filepath, 'rb') as f:
            data = f.read()

        elapsed = time.time() - start_time
        if elapsed > 0:
            return (file_size / 1024 / 1024) / elapsed
        return 0


class PerformanceOptimizationAgent:
    """
    Main agent for performance optimization.
    """

    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.streaming_optimizer = StreamingOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.io_analyzer = IOWaitAnalyzer()

    def profile_extraction(
        self,
        extractor_func: Callable,
        extractor_name: str,
        extractor_type: str,
        *args,
        **kwargs
    ) -> ExtractorProfile:
        """Profile a single extraction call."""
        with self.profiler.profile_extractor(extractor_name, extractor_type):
            result = extractor_func(*args, **kwargs)

        return self.profiler.extractor_profiles[extractor_name]

    def analyze_performance(self) -> PerformanceReport:
        """Analyze collected performance data and generate report."""
        bottlenecks = self.profiler.get_bottlenecks()
        suggestions = self._generate_optimization_suggestions(bottlenecks)

        profiles = self.profiler.extractor_profiles

        total_time = sum(p.total_time_ms for p in profiles.values())
        total_calls = sum(p.total_calls for p in profiles.values())
        total_success = sum(p.success_count for p in profiles.values())
        peak_memory = max(p.peak_memory_mb for p in profiles.values()) if profiles else 0

        throughput = (total_calls / total_time * 60000) if total_time > 0 else 0
        success_rate = total_success / total_calls if total_calls > 0 else 0

        return PerformanceReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            system_info=self._get_system_info(),
            extractor_profiles=profiles,
            identified_bottlenecks=bottlenecks,
            total_extraction_time_ms=total_time,
            total_memory_peak_mb=peak_memory,
            overall_throughput_files_per_min=throughput,
            success_rate=success_rate,
            optimization_suggestions=suggestions,
            high_priority_actions=self._get_high_priority_actions(bottlenecks),
            medium_priority_actions=self._get_medium_priority_actions(bottlenecks),
            low_priority_actions=self._get_low_priority_actions(bottlenecks)
        )

    def _generate_optimization_suggestions(
        self, bottlenecks: List[Bottleneck]
    ) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions based on bottlenecks."""
        suggestions = []

        for bottleneck in bottlenecks:
            if bottleneck.severity in [BottleneckSeverity.CRITICAL, BottleneckSeverity.HIGH]:
                if bottleneck.memory_impact_mb > 500:
                    suggestions.append(OptimizationSuggestion(
                        optimization_type=OptimizationType.STREAMING,
                        component=bottleneck.component,
                        description="Implement streaming file reading to reduce memory footprint",
                        expected_improvement=f"Reduce memory from {bottleneck.memory_impact_mb:.0f}MB to under 200MB",
                        implementation_difficulty="medium",
                        priority=1,
                        code_changes=self._get_streaming_code_example()
                    ))

                if bottleneck.impact_ms > 5000:
                    suggestions.append(OptimizationSuggestion(
                        optimization_type=OptimizationType.CACHING,
                        component=bottleneck.component,
                        description="Add caching for repeated extractions of same files",
                        expected_improvement="Near-instant extraction for cached files",
                        implementation_difficulty="low",
                        priority=2
                    ))

            if bottleneck.severity == BottleneckSeverity.MEDIUM:
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.PARALLEL,
                    component=bottleneck.component,
                    description="Consider parallel extraction for multiple files",
                    expected_improvement="2-4x throughput improvement",
                    implementation_difficulty="medium",
                    priority=3
                ))

        suggestions.sort(key=lambda s: s.priority)
        return suggestions

    def _get_streaming_code_example(self) -> str:
        """Get code example for streaming optimization."""
        return '''
# Before: Full file load (high memory)
with open(filepath, 'rb') as f:
    data = f.read()  # Loads entire file into memory

# After: Streaming (low memory)
chunk_size = 4 * 1024 * 1024  # 4MB chunks
with open(filepath, 'rb') as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        process_chunk(chunk)  # Process chunk immediately
'''

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import psutil

        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
        }

    def _get_high_priority_actions(
        self, bottlenecks: List[Bottleneck]
    ) -> List[str]:
        """Get high priority optimization actions."""
        actions = []

        critical_bottlenecks = [
            b for b in bottlenecks
            if b.severity == BottleneckSeverity.CRITICAL
        ]

        for b in critical_bottlenecks:
            if "memory" in b.operation.lower():
                actions.append(
                    f"URGENT: Reduce memory usage in {b.component} "
                    f"(current: {b.memory_impact_mb:.0f}MB)"
                )

        high_bottlenecks = [
            b for b in bottlenecks
            if b.severity == BottleneckSeverity.HIGH and b.impact_ms > 5000
        ]

        for b in high_bottlenecks:
            actions.append(
                f"Optimize {b.component} extraction time "
                f"(current: {b.impact_ms:.0f}ms)"
            )

        return actions

    def _get_medium_priority_actions(
        self, bottlenecks: List[Bottleneck]
    ) -> List[str]:
        """Get medium priority optimization actions."""
        actions = []

        for b in bottlenecks:
            if b.severity == BottleneckSeverity.MEDIUM:
                actions.append(
                    f"Review and optimize {b.component} ({b.description})"
                )

        return actions

    def _get_low_priority_actions(
        self, bottlenecks: List[Bottleneck]
    ) -> List[str]:
        """Get low priority optimization actions."""
        actions = []

        for b in bottlenecks:
            if b.severity in [BottleneckSeverity.LOW, BottleneckSeverity.INFO]:
                actions.append(
                    f"Consider improvements for {b.component}"
                )

        return actions

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = self.analyze_performance()

        return {
            "performance_report": {
                "timestamp": report.timestamp,
                "system_info": report.system_info,
                "metrics": {
                    "total_extraction_time_ms": report.total_extraction_time_ms,
                    "total_memory_peak_mb": report.total_memory_peak_mb,
                    "overall_throughput_files_per_min": report.overall_throughput_files_per_min,
                    "success_rate": report.success_rate
                },
                "extractor_profiles": {
                    name: {
                        "extractor_type": profile.extractor_type,
                        "total_calls": profile.total_calls,
                        "avg_time_ms": round(profile.avg_time_ms, 2),
                        "peak_memory_mb": round(profile.peak_memory_mb, 2),
                        "success_rate": profile.success_count / profile.total_calls if profile.total_calls > 0 else 0
                    }
                    for name, profile in report.extractor_profiles.items()
                },
                "bottlenecks": [
                    {
                        "component": b.component,
                        "severity": b.severity.value,
                        "description": b.description,
                        "impact_ms": b.impact_ms,
                        "memory_impact_mb": b.memory_impact_mb,
                        "recommendations": b.recommendations
                    }
                    for b in report.identified_bottlenecks
                ],
                "optimization_suggestions": [
                    {
                        "type": s.optimization_type.value,
                        "component": s.component,
                        "description": s.description,
                        "expected_improvement": s.expected_improvement,
                        "difficulty": s.implementation_difficulty,
                        "priority": s.priority
                    }
                    for s in report.optimization_suggestions
                ],
                "action_items": {
                    "high_priority": report.high_priority_actions,
                    "medium_priority": report.medium_priority_actions,
                    "low_priority": report.low_priority_actions
                }
            }
        }

    def print_report(self):
        """Print a human-readable performance report."""
        report_data = self.generate_report()
        pr = report_data["performance_report"]

        print("\n" + "=" * 80)
        print("PERFORMANCE OPTIMIZATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {pr['timestamp']}")

        print("\n--- System Info ---")
        si = pr['system_info']
        print(f"  CPU: {si.get('cpu_count', '?')} cores @ {si.get('cpu_percent', 0):.0f}%")
        print(f"  Memory: {si.get('memory_available_mb', 0):.0f}MB available / {si.get('memory_total_mb', 0):.0f}MB total")
        print(f"  Disk: {si.get('disk_usage_percent', 0):.0f}% used")

        print("\n--- Metrics ---")
        m = pr['metrics']
        print(f"  Total extraction time: {m['total_extraction_time_ms']:.0f}ms")
        print(f"  Peak memory: {m['total_memory_peak_mb']:.1f}MB")
        print(f"  Throughput: {m['overall_throughput_files_per_min']:.1f} files/min")
        print(f"  Success rate: {m['success_rate']*100:.1f}%")

        print("\n--- Extractor Profiles ---")
        for name, profile in pr['extractor_profiles'].items():
            print(f"  {name}:")
            print(f"    Avg time: {profile['avg_time_ms']:.0f}ms")
            print(f"    Peak memory: {profile['peak_memory_mb']:.1f}MB")
            print(f"    Success: {profile['success_rate']*100:.0f}%")

        print("\n--- Identified Bottlenecks ---")
        for b in pr['bottlenecks'][:5]:
            print(f"  [{b['severity'].upper()}] {b['component']}")
            print(f"    {b['description']}")

        print("\n--- High Priority Actions ---")
        for action in pr['action_items']['high_priority']:
            print(f"  ! {action}")

        print("\n--- Optimization Suggestions ---")
        for s in pr['optimization_suggestions'][:3]:
            print(f"  [{s['priority']}] {s['type']}: {s['description']}")
            print(f"     Expected: {s['expected_improvement']}")

        print("\n" + "=" * 80)


def profile_extractor_operation(operation_name: str):
    """Decorator to profile an extractor operation."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = tracemalloc.get_traced_memory()

            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                current, peak = tracemalloc.get_traced_memory()

                logger.debug(
                    f"{operation_name}: {elapsed_ms:.1f}ms, "
                    f"memory delta: {(peak - start_memory[0]) / 1024 / 1024:.1f}MB, "
                    f"success: {success}"
                )

            return result
        return wrapper
    return decorator


def run_performance_analysis(test_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run a complete performance analysis."""
    agent = PerformanceOptimizationAgent()

    if test_files:
        import time
        for filepath in test_files[:10]:
            if os.path.exists(filepath):
                try:
                    agent.profile_extraction(
                        lambda p=filepath: agent._read_file_test(p),
                        os.path.basename(filepath),
                        "test"
                    )
                    time.sleep(0.1)
                except Exception:
                    pass

    agent.print_report()
    return agent.generate_report()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Performance Optimization Agent")
    parser.add_argument("--files", nargs="+", help="Test files to profile")
    parser.add_argument("--report", action="store_true", help="Generate JSON report")

    args = parser.parse_args()

    if args.report:
        report = run_performance_analysis(args.files)
        print(json.dumps(report, indent=2))
    else:
        run_performance_analysis(args.files)
