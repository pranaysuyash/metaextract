#!/usr/bin/env python3
"""
Performance profiling script for metadata extraction engines.
This script analyzes the performance characteristics of different extraction methods
and identifies potential bottlenecks in the system.
"""

import os
import sys
import time
import cProfile
import pstats
import tempfile
from pathlib import Path
import psutil
import threading
from memory_profiler import profile

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../server'))

def create_test_image():
    """Create a minimal test image with some metadata."""
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

def profile_extraction_performance():
    """Profile the performance of the extraction engine."""
    
    print("Profiling Metadata Extraction Performance")
    print("=" * 50)
    
    # Create a test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(create_test_image())
        temp_file_path = temp_file.name

    try:
        # Import the extraction function
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        print("1. Basic Performance Timing...")
        
        # Measure execution time
        start_time = time.time()
        result = extract_comprehensive_metadata(temp_file_path, tier="pro")
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"   Execution time: {execution_time:.2f} seconds")
        
        # Count extracted fields
        metadata = result.get('metadata', {})
        field_count = sum(
            len(v) if isinstance(v, dict) else 1 
            for v in metadata.values()
        ) if metadata else 0
        print(f"   Fields extracted: {field_count}")
        
        print("\n2. Memory Usage Analysis...")
        
        # Get memory usage before and after extraction
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = extract_comprehensive_metadata(temp_file_path, tier="pro")
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        print(f"   Memory used during extraction: {memory_used:.2f} MB")
        
        print("\n3. CPU Profiling...")
        
        # Profile CPU usage
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Run extraction multiple times to get better profiling data
        for i in range(5):
            extract_comprehensive_metadata(temp_file_path, tier="pro")
        
        profiler.disable()
        
        # Save profiling results
        profiler.dump_stats('extraction_profile.prof')
        
        # Print top 10 functions by cumulative time
        stats = pstats.Stats('extraction_profile.prof')
        stats.sort_stats('cumulative')
        print("   Top 10 functions by cumulative time:")
        stats.print_stats(10)
        
        print("\n4. Tier Performance Comparison...")
        
        tiers = ["free", "starter", "pro", "super"]
        tier_times = {}
        
        for tier in tiers:
            start_time = time.time()
            result = extract_comprehensive_metadata(temp_file_path, tier=tier)
            end_time = time.time()
            
            tier_times[tier] = end_time - start_time
            field_count = sum(
                len(v) if isinstance(v, dict) else 1 
                for v in result.get('metadata', {}).values()
            ) if result.get('metadata') else 0
            
            print(f"   {tier}: {tier_times[tier]:.2f}s, {field_count} fields")
        
        print("\n5. Concurrency Testing...")
        
        # Test concurrent extractions
        def run_extraction():
            extract_comprehensive_metadata(temp_file_path, tier="pro")
        
        start_time = time.time()
        
        # Run 3 extractions in parallel
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_extraction)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        concurrent_time = end_time - start_time
        print(f"   3 concurrent extractions: {concurrent_time:.2f}s")
        print(f"   Sequential would take ~{sum(tier_times.values()) * 3 / 4:.2f}s (est.)")
        
        print("\n6. Performance Summary:")
        print(f"   - Single extraction: {execution_time:.2f}s")
        print(f"   - Memory usage: {memory_used:.2f}MB")
        print(f"   - Fields extracted: {field_count}")
        print(f"   - Best performing tier: {min(tier_times, key=tier_times.get)} ({min(tier_times.values()):.2f}s)")
        print(f"   - Worst performing tier: {max(tier_times, key=tier_times.get)} ({max(tier_times.values()):.2f}s)")
        
        return {
            'execution_time': execution_time,
            'memory_used': memory_used,
            'field_count': field_count,
            'tier_times': tier_times,
            'concurrent_time': concurrent_time
        }
        
    except Exception as e:
        print(f"❌ Performance profiling failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def analyze_extraction_bottlenecks():
    """Analyze potential bottlenecks in the extraction process."""
    
    print("\nAnalyzing Extraction Bottlenecks")
    print("=" * 35)
    
    # Create a test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(create_test_image())
        temp_file_path = temp_file.name

    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        print("1. Module Loading Analysis...")
        
        # Import time analysis
        import time
        start = time.time()
        from extractor import module_discovery
        module_discovery_time = time.time() - start
        print(f"   Module discovery import time: {module_discovery_time:.4f}s")
        
        print("\n2. Individual Module Performance...")
        
        # Test specific extraction modules if available
        extraction_modules = [
            'exifread', 'PIL', 'mutagen', 'pyexiv2', 
            'hachoir', 'mediaprocessing', 'imagehash'
        ]
        
        available_modules = []
        for module_name in extraction_modules:
            try:
                start = time.time()
                __import__(module_name)
                load_time = time.time() - start
                available_modules.append((module_name, load_time))
                print(f"   {module_name}: {load_time:.4f}s")
            except ImportError:
                print(f"   {module_name}: Not available")
        
        print("\n3. File Processing Stages...")
        
        # Profile different stages of extraction
        stages = {
            'file_read': lambda: open(temp_file_path, 'rb').read(1024),
            'mime_detection': lambda: __import__('magic').from_file(temp_file_path, mime=True) if 'magic' in [m.__name__ for m in sys.modules.values()] or __import__('magic') else 'image/jpeg',
            'format_identification': lambda: True,  # Placeholder
        }
        
        for stage_name, stage_func in stages.items():
            try:
                start = time.time()
                result = stage_func()
                stage_time = time.time() - start
                print(f"   {stage_name}: {stage_time:.4f}s")
            except Exception as e:
                print(f"   {stage_name}: Error - {str(e)}")
        
        print("\n4. Bottleneck Analysis:")
        print("   - Check if ExifTool is available (often a major bottleneck)")
        print("   - Verify image processing libraries are properly installed")
        print("   - Monitor for file I/O bottlenecks")
        print("   - Check for memory allocation issues")
        print("   - Analyze module loading overhead")
        
        return True
        
    except Exception as e:
        print(f"❌ Bottleneck analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def generate_performance_report():
    """Generate a comprehensive performance report."""
    
    print("\nGenerating Performance Report")
    print("=" * 30)
    
    perf_data = profile_extraction_performance()
    if perf_data:
        print("\nPerformance Report Generated Successfully!")
        print(f"Execution time: {perf_data['execution_time']:.2f}s")
        print(f"Memory usage: {perf_data['memory_used']:.2f}MB")
        print(f"Fields extracted: {perf_data['field_count']}")
        
        # Identify potential issues
        issues = []
        if perf_data['execution_time'] > 5.0:  # More than 5 seconds is slow
            issues.append("Slow extraction time (>5s)")
        if perf_data['memory_used'] > 100.0:  # More than 100MB is high
            issues.append("High memory usage (>100MB)")
        if perf_data['field_count'] == 0:
            issues.append("No fields extracted")
        
        if issues:
            print(f"\nPotential Performance Issues Identified:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\nNo major performance issues detected.")
    
    bottleneck_analysis = analyze_extraction_bottlenecks()
    
    print("\n" + "=" * 50)
    print("Performance profiling completed!")
    print("Profile data saved to 'extraction_profile.prof'")
    print("Use 'python -m pstats extraction_profile.prof' to analyze further")

if __name__ == "__main__":
    print("Running Performance Profiling for Metadata Extraction Engines\n")
    
    # Check if memory_profiler is available
    try:
        import memory_profiler
        print("Memory profiler is available")
    except ImportError:
        print("Memory profiler not available - install with: pip install memory-profiler")
    
    generate_performance_report()