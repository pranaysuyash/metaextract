#!/usr/bin/env python3
"""
Simple Performance Test for MetaExtract Core Features
Tests the key performance improvements without complex dependencies.
"""

import os
import sys
import time
import tempfile
import json
import statistics
from pathlib import Path

# Add server path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def create_test_image():
    """Create a simple test image with basic structure."""
    # Create a minimal JPEG with basic EXIF data
    jpeg_header = bytes([
        0xFF, 0xD8,  # SOI (Start of Image)
        0xFF, 0xE1,  # APP1 marker
        0x00, 0x10,  # Length of APP1 segment
        0x45, 0x78, 0x69, 0x66, 0x00, 0x00,  # "Exif\0\0"
        0x49, 0x49,  # TIFF header (little endian)
        0x2A, 0x00,  # TIFF magic number
        0x08, 0x00, 0x00, 0x00,  # Offset to first IFD
        # IFD (Image File Directory) with basic EXIF tags
        0x01, 0x00,  # Number of directory entries
        0x10, 0x01, 0x03, 0x00,  # Tag: ImageWidth
        0x01, 0x00, 0x00, 0x00,  # Data type: SHORT
        0x01, 0x00, 0x00, 0x00,  # Number of components
        0x64, 0x00, 0x00, 0x00,  # Value offset or value
        0x00, 0x00,  # Next IFD offset (0 = no next IFD)
        0xFF, 0xD9   # EOI (End of Image)
    ])
    return jpeg_header

def test_basic_extraction():
    """Test basic metadata extraction performance."""
    print("🚀 Testing Basic Extraction Performance...")
    
    # Create test file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(create_test_image())
        temp_file_path = temp_file.name
    
    try:
        # Import the extraction function
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Measure execution time
        times = []
        for i in range(5):
            start_time = time.time()
            result = extract_comprehensive_metadata(temp_file_path, tier="pro")
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"   Average extraction time: {avg_time:.3f}s")
        print(f"   Min time: {min_time:.3f}s")
        print(f"   Max time: {max_time:.3f}s")
        
        # Check if we got metadata
        if result and 'extraction_info' in result:
            fields = result['extraction_info'].get('fields_extracted', 0)
            print(f"   Fields extracted: {fields}")
            return True, avg_time, fields
        else:
            print("   No metadata extracted")
            return False, avg_time, 0
            
    except Exception as e:
        print(f"   Error: {e}")
        return False, 0, 0
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_parallel_extraction():
    """Test parallel extraction performance."""
    print("\n⚡ Testing Parallel Extraction Performance...")
    
    # Create multiple test files
    test_files = []
    for i in range(5):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(create_test_image())
            test_files.append(temp_file.name)
    
    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Sequential processing
        print("   Sequential processing...")
        sequential_times = []
        for file_path in test_files:
            start_time = time.time()
            result = extract_comprehensive_metadata(file_path, tier="pro")
            end_time = time.time()
            sequential_times.append(end_time - start_time)
        
        sequential_avg = statistics.mean(sequential_times)
        print(f"   Sequential average: {sequential_avg:.3f}s per file")
        
        # Parallel processing
        print("   Parallel processing...")
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def extract_file(file_path):
            start_time = time.time()
            result = extract_comprehensive_metadata(file_path, tier="pro")
            end_time = time.time()
            return end_time - start_time
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            parallel_times = list(executor.map(extract_file, test_files))
        
        parallel_avg = statistics.mean(parallel_times)
        print(f"   Parallel average: {parallel_avg:.3f}s per file")
        
        # Calculate improvement
        improvement = ((sequential_avg - parallel_avg) / sequential_avg) * 100
        print(f"   Performance improvement: {improvement:.1f}%")
        
        return improvement > 20  # Target: 20%+ improvement
        
    except Exception as e:
        print(f"   Error: {e}")
        return False
    finally:
        # Cleanup
        for f in test_files:
            if os.path.exists(f):
                os.unlink(f)

def test_streaming_framework():
    """Test streaming framework functionality."""
    print("\n🌊 Testing Streaming Framework...")
    
    try:
        from extractor.streaming_framework import StreamingExtractor, StreamingConfig
        
        # Test configuration
        config = StreamingConfig()
        print(f"   Default chunk size: {config.chunk_size} bytes")
        print(f"   Strategy: {config.strategy}")
        
        # Test extractor creation
        extractor = StreamingExtractor(config)
        print("   Streaming extractor created successfully")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_parallel_framework():
    """Test parallel extraction framework."""
    print("\n⚙️ Testing Parallel Framework...")
    
    try:
        from extractor.parallel_extraction import ParallelExtractor, create_parallel_extractor
        
        # Test configuration
        from extractor.parallel_extraction import ParallelExtractionConfig
        config = ParallelExtractionConfig()
        print(f"   Max workers: {config.max_workers}")
        print(f"   Execution model: {config.execution_model}")
        
        # Test extractor creation
        def dummy_extract(file_path):
            return {'file': file_path, 'success': True}
        
        extractor = create_parallel_extractor(dummy_extract, max_workers=2)
        print("   Parallel extractor created successfully")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_memory_management():
    """Test memory management features."""
    print("\n🧠 Testing Memory Management...")
    
    try:
        from extractor.memory_management import MemoryMonitor, AdaptiveChunkSizer
        
        # Test memory monitor
        monitor = MemoryMonitor()
        snapshot = monitor.take_snapshot()
        print(f"   Memory snapshot taken: {len(snapshot)} processes")
        
        # Test chunk sizer
        sizer = AdaptiveChunkSizer()
        chunk_size = sizer.get_optimal_chunk_size(file_size=1024*1024)  # 1MB
        print(f"   Optimal chunk size for 1MB file: {chunk_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_error_handling():
    """Test error handling and fallbacks."""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Test with non-existent file
        result = extract_comprehensive_metadata("/nonexistent/file.jpg", tier="pro")
        
        if result and 'error' in result:
            print("   Error handling for non-existent file: ✅")
        else:
            print("   Error handling for non-existent file: ❌")
            return False
        
        # Test with invalid file
        with tempfile.NamedTemporaryFile(suffix='.invalid', delete=False) as temp_file:
            temp_file.write(b"invalid file content")
            temp_file_path = temp_file.name
        
        try:
            result = extract_comprehensive_metadata(temp_file_path, tier="pro")
            if result:  # Should handle gracefully
                print("   Error handling for invalid file: ✅")
                return True
            else:
                print("   Error handling for invalid file: ❌")
                return False
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def run_performance_benchmark():
    """Run comprehensive performance benchmark."""
    print("🚀 MetaExtract Performance Benchmark")
    print("=" * 50)
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'tests': {},
        'overall_score': 0
    }
    
    # Run tests
    tests = [
        ("Basic Extraction", test_basic_extraction),
        ("Parallel Processing", test_parallel_extraction),
        ("Streaming Framework", test_streaming_framework),
        ("Parallel Framework", test_parallel_framework),
        ("Memory Management", test_memory_management),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_func()
            results['tests'][test_name] = "PASSED" if success else "FAILED"
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            results['tests'][test_name] = f"ERROR: {e}"
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Calculate overall score
    results['overall_score'] = (passed / total) * 100
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"📊 PERFORMANCE BENCHMARK SUMMARY")
    print(f"{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    print(f"Overall score: {results['overall_score']:.1f}%")
    
    if results['overall_score'] >= 80:
        print("🎉 EXCELLENT: Performance improvements are working well!")
    elif results['overall_score'] >= 60:
        print("✅ GOOD: Most performance improvements are working.")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Several performance issues detected.")
    
    # Save results
    with open('performance_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: performance_benchmark_results.json")
    
    return results['overall_score'] >= 70  # Pass if 70%+ score

if __name__ == "__main__":
    success = run_performance_benchmark()
    
    if success:
        print("\n✅ Performance benchmark completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Performance benchmark failed!")
        sys.exit(1)