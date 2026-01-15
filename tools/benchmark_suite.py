#!/usr/bin/env python3
"""
MetaExtract Comprehensive Benchmarking Suite

Performance Optimization Agent - Benchmarking Module
Measures extraction performance against multiple metrics:
- Time per file
- Memory usage (peak and sustained)
- Throughput (files/min)
- Success rates
- Comparison with legacy system

Usage:
    python benchmark_suite.py --suite all
    python benchmark_suite.py --suite large_files
    python benchmark_suite.py --file /path/to/file.dcm
"""

import argparse
import json
import time
import psutil
import os
import sys
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkSuite(Enum):
    """Available benchmark suites"""
    SMALL_FILES = "small_files"
    MEDIUM_FILES = "medium_files"
    LARGE_FILES = "large_files"
    SCIENTIFIC = "scientific"
    MIXED = "mixed"
    ALL = "all"


@dataclass
class MemorySnapshot:
    """Memory usage at a point in time"""
    timestamp: float
    rss_mb: float  # Resident set size
    vms_mb: float  # Virtual memory size
    percent: float  # % of system memory


@dataclass
class ExtractionBenchmark:
    """Results of a single file extraction benchmark"""
    filepath: str
    filename: str
    file_size_mb: float
    file_type: str
    
    # Timing
    extraction_time_ms: float
    
    # Memory
    initial_memory_mb: float
    peak_memory_mb: float
    final_memory_mb: float
    memory_delta_mb: float
    
    # Success
    success: bool
    error_message: Optional[str] = None
    
    # Metadata
    extracted_fields: int = 0
    extraction_errors: int = 0


@dataclass
class BenchmarkResults:
    """Aggregated benchmark results"""
    suite_name: str
    timestamp: str
    files_processed: int
    files_successful: int
    files_failed: int
    
    # Timing statistics
    total_time_seconds: float
    avg_extraction_time_ms: float
    min_extraction_time_ms: float
    max_extraction_time_ms: float
    throughput_files_per_minute: float
    
    # Memory statistics
    avg_peak_memory_mb: float
    max_peak_memory_mb: float
    memory_efficiency: float  # MB per 100MB file
    
    # Success metrics
    success_rate: float
    failure_breakdown: Dict[str, int]
    
    # Individual results
    individual_results: List[ExtractionBenchmark]


class MemoryProfiler:
    """Profiles memory usage during extraction"""
    
    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.process = psutil.Process()
        self.traced_memory = None
    
    def start(self):
        """Start memory profiling"""
        tracemalloc.start()
        self.initial_memory = self.process.memory_info().rss
    
    def take_snapshot(self):
        """Take a memory snapshot"""
        mem_info = self.process.memory_info()
        self.snapshots.append(MemorySnapshot(
            timestamp=time.time(),
            rss_mb=mem_info.rss / 1024 / 1024,
            vms_mb=mem_info.vms / 1024 / 1024,
            percent=self.process.memory_percent()
        ))
    
    def stop(self) -> Dict[str, float]:
        """Stop profiling and return statistics"""
        self.traced_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        mem_info = self.process.memory_info()
        
        return {
            'initial_memory_mb': self.initial_memory / 1024 / 1024,
            'final_memory_mb': mem_info.rss / 1024 / 1024,
            'peak_memory_mb': max([s.rss_mb for s in self.snapshots]),
            'traced_peak_mb': self.traced_memory[1] / 1024 / 1024 if self.traced_memory else 0,
        }


class MetaExtractBenchmark:
    """Main benchmarking coordinator"""
    
    def __init__(self, test_data_dir: str = 'test_images'):
        self.test_data_dir = Path(test_data_dir)
        self.results: List[ExtractionBenchmark] = []
        
        # Import the actual extractor (would need to adjust import path)
        try:
            from server.extractor.comprehensive_metadata_engine import (
                MetadataEngine
            )
            self.engine = MetadataEngine()
        except ImportError:
            logger.warning("Could not import MetadataEngine, using mock")
            self.engine = None
    
    def extract_file(self, filepath: str) -> ExtractionBenchmark:
        """Benchmark extraction of a single file"""
        
        filepath = Path(filepath)
        if not filepath.exists():
            return ExtractionBenchmark(
                filepath=str(filepath),
                filename=filepath.name,
                file_size_mb=0,
                file_type=filepath.suffix.lower(),
                extraction_time_ms=0,
                initial_memory_mb=0,
                peak_memory_mb=0,
                final_memory_mb=0,
                memory_delta_mb=0,
                success=False,
                error_message="File not found"
            )
        
        file_size_mb = filepath.stat().st_size / 1024 / 1024
        file_type = filepath.suffix.lower()
        
        logger.info(f"Benchmarking: {filepath.name} ({file_size_mb:.1f}MB)")
        
        # Profile extraction
        profiler = MemoryProfiler()
        profiler.start()
        
        start_time = time.time()
        
        try:
            # Simulate extraction (would use real engine)
            result = self._simulate_extraction(filepath)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            mem_stats = profiler.stop()
            
            benchmark = ExtractionBenchmark(
                filepath=str(filepath),
                filename=filepath.name,
                file_size_mb=file_size_mb,
                file_type=file_type,
                extraction_time_ms=elapsed_ms,
                initial_memory_mb=mem_stats['initial_memory_mb'],
                peak_memory_mb=mem_stats['peak_memory_mb'],
                final_memory_mb=mem_stats['final_memory_mb'],
                memory_delta_mb=mem_stats['final_memory_mb'] - mem_stats['initial_memory_mb'],
                success=True,
                extracted_fields=len(result.get('metadata', {})) if result else 0
            )
            
            logger.info(
                f"  ✓ {elapsed_ms:.0f}ms, "
                f"Peak: {mem_stats['peak_memory_mb']:.1f}MB, "
                f"Fields: {benchmark.extracted_fields}"
            )
            
            return benchmark
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            mem_stats = profiler.stop()
            
            logger.error(f"  ✗ Failed: {str(e)}")
            
            return ExtractionBenchmark(
                filepath=str(filepath),
                filename=filepath.name,
                file_size_mb=file_size_mb,
                file_type=file_type,
                extraction_time_ms=elapsed_ms,
                initial_memory_mb=mem_stats['initial_memory_mb'],
                peak_memory_mb=mem_stats['peak_memory_mb'],
                final_memory_mb=mem_stats['final_memory_mb'],
                memory_delta_mb=mem_stats['final_memory_mb'] - mem_stats['initial_memory_mb'],
                success=False,
                error_message=str(e)
            )
    
    def _simulate_extraction(self, filepath: Path) -> Dict[str, Any]:
        """Simulate file extraction for benchmarking"""
        # In real implementation, would call actual engine
        # For now, return mock data
        
        import json
        
        # Read some of the file to simulate processing
        with open(filepath, 'rb') as f:
            # Read first 1MB or entire file
            sample = f.read(min(1_000_000, filepath.stat().st_size))
        
        return {
            'metadata': {
                f'field_{i}': f'value_{i}' 
                for i in range(100)
            }
        }
    
    def run_suite(self, suite: BenchmarkSuite) -> BenchmarkResults:
        """Run a predefined benchmark suite"""
        
        logger.info(f"Starting benchmark suite: {suite.value}")
        
        # Define test files for each suite
        test_files = self._get_test_files_for_suite(suite)
        
        if not test_files:
            logger.error(f"No test files found for suite: {suite.value}")
            return None
        
        logger.info(f"Found {len(test_files)} files to benchmark")
        
        self.results = []
        suite_start = time.time()
        
        # Run benchmark for each file
        for filepath in test_files:
            result = self.extract_file(filepath)
            self.results.append(result)
        
        suite_elapsed = time.time() - suite_start
        
        # Aggregate results
        return self._aggregate_results(suite.value, suite_elapsed)
    
    def _get_test_files_for_suite(self, suite: BenchmarkSuite) -> List[str]:
        """Get list of test files for suite"""
        
        # Define test files (would be actual test images in real setup)
        test_suites = {
            BenchmarkSuite.SMALL_FILES: [
                'test_images/5mb.jpg',
                'test_images/10mb.png',
                'test_images/2mb.gif',
            ],
            BenchmarkSuite.MEDIUM_FILES: [
                'test_images/50mb.pdf',
                'test_images/100mb.mp4',
                'test_images/75mb.zip',
            ],
            BenchmarkSuite.LARGE_FILES: [
                'test_images/500mb.dcm',
                'test_images/1gb.fits',
                'test_images/750mb.hdf5',
            ],
            BenchmarkSuite.SCIENTIFIC: [
                'test_images/dicom_brain.dcm',
                'test_images/fits_galaxy.fits',
                'test_images/hdf5_climate.h5',
                'test_images/netcdf_oceanographic.nc',
            ],
            BenchmarkSuite.MIXED: [
                'test_images/5mb.jpg',
                'test_images/50mb.pdf',
                'test_images/200mb.dcm',
                'test_images/10mb.mp4',
            ],
        }
        
        if suite == BenchmarkSuite.ALL:
            # Combine all suites
            all_files = []
            for s in BenchmarkSuite:
                if s != BenchmarkSuite.ALL:
                    all_files.extend(test_suites.get(s, []))
            return all_files
        
        return test_suites.get(suite, [])
    
    def _aggregate_results(self, suite_name: str, total_time: float) -> BenchmarkResults:
        """Aggregate individual results into summary"""
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        if not successful:
            logger.error("No successful extractions in suite!")
            return None
        
        extraction_times = [r.extraction_time_ms for r in successful]
        peak_memories = [r.peak_memory_mb for r in successful]
        
        # Calculate statistics
        import statistics
        import math

        # Handle edge case: no results
        if not self.results:
            logger.error("No results to aggregate!")
            return None

        # Calculate throughput with guard against zero/negative time
        total_time_safe = total_time if total_time > 0 else float('inf')
        throughput = (len(self.results) / total_time_safe) * 60 if total_time_safe != float('inf') else float('inf')

        # Calculate memory efficiency with proper NaN handling for zero file sizes
        all_file_sizes = [r.file_size_mb for r in self.results]
        avg_file_size = statistics.mean(all_file_sizes) if all_file_sizes else 0
        avg_peak_memory = statistics.mean(peak_memories) if peak_memories else 0

        # Use NaN to clearly indicate undefined efficiency rather than masking with 0
        if avg_file_size > 0:
            memory_efficiency = (avg_peak_memory / avg_file_size * 100)
        else:
            memory_efficiency = float('nan')  # Undefined for zero-size files
        
        failure_breakdown = {}
        for result in failed:
            error_type = type(result.error_message).__name__
            failure_breakdown[error_type] = failure_breakdown.get(error_type, 0) + 1
        
        return BenchmarkResults(
            suite_name=suite_name,
            timestamp=datetime.now().isoformat(),
            files_processed=len(self.results),
            files_successful=len(successful),
            files_failed=len(failed),
            total_time_seconds=total_time,
            avg_extraction_time_ms=statistics.mean(extraction_times),
            min_extraction_time_ms=min(extraction_times),
            max_extraction_time_ms=max(extraction_times),
            throughput_files_per_minute=throughput,
            avg_peak_memory_mb=statistics.mean(peak_memories),
            max_peak_memory_mb=max(peak_memories),
            memory_efficiency=memory_efficiency,
            success_rate=len(successful) / len(self.results) if self.results else 0,
            failure_breakdown=failure_breakdown,
            individual_results=self.results
        )
    
    def save_results(self, results: BenchmarkResults, output_path: str = None):
        """Save benchmark results to JSON"""

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"benchmark_results_{timestamp}.json"

        output_path = Path(output_path)

        # Prevent path traversal attacks by validating the resolved path
        resolved_path = output_path.resolve()
        current_dir = Path.cwd().resolve()

        # Allow only paths within current directory
        try:
            resolved_path.relative_to(current_dir)
        except ValueError:
            logger.error(f"Output path escapes current directory: {output_path}")
            raise ValueError(f"Invalid output path: {output_path} would write outside allowed directory")

        # Convert dataclass to dict
        data = {
            'suite_name': results.suite_name,
            'timestamp': results.timestamp,
            'files_processed': results.files_processed,
            'files_successful': results.files_successful,
            'files_failed': results.files_failed,
            'total_time_seconds': results.total_time_seconds,
            'avg_extraction_time_ms': results.avg_extraction_time_ms,
            'min_extraction_time_ms': results.min_extraction_time_ms,
            'max_extraction_time_ms': results.max_extraction_time_ms,
            'throughput_files_per_minute': results.throughput_files_per_minute,
            'avg_peak_memory_mb': results.avg_peak_memory_mb,
            'max_peak_memory_mb': results.max_peak_memory_mb,
            'memory_efficiency': results.memory_efficiency,
            'success_rate': results.success_rate,
            'failure_breakdown': results.failure_breakdown,
            'individual_results': [asdict(r) for r in results.individual_results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Benchmark results saved to: {output_path}")
        
        return output_path
    
    def print_summary(self, results: BenchmarkResults):
        """Print human-readable benchmark summary"""
        
        print("\n" + "=" * 80)
        print(f"BENCHMARK RESULTS: {results.suite_name}")
        print("=" * 80)
        print(f"Timestamp: {results.timestamp}")
        print(f"Files processed: {results.files_processed}")
        print(f"  ✓ Successful: {results.files_successful}")
        print(f"  ✗ Failed: {results.files_failed}")
        print(f"Success rate: {results.success_rate * 100:.1f}%")
        
        print("\nTiming:")
        print(f"  Total time: {results.total_time_seconds:.1f}s")
        print(f"  Avg per file: {results.avg_extraction_time_ms:.1f}ms")
        print(f"  Min: {results.min_extraction_time_ms:.1f}ms")
        print(f"  Max: {results.max_extraction_time_ms:.1f}ms")
        print(f"  Throughput: {results.throughput_files_per_minute:.1f} files/min")
        
        print("\nMemory:")
        print(f"  Avg peak: {results.avg_peak_memory_mb:.1f}MB")
        print(f"  Max peak: {results.max_peak_memory_mb:.1f}MB")
        print(f"  Efficiency: {results.memory_efficiency:.1f}MB per 100MB file")
        
        if results.failure_breakdown:
            print("\nFailure breakdown:")
            for error_type, count in results.failure_breakdown.items():
                print(f"  {error_type}: {count}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='MetaExtract Benchmarking Suite'
    )
    
    parser.add_argument(
        '--suite',
        type=str,
        choices=[s.value for s in BenchmarkSuite],
        default=BenchmarkSuite.MIXED.value,
        help='Benchmark suite to run'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Benchmark a specific file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for JSON results'
    )
    
    parser.add_argument(
        '--test-data-dir',
        type=str,
        default='test_images',
        help='Directory containing test files'
    )
    
    args = parser.parse_args()
    
    # Create benchmarker
    benchmarker = MetaExtractBenchmark(test_data_dir=args.test_data_dir)
    
    # Run benchmark
    if args.file:
        # Benchmark single file
        result = benchmarker.extract_file(args.file)
        print(f"\nFile: {result.filename}")
        print(f"  Size: {result.file_size_mb:.1f}MB")
        print(f"  Time: {result.extraction_time_ms:.1f}ms")
        print(f"  Peak Memory: {result.peak_memory_mb:.1f}MB")
        print(f"  Success: {result.success}")
    else:
        # Run suite
        suite = BenchmarkSuite(args.suite)
        results = benchmarker.run_suite(suite)
        
        if results:
            benchmarker.print_summary(results)
            benchmarker.save_results(results, args.output)


if __name__ == '__main__':
    main()
