#!/usr/bin/env python3
"""
Scientific Format Performance Benchmarking Suite
Comprehensive performance analysis of MetaExtract scientific format extraction.
Measures timing, memory usage, CPU utilization, and scalability metrics.
"""

import sys
import os
import json
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import gc
import tracemalloc

# Add server path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

# Import MetaExtract engines
from extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single benchmark run."""
    dataset_name: str
    dataset_type: str
    file_path: str
    file_size_bytes: int

    # Timing metrics
    extraction_time: float
    total_time: float

    # Memory metrics
    memory_peak_mb: float
    memory_delta_mb: float
    memory_initial_mb: float
    memory_final_mb: float

    # CPU metrics
    cpu_percent_avg: float
    cpu_percent_peak: float

    # Result metrics
    success: bool
    fields_extracted: int
    error_message: Optional[str] = None

    # System info
    system_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkResult:
    """Results for a complete benchmark run."""
    format_type: str
    dataset_count: int
    total_file_size_bytes: int
    total_extraction_time: float
    total_memory_used_mb: float
    avg_cpu_percent: float

    # Aggregated metrics
    metrics: List[PerformanceMetrics] = field(default_factory=list)

    # Performance analysis
    performance_analysis: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """Monitor system performance during extraction."""

    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = 0
        self.peak_memory = 0
        self.memory_samples = []
        self.cpu_samples = []
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.initial_memory
        self.memory_samples = []
        self.cpu_samples = []

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self) -> Tuple[float, float, float, float]:
        """Stop monitoring and return metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = final_memory - self.initial_memory

        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        peak_cpu = max(self.cpu_samples) if self.cpu_samples else 0

        return self.peak_memory, memory_delta, self.initial_memory, final_memory, avg_cpu, peak_cpu

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # Memory monitoring
                current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                self.peak_memory = max(self.peak_memory, current_memory)
                self.memory_samples.append(current_memory)

                # CPU monitoring
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.cpu_samples.append(cpu_percent)

                time.sleep(0.05)  # 20Hz sampling
            except Exception as e:
                logger.warning(f"Performance monitoring error: {e}")
                break

class ScientificPerformanceBenchmarker:
    """Comprehensive performance benchmarker for scientific formats."""

    def __init__(self, datasets_base_path: str):
        self.datasets_base_path = Path(datasets_base_path)
        self.manifest_path = self.datasets_base_path / "dataset_manifest.json"
        self.engine = ComprehensiveMetadataExtractor()
        self.monitor = PerformanceMonitor()

        # System information
        self.system_info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'benchmark_timestamp': datetime.now().isoformat()
        }

    def load_manifest(self) -> Dict[str, Any]:
        """Load the dataset manifest."""
        with open(self.manifest_path, 'r') as f:
            return json.load(f)

    def benchmark_single_dataset(self, dataset_info: Dict[str, Any], format_type: str) -> PerformanceMetrics:
        """Benchmark a single dataset with comprehensive performance monitoring."""
        file_path = dataset_info['files'][0]
        dataset_name = list(dataset_info.keys())[0] if isinstance(dataset_info, dict) else "unknown"

        # Get file size
        file_size = os.path.getsize(file_path)

        logger.info(f"  Benchmarking {dataset_name} ({file_size} bytes)...")

        # Start performance monitoring
        tracemalloc.start()
        self.monitor.start_monitoring()

        start_time = time.time()
        success = False
        fields_extracted = 0
        error_message = None

        try:
            # Perform extraction based on format
            if format_type == 'dicom':
                result = self.engine.medical_engine.extract_dicom_metadata(file_path)
            elif format_type == 'fits':
                result = self.engine.astronomical_engine.extract_fits_metadata(file_path)
            elif format_type == 'hdf5_netcdf':
                dataset_type = dataset_info.get('type', 'hdf5')
                if dataset_type == 'hdf5':
                    result = self.engine.scientific_engine.extract_hdf5_metadata(file_path)
                else:  # netcdf
                    result = self.engine.scientific_engine.extract_netcdf_metadata(file_path)
            else:
                raise ValueError(f"Unknown format type: {format_type}")

            extraction_time = time.time() - start_time
            success = True

            # Count fields extracted
            if result:
                if format_type == 'dicom' and result.get('available'):
                    # Count DICOM fields
                    info_sections = ['patient_info', 'study_info', 'series_info', 'equipment_info',
                                   'image_info', 'acquisition_params', 'dose_info', 'private_tags', 'raw_tags']
                    for section in info_sections:
                        if section in result and isinstance(result[section], dict):
                            fields_extracted += len(result[section])
                elif format_type == 'fits' and result.get('available'):
                    # Count FITS fields
                    if result.get('primary_header'):
                        fields_extracted += len(result['primary_header'])
                    if result.get('wcs_info'):
                        fields_extracted += len(result['wcs_info'])
                    if result.get('observation_info'):
                        fields_extracted += len(result['observation_info'])
                    if result.get('raw_headers'):
                        for hdu_headers in result['raw_headers'].values():
                            if isinstance(hdu_headers, dict):
                                fields_extracted += len(hdu_headers)
                elif format_type == 'hdf5_netcdf' and result.get('available'):
                    # Count HDF5/NetCDF fields
                    if 'datasets' in result:
                        fields_extracted += len(result['datasets'])
                    if 'variables' in result:
                        fields_extracted += len(result['variables'])
                    if 'dimensions' in result:
                        fields_extracted += len(result['dimensions'])
                    if 'global_attributes' in result:
                        fields_extracted += len(result['global_attributes'])
                    if 'attributes' in result:
                        fields_extracted += len(result['attributes'])

        except Exception as e:
            extraction_time = time.time() - start_time
            error_message = str(e)
            success = False

        # Stop monitoring and get metrics
        peak_memory, memory_delta, mem_initial, mem_final, avg_cpu, peak_cpu = self.monitor.stop_monitoring()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        total_time = time.time() - start_time

        return PerformanceMetrics(
            dataset_name=dataset_name,
            dataset_type=format_type,
            file_path=file_path,
            file_size_bytes=file_size,
            extraction_time=extraction_time,
            total_time=total_time,
            memory_peak_mb=peak_memory,
            memory_delta_mb=memory_delta,
            memory_initial_mb=mem_initial,
            memory_final_mb=mem_final,
            cpu_percent_avg=avg_cpu,
            cpu_percent_peak=peak_cpu,
            success=success,
            fields_extracted=fields_extracted,
            error_message=error_message,
            system_info=self.system_info
        )

    def benchmark_format(self, format_type: str, datasets: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark all datasets of a specific format."""
        logger.info(f"Benchmarking {format_type} format with {len(datasets)} datasets")

        metrics = []
        total_file_size = 0
        total_extraction_time = 0.0
        total_memory_used = 0.0
        cpu_samples = []

        for dataset_name, dataset_info in datasets.items():
            metric = self.benchmark_single_dataset(dataset_info, format_type)
            metrics.append(metric)

            total_file_size += metric.file_size_bytes
            total_extraction_time += metric.extraction_time
            total_memory_used += metric.memory_delta_mb
            cpu_samples.append(metric.cpu_percent_avg)

            status = "✅" if metric.success else "❌"
            logger.info(f"    {status} {metric.dataset_name}: {metric.extraction_time:.3f}s, {metric.fields_extracted} fields, {metric.memory_delta_mb:.1f}MB")

        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

        result = BenchmarkResult(
            format_type=format_type,
            dataset_count=len(datasets),
            total_file_size_bytes=total_file_size,
            total_extraction_time=total_extraction_time,
            total_memory_used_mb=total_memory_used,
            avg_cpu_percent=avg_cpu,
            metrics=metrics,
            performance_analysis=self._analyze_performance(metrics)
        )

        return result

    def _analyze_performance(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze performance metrics and provide insights."""
        if not metrics:
            return {}

        successful_metrics = [m for m in metrics if m.success]

        analysis = {
            'success_rate': len(successful_metrics) / len(metrics) * 100,
            'avg_extraction_time': sum(m.extraction_time for m in successful_metrics) / len(successful_metrics) if successful_metrics else 0,
            'avg_memory_delta': sum(m.memory_delta_mb for m in successful_metrics) / len(successful_metrics) if successful_metrics else 0,
            'avg_fields_per_second': 0,
            'memory_efficiency': 0,
            'performance_consistency': 0,
            'bottlenecks': [],
            'recommendations': []
        }

        if successful_metrics:
            total_fields = sum(m.fields_extracted for m in successful_metrics)
            total_time = sum(m.extraction_time for m in successful_metrics)
            analysis['avg_fields_per_second'] = total_fields / total_time if total_time > 0 else 0

            # Memory efficiency (MB per 1000 fields)
            analysis['memory_efficiency'] = (sum(m.memory_delta_mb for m in successful_metrics) / total_fields * 1000) if total_fields > 0 else 0

            # Performance consistency (coefficient of variation)
            times = [m.extraction_time for m in successful_metrics]
            if len(times) > 1:
                mean_time = sum(times) / len(times)
                variance = sum((t - mean_time) ** 2 for t in times) / len(times)
                std_dev = variance ** 0.5
                analysis['performance_consistency'] = (std_dev / mean_time * 100) if mean_time > 0 else 0

        # Identify bottlenecks
        if analysis['avg_extraction_time'] > 1.0:
            analysis['bottlenecks'].append('Slow extraction (>1s average)')
        if analysis['memory_efficiency'] > 50:
            analysis['bottlenecks'].append('High memory usage (>50MB per 1000 fields)')
        if analysis['performance_consistency'] > 50:
            analysis['bottlenecks'].append('Inconsistent performance (>50% variation)')

        # Generate recommendations
        if analysis['avg_extraction_time'] > 0.5:
            analysis['recommendations'].append('Consider optimizing extraction algorithms for better speed')
        if analysis['memory_efficiency'] > 20:
            analysis['recommendations'].append('Review memory management and consider streaming for large files')
        if analysis['performance_consistency'] > 30:
            analysis['recommendations'].append('Investigate performance variability and optimize caching')

        return analysis

    def run_comprehensive_benchmarking(self) -> Dict[str, BenchmarkResult]:
        """Run comprehensive benchmarking on all scientific formats."""
        logger.info("🚀 Starting Comprehensive Scientific Format Performance Benchmarking")

        manifest = self.load_manifest()
        datasets = manifest.get('datasets', {})

        results = {}
        for format_type in ['dicom', 'fits', 'hdf5_netcdf']:
            if format_type in datasets:
                results[format_type] = self.benchmark_format(format_type, datasets[format_type])

        return results

    def generate_comprehensive_report(self, results: Dict[str, BenchmarkResult]) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        total_datasets = sum(result.dataset_count for result in results.values())
        total_file_size = sum(result.total_file_size_bytes for result in results.values())
        total_time = sum(result.total_extraction_time for result in results.values())
        total_memory = sum(result.total_memory_used_mb for result in results.values())

        # Overall performance analysis
        all_metrics = []
        for result in results.values():
            all_metrics.extend(result.metrics)

        successful_metrics = [m for m in all_metrics if m.success]

        overall_analysis = {
            'total_datasets': total_datasets,
            'total_file_size_mb': total_file_size / 1024 / 1024,
            'total_extraction_time': total_time,
            'total_memory_used_mb': total_memory,
            'avg_time_per_dataset': total_time / total_datasets if total_datasets > 0 else 0,
            'avg_memory_per_dataset': total_memory / total_datasets if total_datasets > 0 else 0,
            'overall_success_rate': len(successful_metrics) / len(all_metrics) * 100 if all_metrics else 0,
            'performance_insights': self._generate_overall_insights(results)
        }

        return {
            'benchmark_timestamp': datetime.now().isoformat(),
            'system_info': self.system_info,
            'overall_performance': overall_analysis,
            'format_results': {
                fmt: {
                    'dataset_count': result.dataset_count,
                    'total_file_size_mb': result.total_file_size_bytes / 1024 / 1024,
                    'total_extraction_time': result.total_extraction_time,
                    'total_memory_used_mb': result.total_memory_used_mb,
                    'avg_cpu_percent': result.avg_cpu_percent,
                    'performance_analysis': result.performance_analysis,
                    'metrics': [
                        {
                            'dataset_name': m.dataset_name,
                            'file_size_mb': m.file_size_bytes / 1024 / 1024,
                            'extraction_time': m.extraction_time,
                            'memory_delta_mb': m.memory_delta_mb,
                            'cpu_percent_avg': m.cpu_percent_avg,
                            'fields_extracted': m.fields_extracted,
                            'success': m.success
                        }
                        for m in result.metrics
                    ]
                }
                for fmt, result in results.items()
            }
        }

    def _generate_overall_insights(self, results: Dict[str, BenchmarkResult]) -> List[str]:
        """Generate overall performance insights."""
        insights = []

        # Compare format performance
        format_times = {fmt: result.performance_analysis.get('avg_extraction_time', 0)
                       for fmt, result in results.items()}

        if format_times:
            fastest = min(format_times.items(), key=lambda x: x[1])
            slowest = max(format_times.items(), key=lambda x: x[1])

            if fastest[1] > 0 and slowest[1] > 0:
                ratio = slowest[1] / fastest[1]
                if ratio > 2:
                    insights.append(f"Performance varies significantly by format: {fastest[0]} is {ratio:.1f}x faster than {slowest[0]}")

        # Memory usage analysis
        total_memory = sum(result.total_memory_used_mb for result in results.values())
        if total_memory > 100:
            insights.append("High memory usage detected - consider memory optimization")
        elif total_memory < 10:
            insights.append("Excellent memory efficiency across all formats")

        # Success rate analysis
        success_rates = [result.performance_analysis.get('success_rate', 0) for result in results.values()]
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 0

        if avg_success >= 99:
            insights.append("Exceptional reliability with near-perfect success rates")
        elif avg_success >= 95:
            insights.append("Very reliable performance with high success rates")
        else:
            insights.append("Some reliability issues detected - review error handling")

        return insights

    def save_benchmark_reports(self, results: Dict[str, BenchmarkResult], output_dir: str = "performance_reports"):
        """Save detailed benchmark reports to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save individual format reports
        for format_type, result in results.items():
            report_file = output_path / f"{format_type}_performance_report.json"
            with open(report_file, 'w') as f:
                json.dump({
                    'format_type': result.format_type,
                    'summary': {
                        'dataset_count': result.dataset_count,
                        'total_file_size_mb': result.total_file_size_bytes / 1024 / 1024,
                        'total_extraction_time': result.total_extraction_time,
                        'total_memory_used_mb': result.total_memory_used_mb,
                        'avg_cpu_percent': result.avg_cpu_percent
                    },
                    'performance_analysis': result.performance_analysis,
                    'metrics': [
                        {
                            'dataset_name': m.dataset_name,
                            'file_size_bytes': m.file_size_bytes,
                            'extraction_time': m.extraction_time,
                            'memory_peak_mb': m.memory_peak_mb,
                            'memory_delta_mb': m.memory_delta_mb,
                            'cpu_percent_avg': m.cpu_percent_avg,
                            'fields_extracted': m.fields_extracted,
                            'success': m.success,
                            'error_message': m.error_message
                        }
                        for m in result.metrics
                    ]
                }, f, indent=2)

        # Save comprehensive report
        comprehensive_report = self.generate_comprehensive_report(results)
        summary_file = output_path / "comprehensive_performance_report.json"
        with open(summary_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)

        logger.info(f"Performance reports saved to {output_path}")

def main():
    """Main benchmarking function."""
    # Path to the scientific test datasets
    datasets_path = Path(__file__).parent / "scientific-test-datasets"

    if not datasets_path.exists():
        logger.error(f"Scientific test datasets not found at {datasets_path}")
        sys.exit(1)

    # Create benchmarker and run comprehensive benchmarking
    benchmarker = ScientificPerformanceBenchmarker(str(datasets_path))

    try:
        logger.info("🏃 Starting Comprehensive Scientific Format Performance Benchmarking")
        results = benchmarker.run_comprehensive_benchmarking()

        # Generate and display comprehensive report
        comprehensive_report = benchmarker.generate_comprehensive_report(results)

        print("\n" + "="*90)
        print("🚀 COMPREHENSIVE SCIENTIFIC FORMAT PERFORMANCE BENCHMARKING RESULTS")
        print("="*90)
        print(f"Total Datasets Benchmarked: {comprehensive_report['overall_performance']['total_datasets']}")
        print(f"Overall Success Rate: {comprehensive_report['overall_performance']['overall_success_rate']:.1f}%")
        print(f"Average Time per Dataset: {comprehensive_report['overall_performance']['avg_time_per_dataset']:.3f}s")
        print(f"Total Memory Used: {comprehensive_report['overall_performance']['total_memory_used_mb']:.1f}MB")
        print(f"Total File Size Processed: {comprehensive_report['overall_performance']['total_file_size_mb']:.1f}MB")

        print("\n📊 Format-by-Format Performance:")
        for fmt, data in comprehensive_report['format_results'].items():
            print(f"  {fmt.upper()}: {data['dataset_count']} datasets, {data['total_extraction_time']:.3f}s total, {data['total_memory_used_mb']:.1f}MB memory")

        print("\n💡 Performance Insights:")
        for insight in comprehensive_report['overall_performance']['performance_insights']:
            print(f"  • {insight}")

        print("\n🔍 Detailed Analysis per Format:")
        for fmt, data in comprehensive_report['format_results'].items():
            analysis = data['performance_analysis']
            print(f"  {fmt.upper()}:")
            print(f"    Success Rate: {analysis['success_rate']:.1f}%")
            print(f"    Avg Extraction Time: {analysis['avg_extraction_time']:.3f}s")
            print(f"    Memory Efficiency: {analysis['memory_efficiency']:.1f}MB per 1000 fields")
            if analysis.get('bottlenecks'):
                print(f"    ⚠️  Bottlenecks: {', '.join(analysis['bottlenecks'])}")
            if analysis.get('recommendations'):
                print(f"    💡 Recommendations: {', '.join(analysis['recommendations'])}")

        # Save detailed reports
        benchmarker.save_benchmark_reports(results)

        print(f"\n✅ Benchmarking complete! Detailed reports saved to performance_reports/")

        # Performance assessment
        avg_time = comprehensive_report['overall_performance']['avg_time_per_dataset']
        success_rate = comprehensive_report['overall_performance']['overall_success_rate']

        if success_rate >= 99 and avg_time < 0.1:
            print("🎉 EXCEPTIONAL: Excellent performance across all scientific formats!")
            sys.exit(0)
        elif success_rate >= 95 and avg_time < 0.5:
            print("✅ EXCELLENT: Very good performance with room for optimization")
            sys.exit(0)
        elif success_rate >= 80:
            print("⚠️  GOOD: Acceptable performance, some optimizations recommended")
            sys.exit(1)
        else:
            print("❌ NEEDS IMPROVEMENT: Performance issues require attention")
            sys.exit(2)

    except Exception as e:
        logger.error(f"Benchmarking failed with error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()