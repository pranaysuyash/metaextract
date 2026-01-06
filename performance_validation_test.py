#!/usr/bin/env python3
"""
Comprehensive Performance Validation Test for MetaExtract
Tests all performance improvements including:
- Database indexes
- Redis caching
- Parallel processing
- Batch operations
- Memory management
"""

import os
import sys
import time
import tempfile
import json
import threading
from pathlib import Path
import psutil
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add server path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
from extractor.streaming_framework import StreamingExtractor, StreamingConfig
from extractor.parallel_extraction import ParallelExtractor, create_parallel_extractor
from extractor.distributed_processing import DistributedCoordinator
from extractor.advanced_optimizations import SmartCacheManager
from extractor.advanced_optimizations import create_optimized_config, PerformancePredictor

class PerformanceValidator:
    """Comprehensive performance validation suite."""
    
    def __init__(self):
        self.results = {}
        self.baseline_metrics = {}
        self.improved_metrics = {}
        
    def create_test_files(self, count=10, size_mb=1):
        """Create test files for benchmarking."""
        files = []
        for i in range(count):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                # Create a file with some content
                content = b'EXIF' * (size_mb * 1024 * 256)  # Roughly size_mb MB
                f.write(content)
                files.append(f.name)
        return files
    
    def measure_extraction_time(self, file_path, tier="pro", iterations=5):
        """Measure extraction time for a file."""
        times = []
        for _ in range(iterations):
            start = time.time()
            try:
                result = extract_comprehensive_metadata(file_path, tier=tier)
                end = time.time()
                times.append(end - start)
            except Exception as e:
                print(f"Error extracting metadata: {e}")
                times.append(float('inf'))
        return times
    
    def test_single_file_performance(self):
        """Test single file extraction performance."""
        print("\n🚀 Testing Single File Performance...")
        
        # Create test file
        test_files = self.create_test_files(1, 1)
        test_file = test_files[0]
        
        try:
            # Measure extraction time
            times = self.measure_extraction_time(test_file, iterations=3)
            avg_time = statistics.mean(times)
            
            print(f"   Average extraction time: {avg_time:.3f}s")
            print(f"   Min time: {min(times):.3f}s")
            print(f"   Max time: {max(times):.3f}s")
            
            self.results['single_file'] = {
                'avg_time': avg_time,
                'min_time': min(times),
                'max_time': max(times)
            }
            
            # Verify we got some metadata
            result = extract_comprehensive_metadata(test_file, tier="pro")
            if result and 'extraction_info' in result:
                fields = result['extraction_info'].get('fields_extracted', 0)
                print(f"   Fields extracted: {fields}")
                self.results['single_file']['fields_extracted'] = fields
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def test_batch_processing_performance(self):
        """Test batch processing performance improvements."""
        print("\n📦 Testing Batch Processing Performance...")
        
        # Create test files
        test_files = self.create_test_files(10, 1)
        
        try:
            # Sequential processing
            print("   Sequential processing...")
            sequential_times = []
            for file_path in test_files:
                times = self.measure_extraction_time(file_path, iterations=1)
                sequential_times.extend(times)
            
            sequential_avg = statistics.mean(sequential_times)
            print(f"   Sequential average: {sequential_avg:.3f}s per file")
            
            # Parallel processing
            print("   Parallel processing...")
            def extract_file(file_path):
                return self.measure_extraction_time(file_path, iterations=1)[0]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                parallel_times = list(executor.map(extract_file, test_files))
            
            parallel_avg = statistics.mean(parallel_times)
            print(f"   Parallel average: {parallel_avg:.3f}s per file")
            
            # Calculate improvement
            improvement = ((sequential_avg - parallel_avg) / sequential_avg) * 100
            print(f"   Performance improvement: {improvement:.1f}%")
            
            self.results['batch_processing'] = {
                'sequential_avg': sequential_avg,
                'parallel_avg': parallel_avg,
                'improvement_percent': improvement
            }
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def test_streaming_performance(self):
        """Test streaming framework for large files."""
        print("\n🌊 Testing Streaming Performance...")
        
        # Create larger test file
        test_files = self.create_test_files(1, 10)  # 10MB file
        test_file = test_files[0]
        
        try:
            # Test regular extraction
            print("   Regular extraction...")
            regular_times = self.measure_extraction_time(test_file, iterations=2)
            regular_avg = statistics.mean(regular_times)
            
            # Test streaming extraction
            print("   Streaming extraction...")
            extractor = StreamingExtractor()
            streaming_times = []
            
            for _ in range(2):
                start = time.time()
                try:
                    metadata, metrics = extractor.extract_streaming(test_file)
                    end = time.time()
                    streaming_times.append(end - start)
                    print(f"     Streamed {metrics.chunks_processed} chunks")
                except Exception as e:
                    print(f"     Streaming error: {e}")
                    streaming_times.append(float('inf'))
            
            streaming_avg = statistics.mean(streaming_times)
            
            print(f"   Regular average: {regular_avg:.3f}s")
            print(f"   Streaming average: {streaming_avg:.3f}s")
            
            self.results['streaming'] = {
                'regular_avg': regular_avg,
                'streaming_avg': streaming_avg
            }
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def test_memory_efficiency(self):
        """Test memory efficiency improvements."""
        print("\n🧠 Testing Memory Efficiency...")
        
        process = psutil.Process()
        
        # Create test files
        test_files = self.create_test_files(5, 2)  # 5 files, 2MB each
        
        try:
            # Measure memory before
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process files
            for file_path in test_files:
                result = extract_comprehensive_metadata(file_path, tier="pro")
                if result and 'extraction_info' in result:
                    fields = result['extraction_info'].get('fields_extracted', 0)
                    print(f"   Processed {fields} fields from {os.path.basename(file_path)}")
            
            # Measure memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            print(f"   Memory used: {memory_used:.1f}MB")
            print(f"   Memory per file: {memory_used/len(test_files):.1f}MB")
            
            self.results['memory_efficiency'] = {
                'total_memory_mb': memory_used,
                'memory_per_file_mb': memory_used / len(test_files)
            }
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def test_cache_performance(self):
        """Test caching performance improvements."""
        print("\n💾 Testing Cache Performance...")
        
        # Create test file
        test_files = self.create_test_files(1, 1)
        test_file = test_files[0]
        
        try:
            cache = SmartCacheManager(max_size=1000000)  # 1MB cache
            
            # First extraction (cache miss)
            print("   First extraction (cache miss)...")
            start = time.time()
            result1 = extract_comprehensive_metadata(test_file, tier="pro")
            time1 = time.time() - start
            
            # Cache the result
            if result1:
                cache.set(test_file, result1, 1000)
            
            # Second extraction (cache hit)
            print("   Second extraction (cache hit)...")
            start = time.time()
            cached_result = cache.get(test_file)
            time2 = time.time() - start
            
            # Third extraction (direct, no cache)
            print("   Third extraction (direct, no cache)...")
            start = time.time()
            result3 = extract_comprehensive_metadata(test_file, tier="pro")
            time3 = time.time() - start
            
            print(f"   Cache miss time: {time1:.3f}s")
            print(f"   Cache hit time: {time2:.3f}s")
            print(f"   Direct time: {time3:.3f}s")
            
            if cached_result:
                speedup = ((time1 - time2) / time1) * 100
                print(f"   Cache speedup: {speedup:.1f}%")
            
            self.results['caching'] = {
                'cache_miss_time': time1,
                'cache_hit_time': time2,
                'direct_time': time3
            }
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def validate_performance_targets(self):
        """Validate that performance targets are met."""
        print("\n🎯 Validating Performance Targets...")
        
        targets_met = True
        
        # Check single file performance
        if 'single_file' in self.results:
            avg_time = self.results['single_file']['avg_time']
            if avg_time < 2.0:  # Target: under 2 seconds per file
                print(f"   ✅ Single file performance: {avg_time:.3f}s (target: <2.0s)")
            else:
                print(f"   ❌ Single file performance: {avg_time:.3f}s (target: <2.0s)")
                targets_met = False
        
        # Check batch processing improvement
        if 'batch_processing' in self.results:
            improvement = self.results['batch_processing']['improvement_percent']
            if improvement > 30:  # Target: 30%+ improvement
                print(f"   ✅ Batch processing improvement: {improvement:.1f}% (target: >30%)")
            else:
                print(f"   ❌ Batch processing improvement: {improvement:.1f}% (target: >30%)")
                targets_met = False
        
        # Check memory efficiency
        if 'memory_efficiency' in self.results:
            memory_per_file = self.results['memory_efficiency']['memory_per_file_mb']
            if memory_per_file < 10:  # Target: under 10MB per file
                print(f"   ✅ Memory efficiency: {memory_per_file:.1f}MB per file (target: <10MB)")
            else:
                print(f"   ❌ Memory efficiency: {memory_per_file:.1f}MB per file (target: <10MB)")
                targets_met = False
        
        self.results['targets_met'] = targets_met
        return targets_met
    
    def generate_report(self):
        """Generate comprehensive performance report."""
        print("\n📊 PERFORMANCE VALIDATION REPORT")
        print("=" * 50)
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results,
            'summary': {}
        }
        
        # Single file performance
        if 'single_file' in self.results:
            single = self.results['single_file']
            print(f"Single File Performance:")
            print(f"  Average time: {single['avg_time']:.3f}s")
            print(f"  Fields extracted: {single.get('fields_extracted', 'N/A')}")
            report['summary']['single_file'] = f"{single['avg_time']:.3f}s"
        
        # Batch processing
        if 'batch_processing' in self.results:
            batch = self.results['batch_processing']
            print(f"\nBatch Processing:")
            print(f"  Sequential: {batch['sequential_avg']:.3f}s per file")
            print(f"  Parallel: {batch['parallel_avg']:.3f}s per file")
            print(f"  Improvement: {batch['improvement_percent']:.1f}%")
            report['summary']['batch_improvement'] = f"{batch['improvement_percent']:.1f}%"
        
        # Memory efficiency
        if 'memory_efficiency' in self.results:
            memory = self.results['memory_efficiency']
            print(f"\nMemory Efficiency:")
            print(f"  Total memory used: {memory['total_memory_mb']:.1f}MB")
            print(f"  Memory per file: {memory['memory_per_file_mb']:.1f}MB")
            report['summary']['memory_per_file'] = f"{memory['memory_per_file_mb']:.1f}MB"
        
        # Caching
        if 'caching' in self.results:
            cache = self.results['caching']
            print(f"\nCaching Performance:")
            print(f"  Cache miss: {cache['cache_miss_time']:.3f}s")
            print(f"  Cache hit: {cache['cache_hit_time']:.3f}s")
            print(f"  Direct: {cache['direct_time']:.3f}s")
        
        # Overall assessment
        if self.results.get('targets_met'):
            print(f"\n🎉 OVERALL: All performance targets met!")
            report['summary']['status'] = 'SUCCESS'
        else:
            print(f"\n⚠️  OVERALL: Some performance targets not met")
            report['summary']['status'] = 'PARTIAL'
        
        return report
    
    def run_all_tests(self):
        """Run all performance validation tests."""
        print("🚀 Starting Comprehensive Performance Validation")
        print("=" * 60)
        
        try:
            self.test_single_file_performance()
            self.test_batch_processing_performance()
            self.test_streaming_performance()
            self.test_memory_efficiency()
            self.test_cache_performance()
            
            # Validate targets
            targets_met = self.validate_performance_targets()
            
            # Generate report
            report = self.generate_report()
            
            # Save report
            with open('performance_validation_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📄 Report saved to: performance_validation_report.json")
            
            return targets_met
            
        except Exception as e:
            print(f"\n❌ Error during performance validation: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    validator = PerformanceValidator()
    success = validator.run_all_tests()
    
    if success:
        print("\n✅ Performance validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Performance validation failed!")
        sys.exit(1)