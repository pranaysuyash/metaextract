#!/usr/bin/env python3
"""
Memory Pressure Monitoring System

Provides real-time memory pressure detection and adaptive cache management:
- Monitor system and process memory usage
- Detect high memory pressure conditions
- Trigger cache eviction and cleanup on demand
- Provide metrics and adaptive thresholds
- Support for different pressure levels (normal, elevated, critical)

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import psutil
import logging
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger("metaextract.memory_pressure")


class PressureLevel(Enum):
    """Memory pressure severity levels"""
    NORMAL = 1      # <60% memory usage
    ELEVATED = 2    # 60-80% memory usage
    HIGH = 3        # 80-90% memory usage
    CRITICAL = 4    # >90% memory usage


@dataclass
class MemoryStats:
    """Current memory statistics"""
    timestamp: datetime
    process_rss_mb: float          # Process resident set size (MB)
    process_vms_mb: float          # Process virtual memory size (MB)
    process_percent: float         # Process % of system memory
    system_available_mb: float     # Available system memory (MB)
    system_total_mb: float         # Total system memory (MB)
    system_percent: float          # System memory usage %
    pressure_level: PressureLevel  # Current pressure level


class MemoryPressureMonitor:
    """Monitor system and process memory pressure"""
    
    def __init__(self,
                 normal_threshold: float = 60.0,
                 elevated_threshold: float = 75.0,
                 high_threshold: float = 85.0,
                 critical_threshold: float = 95.0,
                 sample_interval_seconds: int = 5,
                 history_size: int = 12):
        """
        Initialize memory pressure monitor
        
        Args:
            normal_threshold: Below this % = NORMAL
            elevated_threshold: Above this % = ELEVATED
            high_threshold: Above this % = HIGH
            critical_threshold: Above this % = CRITICAL
            sample_interval_seconds: How often to sample memory (seconds)
            history_size: Keep last N samples for trend analysis
        """
        self.normal_threshold = normal_threshold
        self.elevated_threshold = elevated_threshold
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold
        self.sample_interval_seconds = sample_interval_seconds
        self.history_size = history_size
        
        # Current state
        self._current_stats: Optional[MemoryStats] = None
        self._stats_history: List[MemoryStats] = []
        self._lock = threading.Lock()
        
        # Callbacks for pressure events
        self._pressure_callbacks: Dict[PressureLevel, List[Callable]] = {
            PressureLevel.NORMAL: [],
            PressureLevel.ELEVATED: [],
            PressureLevel.HIGH: [],
            PressureLevel.CRITICAL: []
        }
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Get process object
        self._process = psutil.Process()
        
        logger.info(f"Initialized MemoryPressureMonitor (thresholds: "
                   f"normal<{normal_threshold}%, elevated<{elevated_threshold}%, "
                   f"high<{high_threshold}%, critical>{critical_threshold}%)")
    
    def start_monitoring(self) -> None:
        """Start background monitoring thread"""
        if self._monitoring:
            logger.warning("Monitoring already running")
            return
        
        self._monitoring = True
        self._shutdown_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self._monitor_thread.start()
        logger.debug("Memory pressure monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring thread"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        self._shutdown_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.debug("Memory pressure monitoring stopped")
    
    def _monitor_worker(self) -> None:
        """Background worker thread for continuous monitoring"""
        last_pressure_level = None
        
        while self._monitoring and not self._shutdown_event.wait(self.sample_interval_seconds):
            try:
                # Sample current memory
                stats = self._sample_memory()
                
                with self._lock:
                    self._current_stats = stats
                    self._stats_history.append(stats)
                    
                    # Keep only recent history
                    if len(self._stats_history) > self.history_size:
                        self._stats_history.pop(0)
                
                # Trigger callbacks if pressure level changed
                if stats.pressure_level != last_pressure_level:
                    self._trigger_pressure_callbacks(stats.pressure_level)
                    last_pressure_level = stats.pressure_level
                    
            except Exception as e:
                logger.error(f"Error in memory pressure monitor: {e}")
    
    def _sample_memory(self) -> MemoryStats:
        """Sample current memory usage"""
        try:
            # Get process memory
            process_mem = self._process.memory_info()
            process_rss_mb = process_mem.rss / (1024 * 1024)
            process_vms_mb = process_mem.vms / (1024 * 1024)
            
            # Get system memory
            vm = psutil.virtual_memory()
            system_available_mb = vm.available / (1024 * 1024)
            system_total_mb = vm.total / (1024 * 1024)
            system_percent = vm.percent
            
            # Calculate process percentage
            process_percent = (process_rss_mb / system_total_mb) * 100
            
            # Determine pressure level
            pressure_level = self._get_pressure_level(system_percent)
            
            return MemoryStats(
                timestamp=datetime.now(),
                process_rss_mb=process_rss_mb,
                process_vms_mb=process_vms_mb,
                process_percent=process_percent,
                system_available_mb=system_available_mb,
                system_total_mb=system_total_mb,
                system_percent=system_percent,
                pressure_level=pressure_level
            )
            
        except Exception as e:
            logger.error(f"Failed to sample memory: {e}")
            # Return a default state in case of error
            return MemoryStats(
                timestamp=datetime.now(),
                process_rss_mb=0,
                process_vms_mb=0,
                process_percent=0,
                system_available_mb=0,
                system_total_mb=0,
                system_percent=0,
                pressure_level=PressureLevel.NORMAL
            )
    
    def _get_pressure_level(self, system_percent: float) -> PressureLevel:
        """Determine pressure level based on system memory usage"""
        if system_percent >= self.critical_threshold:
            return PressureLevel.CRITICAL
        elif system_percent >= self.high_threshold:
            return PressureLevel.HIGH
        elif system_percent >= self.elevated_threshold:
            return PressureLevel.ELEVATED
        else:
            return PressureLevel.NORMAL
    
    def get_current_stats(self) -> Optional[MemoryStats]:
        """Get current memory statistics"""
        with self._lock:
            return self._current_stats
    
    def get_history(self) -> List[MemoryStats]:
        """Get memory statistics history"""
        with self._lock:
            return self._stats_history.copy()
    
    def get_average_pressure(self, seconds: int = 60) -> float:
        """Get average system memory usage % over last N seconds"""
        with self._lock:
            if not self._stats_history:
                return 0.0
            
            cutoff_time = datetime.now() - timedelta(seconds=seconds)
            recent_stats = [s for s in self._stats_history 
                          if s.timestamp > cutoff_time]
            
            if not recent_stats:
                return self._stats_history[-1].system_percent
            
            return sum(s.system_percent for s in recent_stats) / len(recent_stats)
    
    def is_under_pressure(self) -> bool:
        """Check if system is under memory pressure (ELEVATED or higher)"""
        stats = self.get_current_stats()
        if not stats:
            return False
        return stats.pressure_level.value >= PressureLevel.ELEVATED.value
    
    def is_critical_pressure(self) -> bool:
        """Check if system is under critical memory pressure"""
        stats = self.get_current_stats()
        if not stats:
            return False
        return stats.pressure_level == PressureLevel.CRITICAL
    
    def get_available_memory_mb(self) -> float:
        """Get available system memory in MB"""
        stats = self.get_current_stats()
        return stats.system_available_mb if stats else 0
    
    def get_eviction_target_mb(self) -> float:
        """
        Calculate how much memory should be freed based on pressure level
        
        Returns:
            Bytes to evict from cache
        """
        stats = self.get_current_stats()
        if not stats:
            return 0
        
        # Target different memory levels based on pressure
        if stats.pressure_level == PressureLevel.CRITICAL:
            # Free memory to get to 70% usage
            target_percent = 70.0
        elif stats.pressure_level == PressureLevel.HIGH:
            # Free memory to get to 75% usage
            target_percent = 75.0
        elif stats.pressure_level == PressureLevel.ELEVATED:
            # Free memory to get to 65% usage
            target_percent = 65.0
        else:
            return 0  # No eviction needed
        
        # Calculate how much to free
        current_used = (stats.system_percent / 100.0) * stats.system_total_mb
        target_used = (target_percent / 100.0) * stats.system_total_mb
        
        if current_used > target_used:
            return (current_used - target_used) * (1024 * 1024)  # Convert to bytes
        
        return 0
    
    def register_pressure_callback(self, 
                                   level: PressureLevel,
                                   callback: Callable[[MemoryStats], None]) -> None:
        """
        Register callback function for pressure level changes
        
        Args:
            level: Pressure level to trigger on
            callback: Function to call with MemoryStats
        """
        self._pressure_callbacks[level].append(callback)
        logger.debug(f"Registered callback for {level.name} pressure")
    
    def _trigger_pressure_callbacks(self, level: PressureLevel) -> None:
        """Trigger all callbacks for given pressure level"""
        stats = self.get_current_stats()
        if not stats:
            return
        
        callbacks = self._pressure_callbacks.get(level, [])
        for callback in callbacks:
            try:
                callback(stats)
            except Exception as e:
                logger.error(f"Error in pressure callback: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory pressure summary"""
        stats = self.get_current_stats()
        
        if not stats:
            return {
                'status': 'no_data',
                'message': 'No memory statistics available yet'
            }
        
        return {
            'timestamp': stats.timestamp.isoformat(),
            'pressure_level': stats.pressure_level.name,
            'system': {
                'used_mb': stats.system_total_mb - stats.system_available_mb,
                'available_mb': stats.system_available_mb,
                'total_mb': stats.system_total_mb,
                'percent': round(stats.system_percent, 2)
            },
            'process': {
                'rss_mb': round(stats.process_rss_mb, 2),
                'vms_mb': round(stats.process_vms_mb, 2),
                'percent': round(stats.process_percent, 2)
            },
            'thresholds': {
                'normal': f"<{self.normal_threshold}%",
                'elevated': f"{self.elevated_threshold}%",
                'high': f"{self.high_threshold}%",
                'critical': f">{self.critical_threshold}%"
            },
            'eviction_target_mb': round(self.get_eviction_target_mb() / (1024 * 1024), 2),
            'under_pressure': self.is_under_pressure(),
            'critical': self.is_critical_pressure()
        }


# Global instance
_global_monitor: Optional[MemoryPressureMonitor] = None


def get_global_monitor() -> MemoryPressureMonitor:
    """Get or create global memory pressure monitor"""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = MemoryPressureMonitor()
        _global_monitor.start_monitoring()
    
    return _global_monitor


def shutdown_monitoring() -> None:
    """Shutdown global memory pressure monitor"""
    global _global_monitor
    
    if _global_monitor:
        _global_monitor.stop_monitoring()
        _global_monitor = None
