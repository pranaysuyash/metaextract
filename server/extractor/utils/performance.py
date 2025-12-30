#!/usr/bin/env python3
"""
Performance monitoring and optimization utilities.
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger("metaextract.performance")

class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to measure operation performance."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.metrics[operation_name] = {
                "duration_ms": round(duration * 1000, 2),
                "memory_delta_mb": round(memory_delta / 1024 / 1024, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.debug(f"{operation_name}: {duration*1000:.2f}ms, {memory_delta/1024/1024:.2f}MB")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system performance info."""
        try:
            process = psutil.Process()
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "process_memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "process_cpu_percent": process.cpu_percent(),
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            logger.warning(f"Error getting system info: {e}")
            return {}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "operations": self.metrics,
            "system": self.get_system_info(),
            "total_runtime_ms": round((time.time() - self.start_time) * 1000, 2)
        }
    
    def log_performance_summary(self):
        """Log a summary of performance metrics."""
        total_time = sum(m.get("duration_ms", 0) for m in self.metrics.values())
        total_memory = sum(m.get("memory_delta_mb", 0) for m in self.metrics.values())
        
        logger.info(f"Performance Summary:")
        logger.info(f"  Total processing time: {total_time:.2f}ms")
        logger.info(f"  Total memory delta: {total_memory:.2f}MB")
        logger.info(f"  Operations: {len(self.metrics)}")
        
        # Log slowest operations
        sorted_ops = sorted(
            self.metrics.items(), 
            key=lambda x: x[1].get("duration_ms", 0), 
            reverse=True
        )
        
        if sorted_ops:
            logger.info("  Slowest operations:")
            for op_name, metrics in sorted_ops[:3]:
                logger.info(f"    {op_name}: {metrics.get('duration_ms', 0):.2f}ms")

def optimize_for_file_size(file_size_bytes: int) -> Dict[str, Any]:
    """Return optimization settings based on file size."""
    size_mb = file_size_bytes / 1024 / 1024
    
    if size_mb < 1:  # Small files
        return {
            "use_cache": True,
            "parallel_processing": False,
            "chunk_size": 65536,  # 64KB
            "timeout_seconds": 30
        }
    elif size_mb < 50:  # Medium files
        return {
            "use_cache": True,
            "parallel_processing": True,
            "chunk_size": 1048576,  # 1MB
            "timeout_seconds": 120
        }
    elif size_mb < 500:  # Large files
        return {
            "use_cache": True,
            "parallel_processing": True,
            "chunk_size": 4194304,  # 4MB
            "timeout_seconds": 300
        }
    else:  # Very large files
        return {
            "use_cache": False,  # Too large to cache effectively
            "parallel_processing": True,
            "chunk_size": 8388608,  # 8MB
            "timeout_seconds": 600
        }

def check_system_resources() -> Dict[str, Any]:
    """Check if system has sufficient resources for processing."""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "sufficient_memory": memory.available > 512 * 1024 * 1024,  # 512MB
            "sufficient_disk": disk.free > 1024 * 1024 * 1024,  # 1GB
            "cpu_load_ok": psutil.cpu_percent(interval=0.1) < 80,
            "memory_available_mb": round(memory.available / 1024 / 1024, 2),
            "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            "recommendations": []
        }
    except Exception as e:
        logger.warning(f"Error checking system resources: {e}")
        return {
            "sufficient_memory": True,  # Assume OK if we can't check
            "sufficient_disk": True,
            "cpu_load_ok": True,
            "error": str(e)
        }