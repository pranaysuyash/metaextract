"""
MetaExtract Advanced Analytics Module

This module provides sophisticated analytics to identify patterns in extraction 
failures and performance bottlenecks.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import statistics
import json
from dataclasses import dataclass
from enum import Enum

from .monitoring import get_monitor, SystemMonitor
from .comprehensive_metadata_engine import COMPREHENSIVE_TIER_CONFIGS, Tier


@dataclass
class PerformanceSample:
    """Represents a single performance measurement."""
    timestamp: float
    processing_time_ms: float
    success: bool
    tier: str
    file_type: str
    file_size: Optional[int] = None
    error_type: Optional[str] = None


class BottleneckType(Enum):
    """Types of performance bottlenecks."""
    HIGH_LATENCY = "high_latency"
    LOW_THROUGHPUT = "low_throughput"
    HIGH_ERROR_RATE = "high_error_rate"
    RESOURCE_CONSTRAINED = "resource_constrained"
    MODULE_SPECIFIC = "module_specific"


class PatternAnalyzer:
    """Analyzes patterns in extraction data to identify bottlenecks and failure trends."""
    
    def __init__(self, max_samples: int = 10000):
        self.samples = deque(maxlen=max_samples)
        self.lock = threading.Lock()
        
    def add_sample(self, sample: PerformanceSample):
        """Add a performance sample for analysis."""
        with self.lock:
            self.samples.append(sample)
    
    def get_failure_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in failures."""
        with self.lock:
            if not self.samples:
                return {}
            
            # Group failures by error type
            error_counts = defaultdict(int)
            error_by_tier = defaultdict(lambda: defaultdict(int))
            error_by_filetype = defaultdict(lambda: defaultdict(int))
            
            for sample in self.samples:
                if not sample.success and sample.error_type:
                    error_counts[sample.error_type] += 1
                    error_by_tier[sample.tier][sample.error_type] += 1
                    error_by_filetype[sample.file_type][sample.error_type] += 1
            
            # Calculate failure rates by tier
            tier_failures = {}
            for tier in ['free', 'starter', 'premium', 'super']:
                tier_samples = [s for s in self.samples if s.tier == tier]
                if tier_samples:
                    failed_count = sum(1 for s in tier_samples if not s.success)
                    tier_failures[tier] = {
                        'total': len(tier_samples),
                        'failed': failed_count,
                        'failure_rate': failed_count / len(tier_samples) if tier_samples else 0
                    }
            
            # Calculate failure rates by file type
            filetype_failures = {}
            for filetype in set(s.file_type for s in self.samples):
                filetype_samples = [s for s in self.samples if s.file_type == filetype]
                if filetype_samples:
                    failed_count = sum(1 for s in filetype_samples if not s.success)
                    filetype_failures[filetype] = {
                        'total': len(filetype_samples),
                        'failed': failed_count,
                        'failure_rate': failed_count / len(filetype_samples) if filetype_samples else 0
                    }
            
            return {
                'error_counts': dict(error_counts),
                'error_by_tier': {k: dict(v) for k, v in error_by_tier.items()},
                'error_by_filetype': {k: dict(v) for k, v in error_by_filetype.items()},
                'failure_rates_by_tier': tier_failures,
                'failure_rates_by_filetype': filetype_failures
            }
    
    def get_performance_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in performance metrics."""
        with self.lock:
            if not self.samples:
                return {}
            
            # Calculate overall performance metrics
            all_times = [s.processing_time_ms for s in self.samples if s.success]
            if not all_times:
                return {}
            
            # Performance by tier
            performance_by_tier = {}
            for tier in ['free', 'starter', 'premium', 'super']:
                tier_times = [s.processing_time_ms for s in self.samples if s.tier == tier and s.success]
                if tier_times:
                    performance_by_tier[tier] = {
                        'count': len(tier_times),
                        'avg': statistics.mean(tier_times),
                        'median': statistics.median(tier_times),
                        'min': min(tier_times),
                        'max': max(tier_times),
                        'std_dev': statistics.stdev(tier_times) if len(tier_times) > 1 else 0
                    }
            
            # Performance by file type
            performance_by_filetype = {}
            for filetype in set(s.file_type for s in self.samples):
                filetype_times = [s.processing_time_ms for s in self.samples if s.file_type == filetype and s.success]
                if filetype_times:
                    performance_by_filetype[filetype] = {
                        'count': len(filetype_times),
                        'avg': statistics.mean(filetype_times),
                        'median': statistics.median(filetype_times),
                        'min': min(filetype_times),
                        'max': max(filetype_times),
                        'std_dev': statistics.stdev(filetype_times) if len(filetype_times) > 1 else 0
                    }
            
            # Identify outliers (processing times > 2 standard deviations from mean)
            mean_time = statistics.mean(all_times)
            std_dev = statistics.stdev(all_times) if len(all_times) > 1 else 0
            outliers = [s for s in self.samples if s.success and abs(s.processing_time_ms - mean_time) > 2 * std_dev]
            
            return {
                'overall_performance': {
                    'count': len(all_times),
                    'avg': statistics.mean(all_times),
                    'median': statistics.median(all_times),
                    'min': min(all_times),
                    'max': max(all_times),
                    'std_dev': std_dev
                },
                'performance_by_tier': performance_by_tier,
                'performance_by_filetype': performance_by_filetype,
                'outliers_count': len(outliers),
                'outlier_percentage': len(outliers) / len(self.samples) * 100 if self.samples else 0
            }
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks in the system."""
        with self.lock:
            bottlenecks = []
            
            # Check for high latency
            performance_data = self.get_performance_patterns()
            if performance_data and 'overall_performance' in performance_data:
                avg_time = performance_data['overall_performance']['avg']
                if avg_time > 5000:  # More than 5 seconds average
                    bottlenecks.append({
                        'type': BottleneckType.HIGH_LATENCY.value,
                        'severity': 'high',
                        'description': f'High average processing time: {avg_time:.2f}ms',
                        'recommendation': 'Investigate slow modules or increase system resources'
                    })
            
            # Check for high error rates
            failure_data = self.get_failure_patterns()
            for tier, data in failure_data.get('failure_rates_by_tier', {}).items():
                if data.get('failure_rate', 0) > 0.3:  # More than 30% failure rate
                    bottlenecks.append({
                        'type': BottleneckType.HIGH_ERROR_RATE.value,
                        'severity': 'high',
                        'description': f'High failure rate for {tier} tier: {data["failure_rate"]:.2%}',
                        'recommendation': f'Investigate {tier} tier specific issues'
                    })
            
            # Check for specific file type issues
            for filetype, data in failure_data.get('failure_rates_by_filetype', {}).items():
                if data.get('failure_rate', 0) > 0.5:  # More than 50% failure rate
                    bottlenecks.append({
                        'type': BottleneckType.HIGH_ERROR_RATE.value,
                        'severity': 'high',
                        'description': f'High failure rate for {filetype}: {data["failure_rate"]:.2%}',
                        'recommendation': f'Investigate {filetype} processing issues'
                    })
            
            # Check for performance degradation by file type
            for filetype, perf_data in performance_data.get('performance_by_filetype', {}).items():
                if perf_data.get('avg', 0) > 10000:  # More than 10 seconds average
                    bottlenecks.append({
                        'type': BottleneckType.HIGH_LATENCY.value,
                        'severity': 'medium',
                        'description': f'High average processing time for {filetype}: {perf_data["avg"]:.2f}ms',
                        'recommendation': f'Optimize {filetype} processing pipeline'
                    })
            
            return bottlenecks
    
    def get_trend_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze trends over the specified time period."""
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)  # Convert hours to seconds
            recent_samples = [s for s in self.samples if s.timestamp >= cutoff_time]
            
            if not recent_samples:
                return {}
            
            # Calculate hourly trends
            hourly_data = defaultdict(list)
            for sample in recent_samples:
                hour_key = int(sample.timestamp // 3600)  # Group by hour
                hourly_data[hour_key].append(sample)
            
            # Calculate metrics per hour
            hourly_metrics = []
            for hour, samples in hourly_data.items():
                successful_samples = [s for s in samples if s.success]
                failed_samples = [s for s in samples if not s.success]
                
                avg_time = statistics.mean([s.processing_time_ms for s in successful_samples]) if successful_samples else 0
                success_rate = len(successful_samples) / len(samples) if samples else 0
                
                hourly_metrics.append({
                    'hour': hour,
                    'timestamp': hour * 3600,
                    'total_extractions': len(samples),
                    'successful_extractions': len(successful_samples),
                    'failed_extractions': len(failed_samples),
                    'success_rate': success_rate,
                    'avg_processing_time': avg_time
                })
            
            # Sort by timestamp
            hourly_metrics.sort(key=lambda x: x['timestamp'])
            
            # Calculate trend (simple linear regression slope)
            if len(hourly_metrics) > 1:
                timestamps = [m['timestamp'] for m in hourly_metrics]
                success_rates = [m['success_rate'] for m in hourly_metrics]
                processing_times = [m['avg_processing_time'] for m in hourly_metrics]
                
                # Calculate simple trend (slope)
                if len(success_rates) > 1:
                    time_indices = list(range(len(success_rates)))
                    success_trend = self._calculate_trend(time_indices, success_rates)
                    time_trend = self._calculate_trend(time_indices, processing_times)
                else:
                    success_trend = 0
                    time_trend = 0
            else:
                success_trend = 0
                time_trend = 0
            
            return {
                'hourly_metrics': hourly_metrics,
                'success_rate_trend': success_trend,  # Positive = improving, negative = degrading
                'processing_time_trend': time_trend,  # Positive = slowing down, negative = speeding up
                'trend_period_hours': hours
            }
    
    def _calculate_trend(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate trend using simple linear regression."""
        n = len(x_values)
        if n < 2:
            return 0
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope (m) of regression line: y = mx + b
        numerator = n * sum_xy - sum_x * sum_y
        denominator = n * sum_x2 - sum_x * sum_x
        
        if denominator == 0:
            return 0
        
        return numerator / denominator


class AdvancedAnalytics:
    """Main advanced analytics class."""
    
    def __init__(self):
        self.analyzer = PatternAnalyzer()
        self.monitor = get_monitor()
        self.last_sample_time = time.time()
        self.lock = threading.Lock()
        
    def record_extraction(self, processing_time_ms: float, success: bool, 
                        tier: str = "unknown", file_type: str = "unknown", 
                        file_size: Optional[int] = None, error_type: Optional[str] = None):
        """Record an extraction for analytics."""
        sample = PerformanceSample(
            timestamp=time.time(),
            processing_time_ms=processing_time_ms,
            success=success,
            tier=tier,
            file_type=file_type,
            file_size=file_size,
            error_type=error_type
        )
        
        self.analyzer.add_sample(sample)
    
    def get_failure_analysis(self) -> Dict[str, Any]:
        """Get comprehensive failure analysis."""
        return self.analyzer.get_failure_patterns()
    
    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get comprehensive performance analysis."""
        return self.analyzer.get_performance_patterns()
    
    def get_bottleneck_analysis(self) -> List[Dict[str, Any]]:
        """Get bottleneck analysis."""
        return self.analyzer.identify_bottlenecks()
    
    def get_trend_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get trend analysis."""
        return self.analyzer.get_trend_analysis(hours)
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get a comprehensive analytics report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'failure_analysis': self.get_failure_analysis(),
            'performance_analysis': self.get_performance_analysis(),
            'bottleneck_analysis': self.get_bottleneck_analysis(),
            'trend_analysis': self.get_trend_analysis(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []
        
        # Get current data
        failure_analysis = self.get_failure_analysis()
        performance_analysis = self.get_performance_analysis()
        bottlenecks = self.get_bottleneck_analysis()
        
        # Add recommendations based on bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck['severity'] in ['high', 'critical']:
                recommendations.append(bottleneck['recommendation'])
        
        # Add recommendations based on failure patterns
        high_failure_tiers = [
            tier for tier, data in failure_analysis.get('failure_rates_by_tier', {}).items()
            if data.get('failure_rate', 0) > 0.2  # More than 20% failure rate
        ]
        
        if high_failure_tiers:
            recommendations.append(f"High failure rates detected for tiers: {', '.join(high_failure_tiers)}. Consider reviewing tier-specific configurations.")
        
        # Add recommendations based on performance
        slow_file_types = [
            ftype for ftype, data in performance_analysis.get('performance_by_filetype', {}).items()
            if data.get('avg', 0) > 8000  # More than 8 seconds average
        ]
        
        if slow_file_types:
            recommendations.append(f"Slow processing detected for file types: {', '.join(slow_file_types)}. Consider optimization.")
        
        if not recommendations:
            recommendations.append("System is performing well with no significant issues detected.")
        
        return recommendations


# Global analytics instance
_analytics = None
_analytics_lock = threading.Lock()


def get_analytics() -> AdvancedAnalytics:
    """Get the global analytics instance."""
    global _analytics
    if _analytics is None:
        with _analytics_lock:
            if _analytics is None:
                _analytics = AdvancedAnalytics()
    return _analytics


def record_extraction_for_analytics(processing_time_ms: float, success: bool, 
                                  tier: str = "unknown", file_type: str = "unknown", 
                                  file_size: Optional[int] = None, error_type: Optional[str] = None):
    """Convenience function to record extraction for analytics."""
    analytics = get_analytics()
    analytics.record_extraction(processing_time_ms, success, tier, file_type, file_size, error_type)


def get_analytics_report() -> Dict[str, Any]:
    """Convenience function to get analytics report."""
    analytics = get_analytics()
    return analytics.get_comprehensive_report()


def get_bottleneck_analysis() -> List[Dict[str, Any]]:
    """Convenience function to get bottleneck analysis."""
    analytics = get_analytics()
    return analytics.get_bottleneck_analysis()


def get_trend_analysis(hours: int = 24) -> Dict[str, Any]:
    """Convenience function to get trend analysis."""
    analytics = get_analytics()
    return analytics.get_trend_analysis()


# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the analytics system
    analytics = get_analytics()
    
    # Simulate some extractions
    import random
    
    print("Simulating extractions for analytics...")
    for i in range(1000):
        success = random.choice([True, True, True, True, False])  # 20% failure rate
        processing_time = random.uniform(100, 8000)  # Random processing time
        tier = random.choice(["free", "starter", "premium", "super"])
        file_type = random.choice(["image/jpeg", "image/png", "video/mp4", "application/pdf"])
        
        if not success:
            error_type = random.choice(["FileError", "ProcessingError", "TimeoutError"])
        else:
            error_type = None
            
        analytics.record_extraction(processing_time, success, tier, file_type, error_type=error_type)
    
    # Get comprehensive report
    print("\n=== Comprehensive Analytics Report ===")
    report = analytics.get_comprehensive_report()
    print(json.dumps(report, indent=2, default=str))
    
    print("\n=== Bottleneck Analysis ===")
    bottlenecks = analytics.get_bottleneck_analysis()
    print(json.dumps(bottlenecks, indent=2, default=str))
    
    print("\n=== Trend Analysis (Last 24 hours) ===")
    trends = analytics.get_trend_analysis()
    print(f"Total data points: {len(trends.get('hourly_metrics', []))}")
    print(f"Success rate trend: {trends.get('success_rate_trend', 0):.4f}")
    print(f"Processing time trend: {trends.get('processing_time_trend', 0):.4f}")