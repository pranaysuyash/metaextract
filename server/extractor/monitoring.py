"""
MetaExtract Monitoring Module

This module provides system health metrics and monitoring capabilities for the
comprehensive metadata extraction engine.
"""

import time
import threading
from collections import deque, defaultdict
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os


class ExtractionMetrics:
    """Track metrics for metadata extractions."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.extraction_times = deque(maxlen=max_samples)  # Processing times in ms
        self.extraction_results = deque(maxlen=max_samples)  # Success/failure
        self.extraction_tiers = deque(maxlen=max_samples)  # Tier usage
        self.extraction_file_types = deque(maxlen=max_samples)  # File type tracking
        self.error_counts = defaultdict(int)  # Count different types of errors
        self.start_time = time.time()
        
    def record_extraction(self, processing_time_ms: float, success: bool, 
                         tier: str, file_type: str, error_type: Optional[str] = None):
        """Record a new extraction event."""
        self.extraction_times.append(processing_time_ms)
        self.extraction_results.append(success)
        self.extraction_tiers.append(tier)
        self.extraction_file_types.append(file_type)
        
        if not success and error_type:
            self.error_counts[error_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        now = time.time()
        total_runtime = now - self.start_time
        
        if not self.extraction_times:
            return {
                "total_extractions": 0,
                "success_rate": 0.0,
                "avg_processing_time_ms": 0.0,
                "total_runtime_seconds": total_runtime
            }
        
        total_extractions = len(self.extraction_times)
        successful_extractions = sum(1 for success in self.extraction_results if success)
        success_rate = successful_extractions / total_extractions if total_extractions > 0 else 0
        
        avg_processing_time = sum(self.extraction_times) / len(self.extraction_times) if self.extraction_times else 0
        
        # Calculate extractions per minute
        extractions_per_minute = (total_extractions / total_runtime) * 60 if total_runtime > 0 else 0
        
        # Tier usage breakdown
        tier_counts = defaultdict(int)
        for tier in self.extraction_tiers:
            tier_counts[tier] += 1
            
        # File type breakdown
        file_type_counts = defaultdict(int)
        for ftype in self.extraction_file_types:
            file_type_counts[ftype] += 1
        
        # Recent error summary
        recent_errors = dict(self.error_counts)
        
        return {
            "total_extractions": total_extractions,
            "successful_extractions": successful_extractions,
            "failed_extractions": total_extractions - successful_extractions,
            "success_rate": success_rate,
            "avg_processing_time_ms": avg_processing_time,
            "min_processing_time_ms": min(self.extraction_times) if self.extraction_times else 0,
            "max_processing_time_ms": max(self.extraction_times) if self.extraction_times else 0,
            "extractions_per_minute": extractions_per_minute,
            "total_runtime_seconds": total_runtime,
            "tier_usage": dict(tier_counts),
            "file_type_usage": dict(file_type_counts),
            "recent_errors": recent_errors
        }


class SystemMonitor:
    """Main system monitoring class."""
    
    def __init__(self):
        self.metrics = ExtractionMetrics()
        self.health_status = "operational"  # operational, degraded, error
        self.last_error_time = None
        self.lock = threading.Lock()  # Thread safety for metrics
        
    def record_extraction(self, processing_time_ms: float, success: bool, 
                         tier: str = "unknown", file_type: str = "unknown", 
                         error_type: Optional[str] = None):
        """Record an extraction event for monitoring."""
        with self.lock:
            self.metrics.record_extraction(processing_time_ms, success, tier, file_type, error_type)
            
            if not success:
                self.last_error_time = time.time()
                # Update health status based on error frequency
                if error_type:
                    # Simple health status update - in a real system, you'd have more sophisticated logic
                    recent_errors = sum(1 for result in list(self.metrics.extraction_results)[-10:] if not result)
                    if recent_errors >= 5:  # 5 out of last 10 failed
                        self.health_status = "degraded"
                    elif recent_errors >= 8:  # 8 out of last 10 failed
                        self.health_status = "error"
                    else:
                        self.health_status = "operational"
    
    def get_health_status(self) -> str:
        """Get current system health status."""
        return self.health_status
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring data."""
        with self.lock:
            stats = self.metrics.get_statistics()
            return {
                "health_status": self.health_status,
                "timestamp": datetime.now().isoformat(),
                "metrics": stats
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance-focused summary."""
        with self.lock:
            stats = self.metrics.get_statistics()
            return {
                "success_rate": stats["success_rate"],
                "avg_processing_time_ms": stats["avg_processing_time_ms"],
                "extractions_per_minute": stats["extractions_per_minute"],
                "tier_usage": stats["tier_usage"],
                "file_type_usage": stats["file_type_usage"]
            }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error-focused summary."""
        with self.lock:
            stats = self.metrics.get_statistics()
            return {
                "failed_extractions": stats["failed_extractions"],
                "recent_errors": stats["recent_errors"],
                "error_rate": 1 - stats["success_rate"],
                "last_error_time": self.last_error_time
            }


# Global monitor instance
_monitor = None
_monitor_lock = threading.Lock()


def get_monitor() -> SystemMonitor:
    """Get the global monitor instance."""
    global _monitor
    if _monitor is None:
        with _monitor_lock:
            if _monitor is None:
                _monitor = SystemMonitor()
    return _monitor


def record_extraction_for_monitoring(processing_time_ms: float, success: bool, 
                                   tier: str = "unknown", file_type: str = "unknown", 
                                   error_type: Optional[str] = None):
    """Convenience function to record extraction for monitoring."""
    monitor = get_monitor()
    monitor.record_extraction(processing_time_ms, success, tier, file_type, error_type)


def get_monitoring_data() -> Dict[str, Any]:
    """Convenience function to get monitoring data."""
    monitor = get_monitor()
    return monitor.get_monitoring_data()


def get_performance_summary() -> Dict[str, Any]:
    """Convenience function to get performance summary."""
    monitor = get_monitor()
    return monitor.get_performance_summary()


def get_error_summary() -> Dict[str, Any]:
    """Convenience function to get error summary."""
    monitor = get_monitor()
    return monitor.get_error_summary()


# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the monitoring system
    monitor = get_monitor()
    
    # Simulate some extractions
    import random
    
    for i in range(100):
        success = random.choice([True, True, True, True, False])  # 20% failure rate
        processing_time = random.uniform(100, 2000)  # Random processing time
        tier = random.choice(["free", "starter", "premium", "super"])
        file_type = random.choice(["image/jpeg", "image/png", "video/mp4", "application/pdf"])
        
        if not success:
            error_type = random.choice(["FileError", "ProcessingError", "TimeoutError"])
        else:
            error_type = None
            
        monitor.record_extraction(processing_time, success, tier, file_type, error_type)
    
    # Print monitoring data
    print("=== System Monitoring Data ===")
    data = monitor.get_monitoring_data()
    print(json.dumps(data, indent=2, default=str))
    
    print("\n=== Performance Summary ===")
    perf = monitor.get_performance_summary()
    print(json.dumps(perf, indent=2, default=str))
    
    print("\n=== Error Summary ===")
    errors = monitor.get_error_summary()
    print(json.dumps(errors, indent=2, default=str))